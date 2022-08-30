from locust import HttpUser, between, task
from random import randint


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def view_products(self):
        collection_id = randint(0, 1000)
        self.client.get(f'/store/products/', name='/store/products/')

    @task(5)
    def view_product_detail(self):
        product_id = randint(1, 10)
        self.client.get(f'/store/products/{product_id}/', name='/store/products/:id/')

    @task(1)
    def add_to_cart(self):
        product_id = randint(0, 1000)
        self.client.post(f'/store/carts/{self.cart_id}/items/', name='/store/cart/items/',
                         json={'product_id': product_id,
                               'quantity': 1})

    def on_start(self):
        response = self.client.post('/store/carts/')
        result = response.json()
        self.cart_id = result['id']
