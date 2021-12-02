import pytest
from mib import create_app

@pytest.fixture(scope="session", autouse=True)
def test_client():
    app = create_app()
    with app.app_context():
        with app.test_client() as client:
            yield client


