from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from pydantic import UUID4

from store.core.exceptions import BadRequestException, NotFoundException
from store.schemas.product_schema import ProductFilterIn, ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.usecases.product_usercase import ProductUsecase

router = APIRouter(tags=["products"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(body: ProductIn = Body(...), usecase: ProductUsecase = Depends()) -> ProductOut:
    try:
        return await usecase.create(body=body)
    except BadRequestException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.get(path="/{id}", status_code=status.HTTP_200_OK)
async def get(id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()) -> ProductOut:
    try:
        return await usecase.get(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get(path="/", status_code=status.HTTP_200_OK)
async def query(usecase: ProductUsecase = Depends()) -> list[ProductOut]:
    return await usecase.query()


@router.get(path="/filter-price/", status_code=status.HTTP_200_OK)
async def get_by_price(
    min_price: Decimal = Query(Decimal("4.500"), alias="min_price"),
    max_price: Decimal = Query(Decimal("8.000"), alias="max_price"),
    usecase: ProductUsecase = Depends(),
):

    filters = ProductFilterIn(min_price=min_price, max_price=max_price)
    return await usecase.get_by_price(filters)


@router.patch(path="/{id}", status_code=status.HTTP_200_OK)
async def patch(
    id: UUID4 = Path(alias="id"),
    body: ProductUpdate = Body(...),
    usecase: ProductUsecase = Depends(),
) -> ProductUpdateOut:
    try:
        return await usecase.update(id=id, body=body)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()) -> None:
    try:
        await usecase.delete(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
