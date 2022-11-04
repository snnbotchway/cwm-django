from locust import HttpUser, task, between
from random import randint


class User(HttpUser):
    wait_time = between(1, 10)

    def on_start(self):
        # login and store access token
        # self.token = self.login()
        # self.headers = {'Authorization': 'JWT ' + self.token}

        # create a cart and store id
        response = self.client.post('/store/carts/').json()
        self.cart_id = response['id']

    @task(3)
    def get_products(self):
        category_id = randint(1, 10)
        self.client.get(
            f"/store/products/?category_id={category_id}", name='/store/products/')

    @task(6)
    def get_product(self):
        product_id = randint(1, 1000)
        self.client.get(
            f"/store/products/{product_id}/", name='/store/products/:id')

    @task(1)
    def add_to_cart(self):
        self.client.post(f"/store/carts/{self.cart_id}/cartitems/",
                         data={
                             "product_id": randint(1, 5),
                             "quantity": randint(1, 5)
                         },
                         name='/store/carts/:id/cartitems/')
