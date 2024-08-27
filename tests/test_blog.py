import pytest
from flaskr.db import get_db


def test_index(client, auth):
    """
    Test the index view function
    """
    # index when no user is logged in
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    # index when the user is logged in 
    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    
    # logged in users have a link to update their posts
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    """
    Test expected behavior for views that require a
    user to be logged in (redirect to login page)
    """
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    """
    Tests that certain functions are blocked when the user
    is not the author of the post
    """
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403

    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exist_required(client, auth, path):
    """
    Test that if a post with a given id doesn't exist,
    `update` and `delete` return 404 Not Found
    """
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    """
    Test the create view function

    Expected behavior (when logged in):
    - GET requests return a 200 OK status
    - POST requests insert new post data into the database
    """
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2   # two posts from this user

    
def test_update(client, auth, app):
    """
    Tests the update view function

    Expected behavior (when logged in):
    - GET requests return a 200 OK status
    - POST requests modifies existing data in the database
    """
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    """
    Tests if an error is thrown for invalid data for
    the create and update view functions
    """
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


def test_delete(client, auth, app):
    """
    Tests the delete view function

    Expected behavior:
    - Redirect to the index URL
    - Deleted post should no longer exist in the database
    """
    auth.login()
    response = client.post('/1/delete')
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None