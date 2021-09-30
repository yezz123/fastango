from os import environ

from databases import Database

link = f"postgresql://{environ['DB_USER']}:{environ['DB_PASSWORD']}@{environ['DB_HOST']}:{environ['DB_PORT']}/{environ['DB_NAME']}"


# Postgresql
async def get_psql() -> Database:
    """
    Get Postgresql database connection

    Returns:
        Database: Postgresql database connection

    Yields:
        Iterator[Database]: Postgresql database connection
    """
    db = Database(link)
    await db.connect()
    try:
        yield db
    finally:
        await db.disconnect()
