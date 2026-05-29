from main import app
from routers.users import get_db, get_current_user
from fastapi import status
# from models import Todos
from .utils import * 

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get('/users')
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == 'admin@test.com'
    assert response.json()['username'] == 'admin'
    assert response.json()['first_name'] == 'admin'
    assert response.json()['last_name'] == 'admin'
    assert response.json()['is_active'] == True
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '4491231234'

def test_change_password_success(test_user):
    request = {
        'prevPassword': 'password',
        'newPassword': 'newPassword'
    }
    response = client.put("/users/change_password", json=request)

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid_current_password(test_user):
    request = {
        'prevPassword': 'incorrectpassword',
        'newPassword': 'newPassword'
    }
    response = client.put("/users/change_password", json=request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == { 'detail': 'Password is incorrect' }

def test_change_password_current_password_and_new_password_are_equal(test_user):
    request = {
        'prevPassword': 'password',
        'newPassword': 'password'
    }
    response = client.put("/users/change_password", json=request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == { 'detail': 'The previous password cannot be the same as the new password' }

def test_change_phone_number_success(test_user):
    response = client.put('/users/phonenumber/4497894561')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == 1).first()
    assert model.phone_number == '4497894561'