# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os

from source_jina_ai_reader.config_migration import JinaAiReaderConfigMigration
from source_jina_ai_reader.source import SourceJinaAiReader

TEST_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_config.json"


def test_should_migrate():
    assert JinaAiReaderConfigMigration.should_migrate({"search_prompt": "What is AI"}) is True
    assert JinaAiReaderConfigMigration.should_migrate({"search_prompt": "What%20is%20AI"}) is False


def test__modify_and_save():
    source = SourceJinaAiReader()
    user_config = {"search_prompt": "What is AI"}
    expected = {"search_prompt": "What%20is%20AI" }
    modified_config = JinaAiReaderConfigMigration.modify_and_save(config_path=TEST_CONFIG_PATH, source=source, config=user_config)
    assert modified_config["search_prompt"] == expected["search_prompt"]
    assert modified_config.get("search_prompt")
