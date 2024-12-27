# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os

from source_asana.config_migration import AsanaConfigMigration
from source_asana.source import SourceAsana


TEST_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_config.json"


def test_should_migrate():
    assert AsanaConfigMigration.should_migrate({"access_token": "asdfcxz"}) is True
    assert (
        AsanaConfigMigration.should_migrate(
            {"credentials": {"option_title": "PAT Credentials", "personal_access_token": "1206938133417909"}}
        )
        is False
    )


def test__modify_and_save():
    user_config = {"access_token": "asdfcxz"}
    expected = {"credentials": {"option_title": "PAT Credentials", "personal_access_token": "asdfcxz"}}

    # todo: need to make the migrate a classmethod instead of staticmethod since the missing config field will fail validation
    source = SourceAsana(config=user_config, catalog=None, state=None)

    modified_config = AsanaConfigMigration.modify_and_save(config_path=TEST_CONFIG_PATH, source=source, config=user_config)
    assert modified_config["credentials"]["personal_access_token"] == user_config["access_token"]
    assert modified_config["credentials"]["personal_access_token"] == expected["credentials"]["personal_access_token"]
    assert modified_config.get("credentials")
