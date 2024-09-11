from fastapi import FastAPI, status, Query, Path, Request, Form
from fastapi.templating import Jinja2Templates

from storage import storage
from schemas import NewProduct, SavedProduct, ProductPrice, DeletedProduct

app = FastAPI(
    debug=True,
    title='Group_shop'
)

templates = Jinja2Templates(directory='templates')


@app.get('/', include_in_schema=False)
@app.post('/', include_in_schema=False)
def index(request: Request, q: str = Form(default='')):
    products = storage.get_products(limit=40, q=q)
    context = {
        'request': request,
        'page_title': 'the best shop',
        'products': products
    }
    return templates.TemplateResponse('index.html', context=context)


@app.get('/{product_id}', include_in_schema=False)
def product_detail(request: Request, product_id: int):
    product = storage.get_product(product_id)
    context = {
        'request': request,
        'page_title': f'{product.title}',
        'product': product
    }
    return templates.TemplateResponse('details.html', context=context)


@app.get('/navigation/', include_in_schema=False)
def navigation(request: Request):
    context = {
        'request': request,
        'page_title': 'How to get to us',
    }
    return templates.TemplateResponse('navigation.html', context=context)


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
def update_product_price(new_price: ProductPrice,
                         product_id: int = Path(ge=1, description='product id')) -> SavedProduct:
    result = storage.update_product_price(product_id, new_price.price)
    return result


@app.delete('/api/product/{product_id}', tags=['API', 'Product'])
def update_product_price(product_id: int = Path(ge=1, description='product id')) -> DeletedProduct:
    storage.delete_product(product_id)
    return DeletedProduct(id=product_id)
