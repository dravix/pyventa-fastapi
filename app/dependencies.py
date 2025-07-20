import os
import asyncio
from postgrest import AsyncPostgrestClient, SyncPostgrestClient
from redis import Redis

url: str = os.environ.get("POSTGREST_URL", "")
db = SyncPostgrestClient(url)
db.auth(
    token=os.environ.get("POSTGREST_JWT_SECRET", ""),
    username=os.environ.get("POSTGRES_USER", ""),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

cache = Redis.from_url(
    os.environ.get("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True
)

# async def main():
#     async with AsyncPostgrestClient(url) as client:
#         r = await client.from_("countries").select("*").execute()
#         countries = r.data


# asyncio.run(main())
# import supabase

# url: str = os.environ.get("SUPABASE_URL")
# key: str = os.environ.get("SUPABASE_APIKEY")
# db: supabase.Client = supabase.create_client(url, key)
