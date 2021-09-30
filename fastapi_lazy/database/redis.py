import logging
import pickle

log = logging.getLogger(__name__)

# Get from redis
async def get_from_redis(redis, key: str):
    """
    Get data from redis

    Args:
        redis (redis.Redis): Redis client
        key (str): Key of data

    Returns:
        dict: Data
    """
    try:
        value = await redis.get(key)
        if value:
            return pickle.loads(value)
    except Exception as exp:
        log.error("Error relate to Redis ", exp)


# Set to redis
async def set_to_redis(redis, name: str, value: dict, idd: int):
    """
    Set data to redis

    Args:
        redis (redis.Redis): Redis client
        name (str): Name of data
        value (dict): Data
        idd (int): Id of data

    Returns:
        bool: True if success, False if fail
    """
    try:
        await redis.set(name, pickle.dumps(value), idd=idd)
    except Exception as exp:
        log.error("Error setting redis: ", exp)
