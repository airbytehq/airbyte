from typing import Dict, Any

import pytest as pytest


@pytest.fixture
def test_config() -> Dict[str, Any]:
    return {
        "private_key": "test_private_key"
    }
