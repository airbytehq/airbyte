import pytest

from destination_netsuite.netsuite.service import JournalEntry
from destination_netsuite.netsuite.configuration import Config


@pytest.fixture
def dummy_config():
    return Config(
        base_url="https://5851367.suitetalk.api.netsuite.com",
        token_auth={
            "consumer_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "consumer_secret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "token_id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "token_secret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        },
    )
@pytest.fixture
def journal_entry(dummy_config: Config):
    return JournalEntry(config=dummy_config)