from abc import ABC, abstractmethod
import sqlite3

from fastapi import HTTPException, status

from schemas import NewProduct, SavedProduct


class BaseStorageProduct(ABC):
    @abstractmethod
    def create_product(self, new_product: NewProduct):
        pass

    @abstractmethod
    def get_product(self, _id: int):
        pass

    @abstractmethod
    def get_products(self, limit: int):
        pass

    @abstractmethod
    def update_product_price(self, _id: int, new_price: float):
        pass

    @abstractmethod
    def delete_product(self, _id: int):
        pass


class StorageSQLite(BaseStorageProduct):

    def _create_table(self):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                CREATE TABLE IF NOT EXISTS {self.product_table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    description TEXT,
                    price REAL,
                    cover TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP 
                )
            """
            cursor.execute(query)

    def __init__(self, database_name: str):
        self.database_name = database_name
        self.product_table_name = 'products'
        self._create_table()

    def create_product(self, new_product: NewProduct) -> SavedProduct:
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            values = (new_product.title, new_product.description, new_product.price, str(new_product.cover))
            query = f"""
                INSERT INTO {self.product_table_name} (title, description, price, cover)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, values)

        return self._get_latest_product()

    def _get_latest_product(self) -> SavedProduct:
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                SELECT id, title, description, price, cover, created_at
                FROM {self.product_table_name}
                ORDER BY id DESC
                LIMIT 1

            """
            result = cursor.execute(query).fetchone()
            id, title, description, price, cover, created_at = result
            saved_product = SavedProduct(
                id=id, title=title, description=description, price=price, cover=cover, created_at=created_at
            )

            return saved_product

    def get_product(self, _id: int):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                SELECT id, title, description, price, cover, created_at
                FROM {self.product_table_name}
                WHERE id = {_id}
            """
            result: tuple = cursor.execute(query).fetchone()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Check your entity id, product with {_id} does not exist')
            id, title, description, price, cover, created_at = result
            saved_product = SavedProduct(
                id=id, title=title, description=description, price=price, cover=cover, created_at=created_at
            )
        return saved_product

    def get_products(self, limit: int = 10, q: str = '') -> list[SavedProduct]:
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                SELECT id, title, description, price, cover, created_at
                FROM {self.product_table_name}
                WHERE title LIKE '%{q}%' OR description LIKE '%{q}%'
                ORDER BY id DESC
                LIMIT {limit}
            """
            data: list[tuple] = cursor.execute(query).fetchall()

        list_of_products = []
        for result in data:
            id, title, description, price, cover, created_at = result
            saved_product = SavedProduct(
                id=id, title=title, description=description[:30], price=price, cover=cover, created_at=created_at
            )
            list_of_products.append(saved_product)
        return list_of_products

    def update_product_price(self, _id: int, new_price: float):
        self.get_product(_id)
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                UPDATE products
                SET
                    price = :Price
                WHERE id = :Id
            """
            cursor.execute(query, {'Price': new_price, 'Id': _id})
        saved_result = self.get_product(_id)
        return saved_result

    def delete_product(self, _id: int):
        self.get_product(_id)
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                               DELETE FROM {self.product_table_name}
                               WHERE id = :Id
                   """
            cursor.execute(query, {'Id': _id})

storage = StorageSQLite('db.sqlite')
