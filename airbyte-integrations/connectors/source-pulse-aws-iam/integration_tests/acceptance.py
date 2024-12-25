import pytest

pytest_plugins = ("connector_acceptance_test.plugin",)

@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    yield
