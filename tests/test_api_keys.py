import pytest


@pytest.mark.django_db
def test_create_api_key(api_client, admin_headers):
    resp = api_client.post('/api/v1/api-keys/', {'name': 'Alpha'}, format='json', **admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert 'key' in data
    assert 'key_hash' not in data
    assert data['name'] == 'Alpha'


@pytest.mark.django_db
def test_list_api_keys(api_client, admin_headers):
    api_client.post('/api/v1/api-keys/', {'name': 'Beta'}, format='json', **admin_headers)
    resp = api_client.get('/api/v1/api-keys/', **admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert 'results' in data
    for row in data['results']:
        assert 'key_hash' not in row
        assert 'key' not in row


@pytest.mark.django_db
def test_revoke_api_key(api_client, admin_headers):
    create_resp = api_client.post('/api/v1/api-keys/', {'name': 'Gamma'}, format='json', **admin_headers)
    key_id = create_resp.json()['id']
    resp = api_client.delete(f'/api/v1/api-keys/{key_id}/', **admin_headers)
    assert resp.status_code == 200
    assert resp.json()['is_active'] is False


@pytest.mark.django_db
def test_update_api_key(api_client, admin_headers):
    create_resp = api_client.post('/api/v1/api-keys/', {'name': 'Delta'}, format='json', **admin_headers)
    key_id = create_resp.json()['id']
    resp = api_client.put(f'/api/v1/api-keys/{key_id}/', {'name': 'Delta Renamed', 'is_active': True}, format='json', **admin_headers)
    assert resp.status_code == 200
    assert resp.json()['name'] == 'Delta Renamed'


@pytest.mark.django_db
def test_create_api_key_missing_admin_header_rejected(api_client):
    resp = api_client.post('/api/v1/api-keys/', {'name': 'NoAuth'}, format='json')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_create_api_key_wrong_admin_header_rejected(api_client):
    resp = api_client.post(
        '/api/v1/api-keys/', {'name': 'WrongAuth'}, format='json',
        HTTP_X_ADMIN_KEY='wrong-key-value',
    )
    assert resp.status_code == 403
