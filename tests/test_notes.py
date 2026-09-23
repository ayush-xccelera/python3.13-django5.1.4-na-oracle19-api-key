import pytest


@pytest.mark.django_db
def test_create_note(api_client, auth_headers):
    resp = api_client.post(
        '/api/v1/notes/', {'title': 'My Note', 'content': 'Hello world'},
        format='json', **auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data['status'] == 'ACTIVE'
    assert data['title'] == 'My Note'


@pytest.mark.django_db
def test_list_notes_returns_only_active_for_owner(api_client, auth_headers):
    api_client.post('/api/v1/notes/', {'title': 'N1', 'content': 'c1'}, format='json', **auth_headers)
    resp = api_client.get('/api/v1/notes/', **auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert 'results' in data
    for row in data['results']:
        assert row['status'] == 'ACTIVE'


@pytest.mark.django_db
def test_retrieve_note(api_client, auth_headers):
    create_resp = api_client.post('/api/v1/notes/', {'title': 'R1', 'content': 'c'}, format='json', **auth_headers)
    note_id = create_resp.json()['id']
    resp = api_client.get(f'/api/v1/notes/{note_id}/', **auth_headers)
    assert resp.status_code == 200
    assert resp.json()['id'] == note_id


@pytest.mark.django_db
def test_update_note(api_client, auth_headers):
    create_resp = api_client.post('/api/v1/notes/', {'title': 'U1', 'content': 'c'}, format='json', **auth_headers)
    note_id = create_resp.json()['id']
    resp = api_client.put(
        f'/api/v1/notes/{note_id}/', {'title': 'U1 updated', 'content': 'c updated'},
        format='json', **auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()['title'] == 'U1 updated'


@pytest.mark.django_db
def test_update_note_empty_title_rejected(api_client, auth_headers):
    create_resp = api_client.post('/api/v1/notes/', {'title': 'U2', 'content': 'c'}, format='json', **auth_headers)
    note_id = create_resp.json()['id']
    resp = api_client.put(
        f'/api/v1/notes/{note_id}/', {'title': '', 'content': 'c'},
        format='json', **auth_headers,
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_archive_and_restore_note(api_client, auth_headers):
    create_resp = api_client.post('/api/v1/notes/', {'title': 'A1', 'content': 'c'}, format='json', **auth_headers)
    note_id = create_resp.json()['id']

    archive_resp = api_client.patch(f'/api/v1/notes/{note_id}/archive/', **auth_headers)
    assert archive_resp.status_code == 200
    assert archive_resp.json()['status'] == 'ARCHIVED'

    restore_resp = api_client.patch(f'/api/v1/notes/{note_id}/restore/', **auth_headers)
    assert restore_resp.status_code == 200
    assert restore_resp.json()['status'] == 'ACTIVE'


@pytest.mark.django_db
def test_delete_note(api_client, auth_headers):
    create_resp = api_client.post('/api/v1/notes/', {'title': 'D1', 'content': 'c'}, format='json', **auth_headers)
    note_id = create_resp.json()['id']
    resp = api_client.delete(f'/api/v1/notes/{note_id}/', **auth_headers)
    assert resp.status_code == 204
    get_resp = api_client.get(f'/api/v1/notes/{note_id}/', **auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.django_db
def test_notes_missing_api_key_rejected(api_client):
    resp = api_client.get('/api/v1/notes/')
    assert resp.status_code == 401


@pytest.mark.django_db
def test_notes_owner_isolation(api_client, admin_headers, auth_headers):
    # Create a second client and note; the first client should not see it.
    create_resp = api_client.post('/api/v1/api-keys/', {'name': 'Other Client'}, format='json', **admin_headers)
    other_key = create_resp.json()['key']
    other_headers = {'HTTP_X_API_KEY': other_key}

    other_note_resp = api_client.post(
        '/api/v1/notes/', {'title': 'Other Note', 'content': 'c'}, format='json', **other_headers,
    )
    other_note_id = other_note_resp.json()['id']

    resp = api_client.get(f'/api/v1/notes/{other_note_id}/', **auth_headers)
    assert resp.status_code == 404
