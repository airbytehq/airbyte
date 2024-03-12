#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Mapping

import pytest
from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.sources import Source
from source_facebook_marketing.config_migrations import MigrateAccountIdToArray, MigrateIncludeDeletedToStatusFilters
from source_facebook_marketing.source import SourceFacebookMarketing

# BASE ARGS
CMD = "check"
SOURCE: Source = SourceFacebookMarketing()


# HELPERS
def load_config(config_path: str) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


class TestMigrateAccountIdToArray:
    TEST_CONFIG_PATH = "unit_tests/test_migrations/account_id_to_array/test_old_config.json"
    NEW_TEST_CONFIG_PATH = "unit_tests/test_migrations/account_id_to_array/test_new_config.json"
    UPGRADED_TEST_CONFIG_PATH = "unit_tests/test_migrations/account_id_to_array/test_upgraded_config.json"

    @staticmethod
    def revert_migration(config_path: str = TEST_CONFIG_PATH) -> None:
        with open(config_path, "r") as test_config:
            config = json.load(test_config)
            config.pop("account_ids")
            with open(config_path, "w") as updated_config:
                config = json.dumps(config)
                updated_config.write(config)

    def test_migrate_config(self):
        migration_instance = MigrateAccountIdToArray()
        original_config = load_config(self.TEST_CONFIG_PATH)
        # migrate the test_config
        migration_instance.migrate([CMD, "--config", self.TEST_CONFIG_PATH], SOURCE)
        # load the updated config
        test_migrated_config = load_config(self.TEST_CONFIG_PATH)
        # check migrated property
        assert "account_ids" in test_migrated_config
        assert isinstance(test_migrated_config["account_ids"], list)
        # check the old property is in place
        assert "account_id" in test_migrated_config
        assert isinstance(test_migrated_config["account_id"], str)
        # check the migration should be skipped, once already done
        assert not migration_instance.should_migrate(test_migrated_config)
        # load the old custom reports VS migrated
        assert [original_config["account_id"]] == test_migrated_config["account_ids"]
        # test CONTROL MESSAGE was emitted
        control_msg = migration_instance.message_repository._message_queue[0]
        assert control_msg.type == Type.CONTROL
        assert control_msg.control.type == OrchestratorType.CONNECTOR_CONFIG
        # old custom_reports are stil type(str)
        assert isinstance(control_msg.control.connectorConfig.config["account_id"], str)
        # new custom_reports are type(list)
        assert isinstance(control_msg.control.connectorConfig.config["account_ids"], list)
        # check the migrated values
        assert control_msg.control.connectorConfig.config["account_ids"] == ["01234567890"]
        # revert the test_config to the starting point
        self.revert_migration()

    def test_config_is_reverted(self):
        # check the test_config state, it has to be the same as before tests
        test_config = load_config(self.TEST_CONFIG_PATH)
        # check the config no longer has the migarted property
        assert "account_ids" not in test_config
        # check the old property is still there
        assert "account_id" in test_config
        assert isinstance(test_config["account_id"], str)

    def test_should_not_migrate_new_config(self):
        new_config = load_config(self.NEW_TEST_CONFIG_PATH)
        migration_instance = MigrateAccountIdToArray()
        assert not migration_instance.should_migrate(new_config)

    def test_should_not_migrate_upgraded_config(self):
        new_config = load_config(self.UPGRADED_TEST_CONFIG_PATH)
        migration_instance = MigrateAccountIdToArray()
        assert not migration_instance.should_migrate(new_config)


class TestMigrateIncludeDeletedToStatusFilters:
    OLD_TEST1_CONFIG_PATH = "unit_tests/test_migrations/include_deleted_to_status_filters/include_deleted_false/test_old_config.json"
    NEW_TEST1_CONFIG_PATH = "unit_tests/test_migrations/include_deleted_to_status_filters/include_deleted_false/test_new_config.json"
    OLD_TEST2_CONFIG_PATH = "unit_tests/test_migrations/include_deleted_to_status_filters/include_deleted_true/test_old_config.json"
    NEW_TEST2_CONFIG_PATH = "unit_tests/test_migrations/include_deleted_to_status_filters/include_deleted_true/test_new_config.json"

    UPGRADED_TEST_CONFIG_PATH = "unit_tests/test_migrations/account_id_to_array/test_upgraded_config.json"

    filter_properties = ["ad_statuses", "adset_statuses", "campaign_statuses"]

    def revert_migration(self, config_path: str) -> None:
        with open(config_path, "r") as test_config:
            config = json.load(test_config)
            for filter in self.filter_properties:
                config.pop(filter)
            with open(config_path, "w") as updated_config:
                config = json.dumps(config)
                updated_config.write(config)

    @pytest.mark.parametrize(
        "old_config_path, new_config_path, include_deleted",
        [(OLD_TEST1_CONFIG_PATH, NEW_TEST1_CONFIG_PATH, False), (OLD_TEST2_CONFIG_PATH, NEW_TEST2_CONFIG_PATH, True)],
    )
    def test_migrate_config(self, old_config_path, new_config_path, include_deleted):
        migration_instance = MigrateIncludeDeletedToStatusFilters()
        # migrate the test_config
        migration_instance.migrate([CMD, "--config", old_config_path], SOURCE)
        # load the updated config
        test_migrated_config = load_config(old_config_path)
        # load expected updated config
        expected_new_config = load_config(new_config_path)
        # compare expected with migrated
        assert expected_new_config == test_migrated_config
        # check migrated property
        if include_deleted:
            assert all([filter in test_migrated_config for filter in self.filter_properties])
        # check the old property is in place
        assert "include_deleted" in test_migrated_config
        assert test_migrated_config["include_deleted"] == include_deleted
        # check the migration should be skipped, once already done
        assert not migration_instance.should_migrate(test_migrated_config)
        if include_deleted:
            # test CONTROL MESSAGE was emitted
            control_msg = migration_instance.message_repository._message_queue[0]
            assert control_msg.type == Type.CONTROL
            assert control_msg.control.type == OrchestratorType.CONNECTOR_CONFIG
            # revert the test_config to the starting point
            self.revert_migration(old_config_path)

    @pytest.mark.parametrize("new_config_path", [NEW_TEST1_CONFIG_PATH, NEW_TEST2_CONFIG_PATH])
    def test_should_not_migrate_new_config(self, new_config_path):
        new_config = load_config(new_config_path)
        migration_instance = MigrateIncludeDeletedToStatusFilters()
        assert not migration_instance.should_migrate(new_config)

    def test_should_not_migrate_upgraded_config(self):
        new_config = load_config(self.UPGRADED_TEST_CONFIG_PATH)
        migration_instance = MigrateIncludeDeletedToStatusFilters()
        assert not migration_instance.should_migrate(new_config)
