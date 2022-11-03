from rest_framework import status
from store.models import Product, Category, Customer
from django.conf import settings
from model_bakery import baker
import pytest


@pytest.fixture
def create_product(api_client):
    def do_create_product(product):
        return api_client.post('/store/products/', product)
    return do_create_product


@pytest.fixture
def get_products(api_client):
    def do_get_products(id=None):
        if id:
            return api_client.get(f'/store/products/{id}/')
        return api_client.get(f'/store/products/')
    return do_get_products


@pytest.fixture
def update_product(api_client):
    def do_update_product(data):
        product = baker.make(Product)
        return api_client.patch(f'/store/products/{product.id}/', data)
    return do_update_product


@pytest.fixture
def delete_product(api_client):
    def do_delete_product(ordered=False):
        product = baker.make(Product)
        if ordered:
            user_data = {
                "username": "patdoe",
                "email": "patdoe@gmail.com",
                "first_name": "Pat",
                "last_name": "Doe",
                "password": "pat12345"
            }
            user = api_client.post('/auth/users/', user_data)
            customer = Customer.objects.get(
                user_id=user.data['id'])
            order = baker.make('Order', customer=customer)
            baker.make('OrderItem', product=product, order=order)
        return api_client.delete(f'/store/products/{product.id}/')
    return do_delete_product


@pytest.mark.django_db
class TestCreateProduct:

    def test_if_user_is_anonymous_returns_401(self, create_product):
        category = baker.make(Category)
        product = {
            "title": "a",
            "slug": "a",
            "unit_price": 1,
            "description": "a",
            "inventory": 1,
            "category": category.id
        }
        response = create_product(product)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, create_product):
        authenticate()
        category = baker.make(Category)
        product = {
            "title": "a",
            "slug": "a",
            "unit_price": 1,
            "description": "a",
            "inventory": 1,
            "category": category.id
        }

        response = create_product(product)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticate, create_product):
        authenticate(is_staff=True)
        category = baker.make(Category)
        product = {
            "title": "a",
            "slug": "a",
            "unit_price": 1,
            "description": "a",
            "inventory": -1,
            "category": category.id
        }

        response = create_product(product)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['inventory'] is not None

    def test_if_data_is_valid_returns_201(self, authenticate, create_product):
        authenticate(is_staff=True)
        category = baker.make(Category)
        product = {
            "title": "a",
            "slug": "a",
            "unit_price": 1,
            "description": "a",
            "inventory": 1,
            "category": category.id
        }

        response = create_product(product)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetrieveProduct:
    def test_get_all_products_returns_200(self, get_products):
        products = baker.make(Product, _quantity=10, _bulk_create=True)

        response = get_products()

        assert response.status_code == status.HTTP_200_OK
        assert len(products) == 10

    def test_if_product_exists_returns_200(self, get_products):
        product = baker.make(Product)

        response = get_products(id=product.id)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == product.id

    def test_if_product_does_not_exist_returns_400(self, get_products):
        product = baker.make(Product)

        response = get_products(id=product.id+1)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] is not None


@pytest.mark.django_db
class TestUpdateProduct:

    def test_if_user_is_anonymous_returns_401(self, update_product):

        response = update_product({"title": "a"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, update_product):
        authenticate()

        response = update_product({"title": "a"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticate, update_product):
        authenticate(is_staff=True)

        response = update_product({"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_200(self, authenticate, update_product):
        authenticate(is_staff=True)

        response = update_product({"title": "a"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestDeleteProduct:

    def test_if_user_is_anonymous_returns_401(self, delete_product):

        response = delete_product()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, delete_product):
        authenticate()

        response = delete_product()

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_product_has_been_ordered_returns_405(self, authenticate, delete_product):
        authenticate(is_staff=True)

        response = delete_product(ordered=True)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert response.data['error'] is not None

    def test_if_data_is_valid_returns_200(self, authenticate, delete_product):
        authenticate(is_staff=True)

        response = delete_product()

        assert response.status_code == status.HTTP_204_NO_CONTENT
