import time
import bcrypt
import secrets
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from app.dependencies import (
    db,
    cache,
)  # Assuming you have a dependencies.py that provides the supabase client
from app.identity.schema import Claims, User, UserCreate, UserLogin, Role
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from app.notifications.email import send_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

SESSION_EXPIRE = 3600  # 1 hour


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    session = cache.get(f"::session:{token}")
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid session")
    return Claims.from_json(session.__str__())


@router.get("/account")
def read_account(current_user: Annotated[Claims, Depends(get_current_user)]):
    user = (
        db.from_("users").select("*").eq("id", current_user.user_id).single().execute()
    )
    if user.data is None:
        raise HTTPException(status_code=404, detail="No users found")
    return {"user": User(**user.data)}


@router.post("/login")
async def read_users(user: UserLogin):
    users = (
        db.table("users")
        .select("id, email, password_hash, status")
        .filter("email", "eq", user.email)
        .single()
        .execute()
    )
    if users.data is None:
        raise HTTPException(status_code=404, detail="No users found")
    if bcrypt.checkpw(
        bytes(user.password, "utf-8"), bytes(users.data["password_hash"], "utf-8")
    ):
        if users.data["status"] != "ACTIVE":
            raise HTTPException(status_code=403, detail="User not active")
        claims = Claims(
            user_id=users.data["id"],
            email=users.data["email"],
            status=users.data["status"],
            role="authenticated",
            exp=int(time.time()) + SESSION_EXPIRE,
        )
        users.data["password_hash"] = "********"
        token = secrets.token_hex(32)
        cache.set(
            f"::session:{users.data['id']}:{token}", claims.to_json(), ex=SESSION_EXPIRE
        )
        return {"user": users.data, "token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/refresh")
async def refresh_token(token: Annotated[str, Depends(oauth2_scheme)]):
    session = cache.get(f"::session:1:{token}")
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid session")
    claims = Claims.from_json(session.__str__())
    claims.exp = int(time.time()) + SESSION_EXPIRE
    cache.set(f"::session:1:{token}", claims.to_json(), ex=SESSION_EXPIRE)
    return {"status": "ok", "token": token, "claims": claims}


@router.get("/logout")
def logout(token: Annotated[str, Depends(oauth2_scheme)]):
    cache.delete(f"::session:1:{token}")
    return {"status": "ok", "token": token}


@router.get("/roles")
def read_roles():
    roles = db.table("roles").select("*").execute()
    return {"roles": roles.data}


@router.get("/send-verification-email/{email:str}")
async def verify_email(email: str):
    users = (
        db.table("users")
        .select("id, email, first_name, last_name, status")
        .filter("email", "eq", email)
        .single()
        .execute()
    )
    claims = Claims(
        user_id=users.data["id"],
        email=users.data["email"],
        role="verified_email",
        status=users.data["status"],
        exp=int(time.time()) + 3600,
    )
    if users.data is None:
        raise HTTPException(status_code=404, detail="No users found")
    token = secrets.token_hex(6)
    cache.set(f"::verify-email:{token}", claims.to_json(), ex=3600)
    await send_email(
        to=users.data["email"],
        subject="Please verify your email",
        template="verify-email",
        context={
            "subject": "Welcome to Pyventa!",
            "first_name": users.data["first_name"],
            "last_name": users.data["last_name"],
            "verification_url": "http://localhost:8000/identity/verify-email/" + token,
        },
    )
    return {"email_status": "sent", "email": users.data["email"]}


@router.get("/verify-email/{token}")
def confirm_email(token: str):
    session = cache.get(f"::verify-email:{token}")
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    claims = Claims.from_json(session.__str__())
    cache.delete(f"::verify-email:{token}")

    user = (
        db.table("users")
        .update({"status": "VERIFIED"})
        .eq("id", claims.user_id)
        .execute()
    )
    return RedirectResponse("http://localhost:5173/signin")
    return {"status": "ok", "claims": claims}


@router.post("/signup")
async def create_user(user: UserCreate):
    user_dict = user.model_dump()
    user_dict["password_hash"] = str(
        bcrypt.hashpw(bytes(user_dict["password"], "utf-8"), bcrypt.gensalt())
    )
    if db.table("users").select("id").eq("email", user_dict["email"]).execute().count:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_dict["status"] = "INACTIVE"

    user_dict["password_hash"] = user_dict["password_hash"]
    db.table("users").insert(user_dict).execute()
    await verify_email(user_dict["email"])
    return {"status": "ok", "user": user_dict}


@router.get("/me")
def read_me(current_user: Annotated[Claims, Depends(get_current_user)]):
    return {"user": current_user}


@router.get("/roles/{role_id}")
def read_role(role_id: int):
    try:
        role = (
            db.from_("roles")
            .select("*, permissions(id, action, name)")
            .eq("id", role_id)
            .single()
            .execute()
        )
        if role.data is None:
            raise HTTPException(status_code=404, detail="No roles found")
        return {"role_id": role_id, "role": role.data}
    except Exception as e:
        raise HTTPException(status_code=404, detail="No roles found")


@router.get("/permissions")
def read_permissions():
    try:
        permissions = db.from_("permissions").select("*").execute()
        return {"permissions": permissions.data}
    except Exception as e:
        raise HTTPException(status_code=404, detail="No permissions found")
