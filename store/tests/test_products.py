
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from model_bakery import baker

from store.models import Collection, Product




@pytest.mark.django_db
class TestCreateProducts:
    def test_if_user_is_anonymous_return_401(self):
        client = APIClient()
        product = baker.make(Product)
        response = client.post('/store/products/', product=product)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_product_exist_return_200(self):
        client = APIClient()
        collection = baker.make(Collection)
        response = client.get(f'/store/collections/{collection.id}/')
        assert response.status_code == status.HTTP_200_OK

    def test_upload_image_by_anonymous_return_401(self):
        client = APIClient()
        product = baker.make(Product)
        response = client.post(f'/store/products/{product.id}/images/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_uploaded_image_invalid_return_400(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        product = baker.make(Product)
        response = client.post(f'/store/products/{product.id}/images/', {'images': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestRetrieveProduct:
    def test_if_product_deos_not_exist_return(self):
        client = APIClient()
        response = client.get('/store/products/0/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_product_exist_return_200(self):
        client = APIClient()
        product = baker.make(Product)
        response = client.get(f'/store/products/{product.id}/')
        assert response.status_code == status.HTTP_200_OK
