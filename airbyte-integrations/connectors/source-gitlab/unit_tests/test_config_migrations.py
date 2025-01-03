# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os

from source_gitlab.config_migrations import MigrateGroups
from source_gitlab.source import SourceGitlab


TEST_CONFIG_PATH = f"{os.path.dirname(__file__)}/test_config.json"


def test_should_migrate():
    assert MigrateGroups._should_migrate({"groups": "group group2 group3"}) is True
    assert MigrateGroups._should_migrate({"groups_list": ["test", "group2", "group3"]}) is False


def test__modify_and_save():
    source = SourceGitlab()
    expected = {"groups": "a b c", "groups_list": ["b", "c", "a"]}
    modified_config = MigrateGroups._modify_and_save(config_path=TEST_CONFIG_PATH, source=source, config={"groups": "a b c"})
    assert modified_config["groups_list"].sort() == expected["groups_list"].sort()
    assert modified_config.get("groups")
