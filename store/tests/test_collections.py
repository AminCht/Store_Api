import pytest
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User
from model_bakery import baker

from store.models import Collection, Product


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_anonymous_return_401(self):
        client = APIClient()
        response = client.post('/store/collections/', {'title': 'a'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_not_admin_return_403(self,authenticate):
        client = APIClient()
        authenticate(is_staff=False)
        response = client.post('/store/collections/', {'title': 'a'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_invalid_data_return_400(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        response = client.post('/store/collections/', {'title': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exist_return_200(self):
        client = APIClient()
        collection = baker.make(Collection)
        response = client.get(f'/store/collections/{collection.id}/')
        assert response.status_code == status.HTTP_200_OK