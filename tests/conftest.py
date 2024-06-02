import asyncio
from uuid import UUID

import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from store.db.mongo import db_client
from store.schemas.product_schema import ProductIn, ProductUpdate
from store.usecases.product_usercase import usecase
from tests.factories import product_data, products_data


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mongo_cliente() -> AsyncIOMotorClient:
    return db_client.get()


@pytest.fixture(autouse=True)
async def clear_collections(mongo_cliente: AsyncIOMotorClient):
    yield
    collections_names = await mongo_cliente.get_database().list_collection_names()
    for collection_name in collections_names:
        if collection_name.startswith("system"):
            continue

        await mongo_cliente.get_database()[collection_name].delete_many({})


@pytest.fixture
async def client() -> AsyncClient:
    from store.main import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def products_url() -> str:
    return "/products/"


@pytest.fixture
def product_id() -> UUID:
    return UUID("fce6cc37-10b9-4a8e-a8b2-977df327001a")


@pytest.fixture
def product_in(product_id):
    return ProductIn(**product_data(), id=product_id)


@pytest.fixture
def product_up(product_id):
    return ProductUpdate(**product_data(), id=product_id)


@pytest.fixture
async def product_inserted(product_in):
    return await usecase.create(body=product_in)


@pytest.fixture
def products_in():
    return [ProductIn(**product) for product in products_data()]


@pytest.fixture
async def products_inserted(products_in):
    return [await usecase.create(body=product_in) for product_in in products_in]
