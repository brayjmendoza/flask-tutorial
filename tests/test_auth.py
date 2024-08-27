import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    """
    Test the register view function

    Expected behavior:
    GET - successful render
    POST - redirect to the login URL (with valid form data, 
            which is then stored in the database)
    """
    # Test GET
    assert client.get('/auth/register').status_code == 200

    # Test POST
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"

    # Ensure new login data stored in database
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    """
    Tests the error messages when registering
    """
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data

def test_login(client, auth):
    """
    Test the login view

    Expected behavior:
    - GET request should render successfully
    - URL name is "/"
    - POST request should login the user
    - session should have a user_id set after logging in
    """
    # Test GET request
    assert client.get('/auth/login').status_code == 200

    # Simulate a login (POST request)
    response = auth.login()
    assert response.headers["Location"] == "/"
    
    # allow accessing context variables (accessing session outside of a request usually raises an error)
    with client:
        client.get('/')

        # User logged in successfully
        assert session['user_id'] == 1      
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    """
    Tests the error messages when logging in 
    """
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    """
    Tests the logout view function
    """
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session