# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from .conftest import get_source


def test_config_migrations():
    old_style_config = {"username": "config_username", "password": "config_password", "report_ids": ["report_1", "report_2"]}

    source = get_source(old_style_config)
    migrated_config = source._config
    assert migrated_config.get("credentials", False)
    assert migrated_config["credentials"].get("username") == "config_username"
    assert migrated_config["credentials"].get("password") == "config_password"
    assert migrated_config["report_ids"] == [{"report_id": "report_1"}, {"report_id": "report_2"}]

    new_style_config = {
        "credentials": {"username": "config_username", "password": "config_username"},
        "report_ids": [{"report_id": "report_1"}, {"report_id": "report_2"}],
    }
    source = get_source(new_style_config)
    migrated_config = source._config
    assert new_style_config == migrated_config
