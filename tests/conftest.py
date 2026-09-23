import os

import pytest
from rest_framework.test import APIClient


ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', 'A2v8O5GpCLMIymsnbleTU5Nm2i78uvEwwNVBZ0eVtCI')


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_headers():
    return {'HTTP_X_ADMIN_KEY': ADMIN_API_KEY}


@pytest.fixture
@pytest.mark.django_db
def api_key(api_client, admin_headers):
    """Creates an API key via the admin-gated endpoint and returns (raw_key, key_id)."""
    resp = api_client.post('/api/v1/api-keys/', {'name': 'Test Client'}, format='json', **admin_headers)
    assert resp.status_code == 201, resp.content
    data = resp.json()
    return data['key'], data['id']


@pytest.fixture
def auth_headers(api_key):
    raw_key, _ = api_key
    return {'HTTP_X_API_KEY': raw_key}
