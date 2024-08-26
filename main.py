from fastapi import FastAPI, status, Query, Path

from storage import storage
from schemas import NewProduct, SavedProduct, ProductPrice,  DeletedProduct

app = FastAPI(
    debug=True,
    title='Group_shop'
)


@app.get('/', include_in_schema=False)
def index():
    return {'subject': 'Hello'}


# CRUD
@app.post('/api/product/', description='create product', status_code=status.HTTP_201_CREATED, tags=['API', 'Product'])
def add_product(new_product: NewProduct) -> SavedProduct:
    saved_product = storage.create_product(new_product)
    return saved_product


# READ
@app.get('/api/product/', tags=['API', 'Product'])
def get_products(limit: int = Query(default=10, description='no more than products', gt=0), q: str = '') -> list[SavedProduct]:
    result = storage.get_products(limit=limit, q=q)
    return result


@app.get('/api/product/{product_id}', tags=['API', 'Product'])
def get_product(product_id: int = Path(ge=1, description='product id')) -> SavedProduct:
    result = storage.get_product(product_id)
    return result


# UPDATE
@app.patch('/api/product/{product_id}', tags=['API', 'Product'])
def update_product_price(new_price: ProductPrice, product_id: int = Path(ge=1, description='product id')) -> SavedProduct:
    result = storage.update_product_price(product_id, new_price.price)
    return result


@app.delete('/api/product/{product_id}', tags=['API', 'Product'])
def delete_product(product_id: int = Path(ge=1, description='product id')) -> DeletedProduct:
    result = storage.delete_product(product_id)
    return result
