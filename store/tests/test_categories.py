from rest_framework import status
from store.models import Category, Product
from model_bakery import baker
import pytest


@pytest.fixture
def create_category(api_client):
    def do_create_category(category):
        return api_client.post('/store/categories/', category)
    return do_create_category


@pytest.fixture
def get_categories(api_client):
    def do_get_categories(id=None):
        if id:
            return api_client.get(f'/store/categories/{id}/')
        return api_client.get(f'/store/categories/')
    return do_get_categories


@pytest.fixture
def update_category(api_client):
    def do_update_category(data):
        category = baker.make(Category)
        return api_client.patch(f'/store/categories/{category.id}/', data)
    return do_update_category


@pytest.fixture
def delete_category(api_client):
    def do_delete_category(has_products=False):
        category = baker.make(Category)
        if has_products:
            baker.make(Product, category=category)
        return api_client.delete(f'/store/categories/{category.id}/')
    return do_delete_category


@pytest.mark.django_db
class TestCreateCategory:

    def test_if_user_is_anonymous_returns_401(self, create_category):
        response = create_category({"title": "a"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, create_category):
        authenticate()

        response = create_category({"title": "a"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticate, create_category):
        authenticate(is_staff=True)

        response = create_category({"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_201(self, authenticate, create_category):
        authenticate(is_staff=True)
        response = create_category({"title": "a"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetrieveCategory:
    def test_get_all_categories_returns_200(self, get_categories):
        baker.make(Category, _quantity=10)

        response = get_categories()

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10

    def test_if_category_exists_returns_200(self, get_categories):
        category = baker.make(Category)

        response = get_categories(id=category.id)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": category.id,
            "title": category.title,
            "product_count": 0
        }

    def test_if_category_does_not_exist_returns_400(self, get_categories):
        category = baker.make(Category)

        response = get_categories(id=category.id+1)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] is not None


@pytest.mark.django_db
class TestUpdateCategory:

    def test_if_user_is_anonymous_returns_401(self, update_category):

        response = update_category({"title": "a"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, update_category):
        authenticate()

        response = update_category({"title": "a"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticate, update_category):
        authenticate(is_staff=True)

        response = update_category({"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_200(self, authenticate, update_category):
        authenticate(is_staff=True)

        response = update_category({"title": "a"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestDeleteCategory:

    def test_if_user_is_anonymous_returns_401(self, delete_category):

        response = delete_category()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, delete_category):
        authenticate()

        response = delete_category()

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_category_has_products_returns_405(self, authenticate, delete_category):
        authenticate(is_staff=True)

        response = delete_category(has_products=True)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert response.data['error'] is not None

    def test_if_data_is_valid_returns_200(self, authenticate, delete_category):
        authenticate(is_staff=True)

        response = delete_category()

        assert response.status_code == status.HTTP_204_NO_CONTENT
