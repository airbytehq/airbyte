#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict

from dagger import Container, Platform

from pipelines.airbyte_ci.connectors.context import ConnectorContext

BASE_DESTINATION_NORMALIZATION_BUILD_CONFIGURATION = {
    "destination-clickhouse": {
        "dockerfile": "clickhouse.Dockerfile",
        "dbt_adapter": "dbt-clickhouse>=1.4.0",
        "integration_name": "clickhouse",
        "normalization_image": "airbyte/normalization-clickhouse:0.4.3",
        "supports_in_connector_normalization": False,
        "yum_packages": [],
    },
    "destination-mssql": {
        "dockerfile": "mssql.Dockerfile",
        "dbt_adapter": "dbt-sqlserver==1.0.0",
        "integration_name": "mssql",
        "normalization_image": "airbyte/normalization-mssql:0.4.3",
        "supports_in_connector_normalization": True,
        "yum_packages": [],
    },
    "destination-mysql": {
        "dockerfile": "mysql.Dockerfile",
        "dbt_adapter": "dbt-mysql==1.0.0",
        "integration_name": "mysql",
        "normalization_image": "airbyte/normalization-mysql:0.4.3",
        "supports_in_connector_normalization": False,
        "yum_packages": [],
    },
    "destination-oracle": {
        "dockerfile": "oracle.Dockerfile",
        "dbt_adapter": "dbt-oracle==0.4.3",
        "integration_name": "oracle",
        "normalization_image": "airbyte/normalization-oracle:0.4.3",
        "supports_in_connector_normalization": False,
        "yum_packages": [],
    },
    "destination-postgres": {
        "dockerfile": "Dockerfile",
        "dbt_adapter": "dbt-postgres==1.0.0",
        "integration_name": "postgres",
        "normalization_image": "airbyte/normalization:0.4.3",
        "supports_in_connector_normalization": True,
        "yum_packages": [],
    },
    "destination-redshift": {
        "dockerfile": "redshift.Dockerfile",
        "dbt_adapter": "dbt-redshift==1.0.0",
        "integration_name": "redshift",
        "normalization_image": "airbyte/normalization-redshift:0.4.3",
        "supports_in_connector_normalization": True,
        "yum_packages": [],
    },
    "destination-tidb": {
        "dockerfile": "tidb.Dockerfile",
        "dbt_adapter": "dbt-tidb==1.0.1",
        "integration_name": "tidb",
        "normalization_image": "airbyte/normalization-tidb:0.4.3",
        "supports_in_connector_normalization": True,
        "yum_packages": [],
    },
}
DESTINATION_NORMALIZATION_BUILD_CONFIGURATION: Dict[str, Dict[str, Any]] = {
    **BASE_DESTINATION_NORMALIZATION_BUILD_CONFIGURATION,
    **{f"{k}-strict-encrypt": v for k, v in BASE_DESTINATION_NORMALIZATION_BUILD_CONFIGURATION.items()},
}


def with_normalization(context: ConnectorContext, build_platform: Platform) -> Container:
    normalization_image_name = DESTINATION_NORMALIZATION_BUILD_CONFIGURATION[context.connector.technical_name]["normalization_image"]
    assert isinstance(normalization_image_name, str)
    return context.dagger_client.container(platform=build_platform).from_(normalization_image_name)
