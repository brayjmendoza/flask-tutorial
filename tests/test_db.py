import sqlite3

import pytest
from flaskr.db import get_db


def test_get_close_db(app):
    """
    Test if get_db returns the same connection each
    time it's called and if the connection is closed
    after the context
    """
    # Test if each connection is the same
    with app.app_context():
        db = get_db()
        assert db is get_db()

    # Test if the connection is closed
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

def test_init_db_command(runner, monkeypatch):
    """
    Test that the init-db command called the init_db
    function and has an output message
    """
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called