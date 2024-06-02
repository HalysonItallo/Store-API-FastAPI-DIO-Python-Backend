from motor.motor_asyncio import AsyncIOMotorClient

from store.core.config import settings


class MongoClient:
    def __init__(self) -> None:
        self._client = AsyncIOMotorClient(settings.DATABASE_URL)

    def get(self) -> AsyncIOMotorClient:
        return self._client


db_client = MongoClient()
