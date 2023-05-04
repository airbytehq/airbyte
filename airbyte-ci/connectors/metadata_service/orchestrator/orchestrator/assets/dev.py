import pandas as pd
import yaml
import json
from pydash.collections import key_by
from deepdiff import DeepDiff
from dagster import Output, asset, OpExecutionContext, MetadataValue
from typing import List

from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe
from orchestrator.models.metadata import PartialMetadataDefinition

from metadata_service.models.generated.ConnectorRegistryV0 import ConnectorRegistryV0


"""
NOTE: This file is temporary and will be removed once we have metadata files checked into source control.

TODO (ben): Remove this file once we have metadata files checked into source control.
"""

GROUP_NAME = "dev"


# These are the overrides for our generated metadata files.
# Applying these overrides is what is required for them to pass validation.
OVERRIDES = {
    # airbyte/source-freshcaller
    "8a5d48f6-03bb-4038-a942-a8d3f175cca3": {"connectorSubtype": "api", "releaseStage": "alpha"},
    # airbyte/source-genesys
    "5ea4459a-8f1a-452a-830f-a65c38cc438d": {"connectorSubtype": "api", "releaseStage": "alpha"},
    # airbyte/source-rss
    "0efee448-6948-49e2-b786-17db50647908": {"connectorSubtype": "api", "releaseStage": "alpha"},
    # airbyte/destination-azure-blob-storage
    "b4c5d105-31fd-4817-96b6-cb923bfc04cb": {"connectorSubtype": "file"},
    # airbyte/destination-amazon-sqs
    "0eeee7fb-518f-4045-bacc-9619e31c43ea": {"connectorSubtype": "api"},
    # airbyte/destination-doris
    "05c161bf-ca73-4d48-b524-d392be417002": {"connectorSubtype": "database"},
    # airbyte/destination-iceberg
    "df65a8f3-9908-451b-aa9b-445462803560": {"connectorSubtype": "database"},
    # airbyte/destination-aws-datalake
    "99878c90-0fbd-46d3-9d98-ffde879d17fc": {"connectorSubtype": "database"},
    # airbyte/destination-bigquery
    "22f6c74f-5699-40ff-833c-4a879ea40133": {"connectorSubtype": "database"},
    # airbyte/destination-bigquery-denormalized
    "079d5540-f236-4294-ba7c-ade8fd918496": {"connectorSubtype": "database"},
    # airbyte/destination-cassandra
    "707456df-6f4f-4ced-b5c6-03f73bcad1c5": {"connectorSubtype": "database"},
    # airbyte/destination-keen
    "81740ce8-d764-4ea7-94df-16bb41de36ae": {"connectorSubtype": "api"},
    # airbyte/destination-clickhouse
    "ce0d828e-1dc4-496c-b122-2da42e637e48": {"connectorSubtype": "database"},
    # airbyte/destination-r2
    "0fb07be9-7c3b-4336-850d-5efc006152ee": {"connectorSubtype": "file"},
    # airbyte/destination-databricks
    "072d5540-f236-4294-ba7c-ade8fd918496": {"connectorSubtype": "database"},
    # airbyte/destination-dynamodb
    "8ccd8909-4e99-4141-b48d-4984b70b2d89": {"connectorSubtype": "database"},
    # airbyte/destination-e2e-test
    "2eb65e87-983a-4fd7-b3e3-9d9dc6eb8537": {"connectorSubtype": "unknown", "releaseStage": "alpha"},
    # airbyte/destination-elasticsearch
    "68f351a7-2745-4bef-ad7f-996b8e51bb8c": {"connectorSubtype": "api"},
    # airbyte/destination-exasol
    "bb6071d9-6f34-4766-bec2-d1d4ed81a653": {"connectorSubtype": "database"},
    # airbyte/destination-firebolt
    "18081484-02a5-4662-8dba-b270b582f321": {"connectorSubtype": "database"},
    # airbyte/destination-gcs
    "ca8f6566-e555-4b40-943a-545bf123117a": {"connectorSubtype": "file"},
    # airbyte/destination-firestore
    "27dc7500-6d1b-40b1-8b07-e2f2aea3c9f4": {"connectorSubtype": "database"},
    # airbyte/destination-pubsub
    "356668e2-7e34-47f3-a3b0-67a8a481b692": {"connectorSubtype": "api"},
    # airbyte/destination-kafka
    "9f760101-60ae-462f-9ee6-b7a9dafd454d": {"connectorSubtype": "database"},
    # airbyte/destination-kinesis
    "6d1d66d4-26ab-4602-8d32-f85894b04955": {"connectorSubtype": "api"},
    # airbyte/destination-csv
    "8be1cf83-fde1-477f-a4ad-318d23c9f3c6": {"connectorSubtype": "file"},
    # airbyte/destination-local-json
    "a625d593-bba5-4a1c-a53d-2d246268a816": {"connectorSubtype": "file"},
    # airbyte/destination-mqtt
    "f3802bc4-5406-4752-9e8d-01e504ca8194": {"connectorSubtype": "message_queue"},
    # airbyte/destination-mssql
    "d4353156-9217-4cad-8dd7-c108fd4f74cf": {"connectorSubtype": "database"},
    # airbyte/destination-meilisearch
    "af7c921e-5892-4ff2-b6c1-4a5ab258fb7e": {"connectorSubtype": "api"},
    # airbyte/destination-mongodb
    "8b746512-8c2e-6ac1-4adc-b59faafd473c": {"connectorSubtype": "database"},
    # airbyte/destination-mysql
    "ca81ee7c-3163-4246-af40-094cc31e5e42": {"connectorSubtype": "database"},
    # airbyte/destination-oracle
    "3986776d-2319-4de9-8af8-db14c0996e72": {"connectorSubtype": "database"},
    # airbyte/destination-postgres
    "25c5221d-dce2-4163-ade9-739ef790f503": {"connectorSubtype": "database"},
    # airbyte/destination-pulsar
    "2340cbba-358e-11ec-8d3d-0242ac130203": {"connectorSubtype": "database"},
    # airbyte/destination-rabbitmq
    "e06ad785-ad6f-4647-b2e8-3027a5c59454": {"connectorSubtype": "database"},
    # airbyte/destination-redis
    "d4d3fef9-e319-45c2-881a-bd02ce44cc9f": {"connectorSubtype": "database"},
    # airbyte/destination-redshift
    "f7a7d195-377f-cf5b-70a5-be6b819019dc": {"connectorSubtype": "database"},
    # airbyte/destination-redpanda
    "825c5ee3-ed9a-4dd1-a2b6-79ed722f7b13": {"connectorSubtype": "database"},
    # airbyte/destination-rockset
    "2c9d93a7-9a17-4789-9de9-f46f0097eb70": {"connectorSubtype": "database"},
    # airbyte/destination-s3
    "4816b78f-1489-44c1-9060-4b19d5fa9362": {"connectorSubtype": "file"},
    # airbyte/destination-s3-glue
    "471e5cab-8ed1-49f3-ba11-79c687784737": {"connectorSubtype": "file"},
    # airbyte/destination-sftp-json
    "e9810f61-4bab-46d2-bb22-edfc902e0644": {"connectorSubtype": "file"},
    # airbyte/destination-snowflake
    "424892c4-daac-4491-b35d-c6688ba547ba": {"connectorSubtype": "database"},
    # airbyte/destination-mariadb-columnstore
    "294a4790-429b-40ae-9516-49826b9702e1": {"connectorSubtype": "database"},
    # ghcr.io/devmate-cloud/streamr-airbyte-connectors
    "eebd85cf-60b2-4af6-9ba0-edeca01437b0": {"connectorSubtype": "api"},
    # airbyte/destination-scylla
    "3dc6f384-cd6b-4be3-ad16-a41450899bf0": {"connectorSubtype": "database"},
    # airbyte/destination-google-sheets
    "a4cbd2d1-8dbe-4818-b8bc-b90ad782d12a": {"connectorSubtype": "api"},
    # airbyte/destination-sqlite
    "b76be0a6-27dc-4560-95f6-2623da0bd7b6": {"connectorSubtype": "database"},
    # airbyte/destination-tidb
    "06ec60c7-7468-45c0-91ac-174f6e1a788b": {"connectorSubtype": "database"},
    # airbyte/destination-typesense
    "36be8dc6-9851-49af-b776-9d4c30e4ab6a": {"connectorSubtype": "database"},
    # airbyte/destination-yugabytedb
    "2300fdcf-a532-419f-9f24-a014336e7966": {"connectorSubtype": "database"},
    # airbyte/destination-databend
    "302e4d8e-08d3-4098-acd4-ac67ca365b88": {"connectorSubtype": "database"},
    # airbyte/destination-teradata
    "58e6f9da-904e-11ed-a1eb-0242ac120002": {"connectorSubtype": "database"},
    # airbyte/destination-weaviate
    "7b7d7a0d-954c-45a0-bcfc-39a634b97736": {"connectorSubtype": "database"},
    # airbyte/destination-duckdb
    "94bd199c-2ff0-4aa2-b98e-17f0acb72610": {"connectorSubtype": "database"},
    # airbyte/destination-dev-null
    "a7bcc9d8-13b3-4e49-b80d-d020b90045e3": {"connectorSubtype": "file"},
}

# HELPERS


def key_registry_entries(registry: List[dict]) -> dict:
    """Transforms a List of connectors into a dictionary keyed by the connector id.

    Args:
        registry (List[dict]): List of connectors

    Returns:
        dict: Dictionary of connectors keyed by the connector id
    """
    registry_keyed = registry.copy()
    for connector_type, id_field in [("sources", "sourceDefinitionId"), ("destinations", "destinationDefinitionId")]:
        registry_keyed[connector_type] = key_by(registry_keyed[connector_type], id_field)
    return registry_keyed


def diff_registries(registry_dict_1: dict, registry_dict_2: dict) -> DeepDiff:
    """Compares two registries and returns a DeepDiff object.

    Args:
        registry_dict_1 (dict)
        registry_dict_2 (dict)

    Returns:
        DeepDiff
    """
    new_metadata_fields = [
        r"githubIssueLabel",
        r"license",
    ]

    removed_metadata_fields = [
        r"protocolVersion",
    ]

    # TODO (ben) remove this when checking the final registry from GCS metadata
    temporarily_ignored_fields = [
        r"spec",
    ]

    excludedRegex = new_metadata_fields + removed_metadata_fields + temporarily_ignored_fields
    keyed_registry_dict_1 = key_registry_entries(registry_dict_1)
    keyed_registry_dict_2 = key_registry_entries(registry_dict_2)

    return DeepDiff(keyed_registry_dict_1, keyed_registry_dict_2, ignore_order=True, exclude_regex_paths=excludedRegex, verbose_level=2)


# ASSETS


@asset(group_name=GROUP_NAME)
def overrode_metadata_definitions(
    legacy_registry_derived_metadata_definitions: List[PartialMetadataDefinition],
) -> List[PartialMetadataDefinition]:
    """
    Overrides the metadata definitions with the values in the OVERRIDES dictionary.
    This is useful for ensuring all connectors are passing validation when we go live.
    """
    overrode_definitions = []
    for metadata_definition in legacy_registry_derived_metadata_definitions:
        definition_id = metadata_definition["data"]["definitionId"]
        if definition_id in OVERRIDES:
            metadata_definition["data"].update(OVERRIDES[definition_id])
        overrode_definitions.append(metadata_definition)

    return overrode_definitions


@asset(required_resource_keys={"metadata_file_directory"}, group_name=GROUP_NAME)
def persist_metadata_definitions(context: OpExecutionContext, overrode_metadata_definitions: List[PartialMetadataDefinition]):
    """
    Persist the metadata definitions to the local metadata file directory.
    """
    files = []
    for metadata in overrode_metadata_definitions:
        connector_dir_name = metadata["data"]["dockerRepository"].replace("airbyte/", "")
        definitionId = metadata["data"]["definitionId"]

        key = f"{connector_dir_name}-{definitionId}"

        yaml_string = yaml.dump(metadata.dict())

        file = context.resources.metadata_file_directory.write_data(yaml_string.encode(), ext="yaml", key=key)
        files.append(file)

    file_paths = [file.path for file in files]
    file_paths_str = "\n".join(file_paths)

    return Output(files, metadata={"count": len(files), "file_paths": file_paths_str})


@asset(group_name=GROUP_NAME)
def cloud_registry_diff(cloud_registry_from_metadata: ConnectorRegistryV0, legacy_cloud_registry: ConnectorRegistryV0) -> dict:
    """
    Compares the cloud registry from the metadata with the latest OSS registry.
    """
    cloud_registry_from_metadata_dict = json.loads(cloud_registry_from_metadata.json())
    legacy_cloud_registry_dict = json.loads(legacy_cloud_registry.json())
    return diff_registries(legacy_cloud_registry_dict, cloud_registry_from_metadata_dict).to_dict()


@asset(group_name=GROUP_NAME)
def oss_registry_diff(oss_registry_from_metadata: ConnectorRegistryV0, legacy_oss_registry: ConnectorRegistryV0) -> dict:
    """
    Compares the OSS registry from the metadata with the latest OSS registry.
    """
    oss_registry_from_metadata_dict = json.loads(oss_registry_from_metadata.json())
    legacy_oss_registry_dict = json.loads(legacy_oss_registry.json())
    return diff_registries(legacy_oss_registry_dict, oss_registry_from_metadata_dict).to_dict()


@asset(group_name=GROUP_NAME)
def cloud_registry_diff_dataframe(cloud_registry_diff: dict) -> OutputDataFrame:
    diff_df = pd.DataFrame.from_dict(cloud_registry_diff)
    return output_dataframe(diff_df)


@asset(group_name=GROUP_NAME)
def oss_registry_diff_dataframe(oss_registry_diff: dict) -> OutputDataFrame:
    diff_df = pd.DataFrame.from_dict(oss_registry_diff)
    return output_dataframe(diff_df)


@asset(required_resource_keys={"latest_metadata_file_blobs"}, group_name=GROUP_NAME)
def metadata_directory_report(context: OpExecutionContext):
    latest_metadata_file_blobs = context.resources.latest_metadata_file_blobs
    blobs = [blob.name for blob in latest_metadata_file_blobs]
    blobs_df = pd.DataFrame(blobs)

    return output_dataframe(blobs_df)


@asset(required_resource_keys={"registry_report_directory_manager"}, group_name=GROUP_NAME)
def oss_registry_diff_report(context: OpExecutionContext, oss_registry_diff_dataframe: pd.DataFrame):
    markdown = oss_registry_diff_dataframe.to_markdown()

    registry_report_directory_manager = context.resources.registry_report_directory_manager
    file_handle = registry_report_directory_manager.write_data(markdown.encode(), ext="md", key="dev/oss_registry_diff_report")

    metadata = {
        "preview": MetadataValue.md(markdown),
        "gcs_path": MetadataValue.url(file_handle.gcs_path),
    }
    return Output(metadata=metadata, value=file_handle)


@asset(required_resource_keys={"registry_report_directory_manager"}, group_name=GROUP_NAME)
def cloud_registry_diff_report(context: OpExecutionContext, cloud_registry_diff_dataframe: pd.DataFrame):
    markdown = cloud_registry_diff_dataframe.to_markdown()

    registry_report_directory_manager = context.resources.registry_report_directory_manager
    file_handle = registry_report_directory_manager.write_data(markdown.encode(), ext="md", key="dev/cloud_registry_diff_report")

    metadata = {
        "preview": MetadataValue.md(markdown),
        "gcs_path": MetadataValue.url(file_handle.gcs_path),
    }
    return Output(metadata=metadata, value=file_handle)
