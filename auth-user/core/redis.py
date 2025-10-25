from redis import asyncio as aioredis

from core.config import settings

redis = aioredis.from_url(
    url=settings.redis.url,
    decode_responses=True,
)
