import os

# Disable the LLM in tests so the suite is deterministic and offline. Set before
# importing app so load_dotenv (override=False) won't re-enable Gemini.
os.environ["LLM_PROVIDER"] = "disabled"

import pytest

from app import create_app
from config import Config
from extensions import db as _db


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret"


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
