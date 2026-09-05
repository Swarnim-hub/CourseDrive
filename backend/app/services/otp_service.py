import random
import string
import logging
from typing import Optional
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)

# Fallback in-memory dict if redis is unavailable in some local dev scenarios
_memory_otp_cache: dict[str, str] = {}


class OTPService:
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None

    async def get_redis(self) -> Optional[redis.Redis]:
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=2,
                )
            except Exception as e:
                logger.warning(f"Could not connect to Redis at {settings.REDIS_URL}: {e}")
                self._redis_client = None
        return self._redis_client

    def generate_otp(self, length: int = 6) -> str:
        """Generate a random numeric OTP code."""
        return "".join(random.choices(string.digits, k=length))

    async def store_otp(self, email: str, otp: str, expire_seconds: int = 600) -> bool:
        """Store OTP for an email address with expiration (default 10 mins)."""
        key = f"otp:{email.lower()}"
        client = await self.get_redis()
        if client:
            try:
                await client.setex(key, expire_seconds, otp)
                return True
            except Exception as e:
                logger.warning(f"Redis store_otp failed: {e}. Using fallback memory store.")
        
        _memory_otp_cache[key] = otp
        return True

    async def verify_otp(self, email: str, otp: str) -> bool:
        """Verify the provided OTP against the stored one and delete if valid."""
        key = f"otp:{email.lower()}"
        client = await self.get_redis()
        if client:
            try:
                stored = await client.get(key)
                if stored and stored == otp:
                    await client.delete(key)
                    return True
                return False
            except Exception as e:
                logger.warning(f"Redis verify_otp failed: {e}. Using fallback memory store.")
        
        stored = _memory_otp_cache.get(key)
        if stored and stored == otp:
            del _memory_otp_cache[key]
            return True
        return False


otp_service = OTPService()
