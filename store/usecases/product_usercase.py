from datetime import datetime, timezone
from uuid import UUID

import pymongo
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import ValidationError

from store.core.exceptions import BadRequestException, NotFoundException
from store.db.mongo import db_client
from store.models.product_model import ProductModel
from store.schemas.product_schema import ProductFilterIn, ProductIn, ProductOut, ProductUpdate, ProductUpdateOut


class ProductUsecase:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient = db_client.get()
        self.database: AsyncIOMotorDatabase = self.client.get_database()
        self.collection = self.database.get_collection("products")

    async def create(self, body: ProductIn) -> ProductOut:
        try:
            product_model = ProductModel(**body.model_dump())
            await self.collection.insert_one(product_model.model_dump())
            return ProductOut(**product_model.model_dump())
        except ValidationError as err:
            raise BadRequestException(f"errors: {err.errors()}")

    async def get(self, id: UUID) -> ProductOut:
        result = await self.collection.find_one({"id": id})

        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        return ProductOut(**result)

    async def query(self) -> list[ProductOut]:
        return [ProductOut(**item) async for item in self.collection.find()]

    async def get_by_price(self, query_params: ProductFilterIn) -> list[ProductOut]:
        return [
            ProductOut(**item)
            async for item in self.collection.find(
                {
                    "price": {"$gt": query_params.min_price, "$lt": query_params.max_price},
                }
            )
        ]

    async def update(self, id: UUID, body: ProductUpdate) -> ProductUpdateOut:

        if not body.updated_at:
            body.updated_at = datetime.now(timezone.utc)

        result = await self.collection.find_one_and_update(
            filter={"id": id},
            update={"$set": body.model_dump(exclude_none=True)},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        return ProductUpdateOut(**result)

    async def delete(self, id: UUID) -> bool:
        product = await self.collection.find_one({"id": id})
        if not product:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        result = await self.collection.delete_one({"id": id})

        return True if result.deleted_count > 0 else False


usecase = ProductUsecase()
