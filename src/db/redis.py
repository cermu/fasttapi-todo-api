import redis.asyncio as aioredis
from src.config import settings

TOKEN_ID_EXPIRY = 1200

token_blocklist = aioredis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    password=settings.REDIS_PASS
)

async def add_token_id_to_blocklist(token_id: str) -> dict:
    try:
        await token_blocklist.set(name=token_id, value="_", ex=TOKEN_ID_EXPIRY)
        return {"message": "token id saved in redis successfully."}
    except Exception as e:
        return {"error": str(e)}

async def is_token_id_in_blocklist(token_id: str) -> dict:
    try:
        results = await token_blocklist.get(token_id)
        return {"results": results is not None}
    except Exception as e:
        return {"error": str(e)}
