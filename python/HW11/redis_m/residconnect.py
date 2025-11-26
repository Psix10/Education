from redis.asyncio import Redis
import json
import functools
from fastapi import Request



redis_c = Redis(host='localhost', port=6379, db=0)

async def get_redis() -> Redis:
    global redis_c
    return redis_c

async def set_cache(key: str, value: dict, expire: int = 60):
    r = await get_redis()
    await r.set(key, json.dumps(value), ex=expire)

async def get_cache(key: str):
    r = await get_redis()
    data = await r.get(key)
    if data:
        return json.loads(data)
    return None

def cache_response(expire: int = 60):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request | None = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get("request")
            
            if request is None:
                raise ValueError("Request parameter is required for caching")
            
            key = f"cache:{request.url.path}?{request.url.query}"
            cached = await get_cache(key)
            if cached:
                print("Returning from cache")
                return cached
            
            result = await func(*args, **kwargs)
            if isinstance(result, list):
                serializable_result = [item.to_dict() for item in result]
            else:
                serializable_result = result.to_dict() if hasattr(result, "to_dict") else result
            await set_cache(key, serializable_result, expire=expire)
            print("Returning from DB")
            return result
        return wrapper
    return decorator