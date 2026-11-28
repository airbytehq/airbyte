#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from typing import Mapping

import pytest
from source_arxiv.streams import ArxivStream


RESOURCE_DIR = Path(__file__).parent / "resource"


@pytest.fixture(autouse=True)
def disable_rate_limit_sleep(mocker):
    mocker.patch.object(ArxivStream, "_throttle", lambda self: None)


@pytest.fixture
def config() -> Mapping[str, object]:
    return {"search_query": "cat:cs.AI", "max_results_per_page": 2}


@pytest.fixture
def xml_fixture():
    def _read(name: str) -> str:
        return (RESOURCE_DIR / name).read_text()

    return _read
