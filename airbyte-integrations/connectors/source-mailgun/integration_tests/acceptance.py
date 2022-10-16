#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import json
import os.path
from typing import Any, Dict, Iterable

import pytest

from .fill_data import DataFiller

pytest_plugins = ("source_acceptance_test.plugin",)


class Config:

    messages_per_sender: int = 5
    min_update_interval: int = datetime.timedelta(2).total_seconds()  # 2 days

    recipients: Iterable[str] = [
        "integration-test@airbyte.io",
    ]
    senders: Iterable[str] = [
        "Ann",
        "Bob",
        "Carl",
    ]

    test_data_file_path: str = os.path.join(os.path.dirname(__file__), "test_data.json")

    @classmethod
    def get_test_data(cls) -> Dict[str, Any]:
        with open(cls.test_data_file_path) as tdf:
            return json.load(tdf)

    @classmethod
    def update_timestamp(cls, timestamp: float):
        test_data = cls.get_test_data()
        test_data.update({"last_update_timestamp": timestamp})
        with open(cls.test_data_file_path, "w") as tdf:
            json.dump(test_data, tdf)


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    """
    Fill the sandbox with fresh data by sending simple text-only messages.
    """
    config = Config
    now = datetime.datetime.now().timestamp()
    if config.get_test_data()["last_update_timestamp"] + config.min_update_interval <= now:
        data_filler: DataFiller = DataFiller(
            from_emails=config.senders, to=config.recipients, number_of_messages=config.messages_per_sender
        )
        data_filler.fill()
        config.update_timestamp(now)

    yield
