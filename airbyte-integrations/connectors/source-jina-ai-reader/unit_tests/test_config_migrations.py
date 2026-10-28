# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
import os
import shutil

from source_jina_ai_reader.config_migration import JinaAiReaderConfigMigration
from source_jina_ai_reader.source import SourceJinaAiReader


TEST_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_config.json"


def test_should_migrate():
    assert JinaAiReaderConfigMigration.should_migrate({"search_prompt": "What is AI"}) is True
    assert JinaAiReaderConfigMigration.should_migrate({"search_prompt": "What%20is%20AI"}) is False


def test__modify_and_save(tmp_path):
    source = SourceJinaAiReader()
    user_config = {"search_prompt": "What is AI"}
    expected = {"search_prompt": "What%20is%20AI"}
    config_path = str(tmp_path / "test_config.json")
    shutil.copyfile(TEST_CONFIG_PATH, config_path)
    modified_config = JinaAiReaderConfigMigration.modify_and_save(config_path=config_path, source=source, config=user_config)
    assert modified_config["search_prompt"] == expected["search_prompt"]
    assert modified_config.get("search_prompt")


def test_migrate_emits_control_message(tmp_path, capsys):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"search_prompt": "What is AI"}))

    JinaAiReaderConfigMigration.migrate(["check", "--config", str(config_path)], SourceJinaAiReader)

    control_message = json.loads(capsys.readouterr().out)
    assert control_message["type"] == "CONTROL"
    assert control_message["control"]["connectorConfig"]["config"]["search_prompt"] == "What%20is%20AI"
    assert json.loads(config_path.read_text())["search_prompt"] == "What%20is%20AI"


def test_migrate_does_not_emit_control_message_for_encoded_prompt(tmp_path, capsys):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"search_prompt": "What%20is%20AI"}))

    JinaAiReaderConfigMigration.migrate(["check", "--config", str(config_path)], SourceJinaAiReader)

    assert capsys.readouterr().out == ""
