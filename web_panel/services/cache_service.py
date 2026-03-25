"""
Redis Cache Service for QR Access PRO
Manages caching of validation data and frequently accessed information.
"""
import redis
import json
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

try:
    # Try to connect to Redis
    cache = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True,
        socket_connect_timeout=5
    )
    cache.ping()
    logger.info("Redis cache connected successfully")
except Exception as e:
    logger.warning(f"Redis not available: {e}. Operating in no-cache mode")
    cache = None


def is_redis_available():
    """Check if Redis is available."""
    return cache is not None


def get_cache(key):
    """Get value from cache."""
    if not cache:
        return None
    try:
        value = cache.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None


def set_cache(key, value, expire_seconds=300):
    """Set value in cache with expiration."""
    if not cache:
        return False
    try:
        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value)
        cache.setex(key, expire_seconds, value)
        return True
    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False


def delete_cache(key):
    """Delete value from cache."""
    if not cache:
        return False
    try:
        cache.delete(key)
        return True
    except Exception as e:
        logger.error(f"Cache delete error: {e}")
        return False


def cache_user_qr_validation(user_id, qr_code, result, expire_seconds=300):
    """Cache QR validation result."""
    key = f"qr_validation:{user_id}:{qr_code}"
    return set_cache(key, {"valid": result, "timestamp": str(datetime.now())}, expire_seconds)


def get_cached_qr_validation(user_id, qr_code):
    """Get cached QR validation."""
    key = f"qr_validation:{user_id}:{qr_code}"
    return get_cache(key)


def invalidate_user_cache(user_id):
    """Invalidate all cache entries for a user."""
    if not cache:
        return False
    try:
        pattern = f"qr_validation:{user_id}:*"
        for key in cache.scan_iter(match=pattern):
            cache.delete(key)
        logger.info(f"Invalidated cache for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")
        return False


def cache_user_data(user_id, user_data, expire_seconds=600):
    """Cache user data."""
    key = f"user_data:{user_id}"
    return set_cache(key, user_data, expire_seconds)


def get_cached_user_data(user_id):
    """Get cached user data."""
    key = f"user_data:{user_id}"
    return get_cache(key)


def cache_stats(key_name, stats_data, expire_seconds=300):
    """Cache statistics data."""
    key = f"stats:{key_name}"
    return set_cache(key, stats_data, expire_seconds)


def get_cached_stats(key_name):
    """Get cached statistics."""
    key = f"stats:{key_name}"
    return get_cache(key)


def clear_all_cache():
    """Clear all Redis cache (use with caution)."""
    if not cache:
        return False
    try:
        cache.flushdb()
        logger.warning("All Redis cache cleared")
        return True
    except Exception as e:
        logger.error(f"Cache flush error: {e}")
        return False


from datetime import datetime
