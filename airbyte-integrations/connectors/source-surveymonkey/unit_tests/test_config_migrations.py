#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json

from source_surveymonkey.config_migrations import MigrateAccessTokenToCredentials
from source_surveymonkey.source import SourceSurveymonkey


TEST_CONFIG = "test_old_config.json"
NEW_TEST_CONFIG = "test_new_config.json"
UPGRADED_TEST_CONFIG = "test_upgraded_config.json"


def revert_migration(config_path: str = TEST_CONFIG) -> None:
    config_path = "unit_tests/test_config_migrations/" + config_path
    with open(config_path, "r") as test_config:
        config = json.load(test_config)
        config.pop("credentials")
        with open(config_path, "w") as updated_config:
            config = json.dumps(config)
            updated_config.write(config)


def test_migrate_config(capsys, read_json):
    migration_instance = MigrateAccessTokenToCredentials()
    original_config = read_json(TEST_CONFIG)
    # migrate the test_config
    migration_instance.migrate(["check", "--config", "unit_tests/test_config_migrations/" + TEST_CONFIG], SourceSurveymonkey())
    # load the updated config
    test_migrated_config = read_json(TEST_CONFIG)
    # check migrated property
    assert "credentials" in test_migrated_config
    assert isinstance(test_migrated_config["credentials"], dict)
    assert "access_token" in test_migrated_config["credentials"]
    assert isinstance(test_migrated_config["access_token"], str)
    assert "auth_method" in test_migrated_config["credentials"]
    assert test_migrated_config["credentials"]["auth_method"] == "oauth2.0"
    # check the old property is in place
    assert "access_token" in test_migrated_config
    assert isinstance(test_migrated_config["access_token"], str)
    # check the migration should be skipped, once already done
    assert not migration_instance.should_migrate(test_migrated_config)
    # load the old custom reports VS migrated
    assert original_config["access_token"] == test_migrated_config["credentials"]["access_token"]
    # test CONTROL MESSAGE was emitted
    control_msg = json.loads(capsys.readouterr()[0].split("\n")[0])
    control = control_msg.get("control", {})
    config = control.get("connectorConfig", {}).get("config", {})

    assert control_msg.get("type") == "CONTROL"
    assert control.get("type") == "CONNECTOR_CONFIG"
    # old custom_reports are stil type(str)
    assert isinstance(config.get("access_token"), str)
    # new custom_reports are type(list)
    assert isinstance(config.get("credentials", {}).get("access_token"), str)
    # check the migrated values
    assert config.get("credentials", {}).get("access_token") == "access_token"
    # revert the test_config to the starting point
    revert_migration()


def test_config_is_reverted(read_json):
    # check the test_config state, it has to be the same as before tests
    test_config = read_json(TEST_CONFIG)
    # check the config no longer has the migarted property
    assert "credentials" not in test_config
    # check the old property is still there
    assert "access_token" in test_config
    assert isinstance(test_config["access_token"], str)


def test_should_not_migrate_new_config(read_json):
    new_config = read_json(NEW_TEST_CONFIG)
    migration_instance = MigrateAccessTokenToCredentials()
    assert not migration_instance.should_migrate(new_config)


def test_should_not_migrate_upgraded_config(read_json):
    new_config = read_json(UPGRADED_TEST_CONFIG)
    migration_instance = MigrateAccessTokenToCredentials()
    assert not migration_instance.should_migrate(new_config)
