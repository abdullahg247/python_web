# flask_api/tests/conftest.py
import os
import sys
import pytest
from dotenv import load_dotenv

# --- Ensure project root on sys.path ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- Load .env if present (optional) ---
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# --- Import app factory ---
from flask_api.app import create_app  # noqa: E402

TEST_CONFIG = {
    "TESTING": True,
    "SECRET_KEY": "test-secret",
}


def _build_app():
    """
    Robustly create the Flask app whether create_app()
    expects 0 args or an optional config dict.
    """
    try:
        # Most common: no-arg factory
        app = create_app()
    except TypeError:
        # If factory requires a config dict
        app = create_app(TEST_CONFIG)

    # Ensure test config is applied either way
    app.config.update(TEST_CONFIG)
    return app


@pytest.fixture(scope="session")
def app():
    app = _build_app()
    # If your app uses app context-dependent stuff in tests, uncomment:
    # with app.app_context():
    #     yield app
    #     return
    yield app


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()
