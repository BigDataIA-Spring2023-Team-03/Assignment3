import pytest
from fastapi.testclient import TestClient
from apis import app
from Util.DbUtil import DbUtil

client = TestClient(app)


@pytest.fixture
def model():
    return {
        "first_name": "FN_test",
        "last_name": "LN_test",
        "email": "email_test@gmail.com",
        "password": "pass_test"
    }

@pytest.fixture(scope='function')
def cleanup():
    yield
    dbUtil = DbUtil('database/metadata.db')
    cursor = dbUtil.conn.cursor()
    cursor.execute("DELETE FROM users WHERE email = 'email_test@gmail.com'")
    dbUtil.conn.commit()

def test_register(model):
    response = client.post("/user/register", json=model)
    assert response.status_code == 200
    assert 'access_token' in response.json()

@pytest.mark.usefixtures('cleanup')
def test_login(model):
    # positive case
    response = client.post("/user/login", json={
        "email": model["email"],
        "password": model["password"]
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()

    # negative case
    response = client.post("/user/login", json={
        "email": "random@gmail.com",
        "password": "randomPass"
    })
    assert response.status_code == 401
