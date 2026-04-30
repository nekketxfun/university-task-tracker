import pytest
from task_tracker.models import Task

@pytest.mark.django_db
def test_create_task(authenticated_client):
    data = {
        'title': 'Test Task',
        'description': 'Description',
        'deadline': '2026-12-31T23:59:59Z',
        'priority': 'medium'
    }
    response = authenticated_client.post('/api/v1/tasks/', data, format='json')
    assert response.status_code == 201
    assert Task.objects.count() == 1