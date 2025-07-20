from pydantic import BaseModel
from typing import Optional
import json


class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class User(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    status: str


class Claims(BaseModel):
    user_id: int
    email: str
    role: str
    status: str
    exp: int

    def serialize(self):
        return self.dict()

    def to_string(self):
        return json.dumps(self.dict())

    def to_json(self):
        return json.dumps(self.dict())

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls(**data)


class Role(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
