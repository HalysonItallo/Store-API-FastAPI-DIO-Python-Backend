from store.models.base_model import CreateBaseModel
from store.schemas.product_schema import ProductIn


class ProductModel(ProductIn, CreateBaseModel):
    pass
