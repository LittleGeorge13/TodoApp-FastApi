from main import app
from routers.todos import get_db, get_current_user
from fastapi import status
from models import Todos
from .utils import * 

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{ 'complete': False,
                                'title': 'Learn to Code',
                                'description': 'Need to learn everyday!',
                                'id': 1,
                                'priority': 5,
                                'owner_id': 1 }]
    
def test_read_todo(test_todo):
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == { 'complete': False,
                                'title': 'Learn to Code',
                                'description': 'Need to learn everyday!',
                                'id': 1,
                                'priority': 5,
                                'owner_id': 1 }
    
def test_read_todo_authenticated_not_found(test_todo):
    response = client.get("/todos/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}

def test_create_todo(test_todo):
    request_data = {
        'title': 'new todo',
        'description': 'new todo desc',
        'complete': False,
        'priority': 5,
    }
    response = client.post("/todos", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.complete == request_data.get('complete')
    assert model.priority == request_data.get('priority')
    assert model.id == 2

def test_update_todo(test_todo):
    request_data = {
        'title': 'Changed the title',
        'description': 'Need to learn everyday!',
        'complete': False,
        'priority': 5,
    }

    response = client.put("/todos/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == 'Changed the title'

def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Changed the title',
        'description': 'Need to learn everyday!',
        'complete': False,
        'priority': 5,
    }

    response = client.put("/todos/999", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == { 'detail': 'Todo not found' }

def test_delete_todo(test_todo):
    response = client.delete("/todos/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()    
    assert model == None

def test_delete_todo_not_found(test_todo):
    response = client.delete("/todos/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == { 'detail': 'Todo not found' }