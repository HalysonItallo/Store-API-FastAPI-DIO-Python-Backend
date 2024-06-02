from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from store.core.exceptions import BadRequestException, NotFoundException
from store.schemas.product_schema import ProductFilterIn, ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.usecases.product_usercase import usecase


async def test_usecases_create_should_return_success(product_in: ProductIn):
    result: ProductOut = await usecase.create(body=product_in)

    assert isinstance(result, ProductOut)
    assert result.name == "Iphone 14 Pro Max"


async def test_usecases_create_should_return_bad_request(product_in: ProductIn):
    product_in.price = "incorrect value"
    with pytest.raises(BadRequestException) as err:
        await usecase.create(body=product_in)

    assert (
        err.value.message
        == "errors: [{'type': 'decimal_parsing', 'loc': ('price',), 'msg': 'Input should be a valid decimal', 'input': 'incorrect value', 'url': 'https://errors.pydantic.dev/2.7/v/decimal_parsing'}]"
    )


async def test_usecases_get_should_return_success(product_inserted: ProductOut):
    result: ProductOut = await usecase.get(id=product_inserted.id)

    assert isinstance(result, ProductOut)
    assert result.name == "Iphone 14 Pro Max"


async def test_usecases_get_should_not_found():
    with pytest.raises(NotFoundException) as err:
        await usecase.get(id=UUID("1e4f214e-85f7-461a-89d0-a751a32e3bb9"))

    assert err.value.message == "Product not found with filter: 1e4f214e-85f7-461a-89d0-a751a32e3bb9"


@pytest.mark.usefixtures("products_inserted")
async def test_usecases_query_should_return_success():
    result: list[ProductOut] = await usecase.query()

    assert isinstance(result, list)
    assert len(result) > 1


@pytest.mark.usefixtures("products_inserted")
async def test_usecases_get_by_price_should_return_success():

    product_filter_in = ProductFilterIn(min_price="4.500", max_price="7.000")
    result: list[ProductOut] = await usecase.get_by_price(query_params=product_filter_in)

    assert isinstance(result, list)
    assert len(result) == 2


async def test_usecases_update_should_return_success(product_inserted: ProductOut, product_up: ProductUpdate):
    product_up.price = "7500.00"
    result: list[ProductOut] = await usecase.update(id=product_inserted.id, body=product_up)

    assert isinstance(result, ProductUpdateOut)


async def test_usecases_update_should_return_not_found(product_up: ProductUpdate):
    product_up.price = "7500.00"
    with pytest.raises(NotFoundException) as err:
        await usecase.update(id=UUID("1e4f214e-85f7-461a-89d0-a751a32e3bb9"), body=product_up)

    assert err.value.message == "Product not found with filter: 1e4f214e-85f7-461a-89d0-a751a32e3bb9"


async def test_usecases_update_should_return_success_with_pass_updated_at_field(
    product_inserted: ProductOut, product_up: ProductUpdate
):
    mask = "%Y-%m-%dT%H:%M:%SZ"
    time_utc_now = datetime.now(timezone.utc) + timedelta(days=4)

    product_up.updated_at = time_utc_now

    result = await usecase.update(id=product_inserted.id, body=product_up)

    assert datetime.strftime(result.updated_at, mask) == datetime.strftime(time_utc_now, mask)


async def test_usecases_update_should_return_success_with_updated_at_field_updated_datetime(
    product_inserted: ProductOut, product_up: ProductUpdate
):
    result = await usecase.update(id=product_inserted.id, body=product_up)

    assert product_inserted.updated_at != result.updated_at


async def test_usecases_delete_should_return_success(product_inserted: ProductOut):
    result = await usecase.delete(id=product_inserted.id)

    assert result is True


async def test_usecases_delete_should_not_found():
    with pytest.raises(NotFoundException) as err:
        await usecase.delete(id=UUID("1e4f214e-85f7-461a-89d0-a751a32e3bb9"))

    assert err.value.message == "Product not found with filter: 1e4f214e-85f7-461a-89d0-a751a32e3bb9"
