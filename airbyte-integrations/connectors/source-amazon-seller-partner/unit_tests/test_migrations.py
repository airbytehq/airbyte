#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Mapping

from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.sources import Source
from source_amazon_seller_partner.config_migrations import MigrateAccountType
from source_amazon_seller_partner.source import SourceAmazonSellerPartner

CMD = "check"
TEST_NOT_MIGRATED_CONFIG_PATH = "unit_tests/test_migrations/not_migrated_config.json"
TEST_MIGRATED_CONFIG_PATH = "unit_tests/test_migrations/migrated_config.json"
SOURCE: Source = SourceAmazonSellerPartner()


def load_config(config_path: str = TEST_NOT_MIGRATED_CONFIG_PATH) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def test_migrate_config(capsys):
    config = load_config(TEST_NOT_MIGRATED_CONFIG_PATH)
    assert "acount_type" not in config
    migration_instance = MigrateAccountType()
    migration_instance.migrate([CMD, "--config", TEST_NOT_MIGRATED_CONFIG_PATH], SOURCE)
    control_msg = json.loads(capsys.readouterr().out)
    assert control_msg["type"] == Type.CONTROL.value
    assert control_msg["control"]["type"] == OrchestratorType.CONNECTOR_CONFIG.value
    migrated_config = control_msg["control"]["connectorConfig"]["config"]
    assert migrated_config["account_type"] == "Seller"


def test_should_not_migrate():
    config = load_config(TEST_MIGRATED_CONFIG_PATH)
    assert config["account_type"]
    migration_instance = MigrateAccountType()
    assert not migration_instance._should_migrate(config)
