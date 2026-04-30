import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass', email='test@example.com')

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client