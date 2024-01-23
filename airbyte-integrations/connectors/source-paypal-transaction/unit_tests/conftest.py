import pytest
from source_paypal_transaction import SourcePaypalTransaction

@pytest.fixture(name="config")
def config_fixture():
    return {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "start_date": "2022-01-01T00:00:00Z",
        "is_sandbox": True
    }

@pytest.fixture(name="source")
def source_fixture():
    return SourcePaypalTransaction()