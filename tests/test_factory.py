from flaskr import create_app

def test_config():
    """
    Test if the 'TESTING' configuration is being
    properly handled
    """
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing