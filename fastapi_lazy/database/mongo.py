from os import environ

from motor.motor_asyncio import AsyncIOMotorClient

link = f'mongodb://{environ["MONGO_USER"]}:{environ["MONGO_PASSWORD"]}@mongo:27017/'

# MongoDB
async def get_mongo() -> AsyncIOMotorClient:
    """
    Get MongoDB client

    Returns:
        AsyncIOMotorClient: MongoDB client

    Yields:
        Iterator[AsyncIOMotorClient]: MongoDB client
    """
    client = AsyncIOMotorClient(link)
    database = client.fastapi_lazy
    try:
        yield database
    finally:
        await database.close()
