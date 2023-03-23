import yaml
from dagster import Output, asset

GROUP_NAME = "dev"

OVERRIDES = {
  # airbyte/source-freshcaller
  "8a5d48f6-03bb-4038-a942-a8d3f175cca3": {
    "connectionType": "api",
    "releaseStage": "alpha"
  },
  # airbyte/source-genesys
  "5ea4459a-8f1a-452a-830f-a65c38cc438d": {
    "connectionType": "api",
    "releaseStage": "alpha"
  },
  # airbyte/source-rss
  "0efee448-6948-49e2-b786-17db50647908": {
    "connectionType": "api",
    "releaseStage": "alpha"
  },
  # airbyte/destination-azure-blob-storage
  "b4c5d105-31fd-4817-96b6-cb923bfc04cb": {
    "connectionType": "file"
  },
  # airbyte/destination-amazon-sqs
  "0eeee7fb-518f-4045-bacc-9619e31c43ea": {
    "connectionType": "api"
  },
  # airbyte/destination-doris
  "05c161bf-ca73-4d48-b524-d392be417002": {
    "connectionType": "database"
  },
  # airbyte/destination-iceberg
  "df65a8f3-9908-451b-aa9b-445462803560": {
    "connectionType": "database"
  },
  # airbyte/destination-aws-datalake
  "99878c90-0fbd-46d3-9d98-ffde879d17fc": {
    "connectionType": "database"
  },
  # airbyte/destination-bigquery
  "22f6c74f-5699-40ff-833c-4a879ea40133": {
    "connectionType": "database"
  },
  # airbyte/destination-bigquery-denormalized
  "079d5540-f236-4294-ba7c-ade8fd918496": {
    "connectionType": "database"
  },
  # airbyte/destination-cassandra
  "707456df-6f4f-4ced-b5c6-03f73bcad1c5": {
    "connectionType": "database"
  },
  # airbyte/destination-keen
  "81740ce8-d764-4ea7-94df-16bb41de36ae": {
    "connectionType": "api"
  },
  # airbyte/destination-clickhouse
  "ce0d828e-1dc4-496c-b122-2da42e637e48": {
    "connectionType": "database"
  },
  # airbyte/destination-r2
  "0fb07be9-7c3b-4336-850d-5efc006152ee": {
    "connectionType": "file"
  },
  # airbyte/destination-databricks
  "072d5540-f236-4294-ba7c-ade8fd918496": {
    "connectionType": "database"
  },
  # airbyte/destination-dynamodb
  "8ccd8909-4e99-4141-b48d-4984b70b2d89": {
    "connectionType": "database"
  },
  # airbyte/destination-e2e-test
  "2eb65e87-983a-4fd7-b3e3-9d9dc6eb8537": {
    "connectionType": "unknown",
    "releaseStage": "alpha"
  },
  # airbyte/destination-elasticsearch
  "68f351a7-2745-4bef-ad7f-996b8e51bb8c": {
    "connectionType": "api"
  },
  # airbyte/destination-exasol
  "bb6071d9-6f34-4766-bec2-d1d4ed81a653": {
    "connectionType": "database"
  },
  # airbyte/destination-firebolt
  "18081484-02a5-4662-8dba-b270b582f321": {
    "connectionType": "database"
  },
  # airbyte/destination-gcs
  "ca8f6566-e555-4b40-943a-545bf123117a": {
    "connectionType": "file"
  },
  # airbyte/destination-firestore
  "27dc7500-6d1b-40b1-8b07-e2f2aea3c9f4": {
    "connectionType": "database"
  },
  # airbyte/destination-pubsub
  "356668e2-7e34-47f3-a3b0-67a8a481b692": {
    "connectionType": "api"
  },
  # airbyte/destination-kafka
  "9f760101-60ae-462f-9ee6-b7a9dafd454d": {
    "connectionType": "database"
  },
  # airbyte/destination-kinesis
  "6d1d66d4-26ab-4602-8d32-f85894b04955": {
    "connectionType": "api"
  },
  # airbyte/destination-csv
  "8be1cf83-fde1-477f-a4ad-318d23c9f3c6": {
    "connectionType": "file"
  },
  # airbyte/destination-local-json
  "a625d593-bba5-4a1c-a53d-2d246268a816": {
    "connectionType": "file"
  },
  # airbyte/destination-mqtt
  "f3802bc4-5406-4752-9e8d-01e504ca8194": {
    "connectionType": "message_queue"
  },
  # airbyte/destination-mssql
  "d4353156-9217-4cad-8dd7-c108fd4f74cf": {
    "connectionType": "database"
  },
  # airbyte/destination-meilisearch
  "af7c921e-5892-4ff2-b6c1-4a5ab258fb7e": {
    "connectionType": "api"
  },
  # airbyte/destination-mongodb
  "8b746512-8c2e-6ac1-4adc-b59faafd473c": {
    "connectionType": "database"
  },
  # airbyte/destination-mysql
  "ca81ee7c-3163-4246-af40-094cc31e5e42": {
    "connectionType": "database"
  },
  # airbyte/destination-oracle
  "3986776d-2319-4de9-8af8-db14c0996e72": {
    "connectionType": "database"
  },
  # airbyte/destination-postgres
  "25c5221d-dce2-4163-ade9-739ef790f503": {
    "connectionType": "database"
  },
  # airbyte/destination-pulsar
  "2340cbba-358e-11ec-8d3d-0242ac130203": {
    "connectionType": "database"
  },
  # airbyte/destination-rabbitmq
  "e06ad785-ad6f-4647-b2e8-3027a5c59454": {
    "connectionType": "database"
  },
  # airbyte/destination-redis
  "d4d3fef9-e319-45c2-881a-bd02ce44cc9f": {
    "connectionType": "database"
  },
  # airbyte/destination-redshift
  "f7a7d195-377f-cf5b-70a5-be6b819019dc": {
    "connectionType": "database"
  },
  # airbyte/destination-redpanda
  "825c5ee3-ed9a-4dd1-a2b6-79ed722f7b13": {
    "connectionType": "database"
  },
  # airbyte/destination-rockset
  "2c9d93a7-9a17-4789-9de9-f46f0097eb70": {
    "connectionType": "database"
  },
  # airbyte/destination-s3
  "4816b78f-1489-44c1-9060-4b19d5fa9362": {
    "connectionType": "file"
  },
  # airbyte/destination-s3-glue
  "471e5cab-8ed1-49f3-ba11-79c687784737": {
    "connectionType": "file"
  },
  # airbyte/destination-sftp-json
  "e9810f61-4bab-46d2-bb22-edfc902e0644": {
    "connectionType": "file"
  },
  # airbyte/destination-snowflake
  "424892c4-daac-4491-b35d-c6688ba547ba": {
    "connectionType": "database"
  },
  # airbyte/destination-mariadb-columnstore
  "294a4790-429b-40ae-9516-49826b9702e1": {
    "connectionType": "database"
  },
  # ghcr.io/devmate-cloud/streamr-airbyte-connectors
  "eebd85cf-60b2-4af6-9ba0-edeca01437b0": {
    "connectionType": "api"
  },
  # airbyte/destination-scylla
  "3dc6f384-cd6b-4be3-ad16-a41450899bf0": {
    "connectionType": "database"
  },
  # airbyte/destination-google-sheets
  "a4cbd2d1-8dbe-4818-b8bc-b90ad782d12a": {
    "connectionType": "api"
  },
  # airbyte/destination-sqlite
  "b76be0a6-27dc-4560-95f6-2623da0bd7b6": {
    "connectionType": "database"
  },
  # airbyte/destination-tidb
  "06ec60c7-7468-45c0-91ac-174f6e1a788b": {
    "connectionType": "database"
  },
  # airbyte/destination-typesense
  "36be8dc6-9851-49af-b776-9d4c30e4ab6a": {
    "connectionType": "database"
  },
  # airbyte/destination-yugabytedb
  "2300fdcf-a532-419f-9f24-a014336e7966": {
    "connectionType": "database"
  },
  # airbyte/destination-databend
  "302e4d8e-08d3-4098-acd4-ac67ca365b88": {
    "connectionType": "database"
  },
  # airbyte/destination-teradata
  "58e6f9da-904e-11ed-a1eb-0242ac120002": {
    "connectionType": "database"
  },
  # airbyte/destination-weaviate
  "7b7d7a0d-954c-45a0-bcfc-39a634b97736": {
    "connectionType": "database"
  },
  # airbyte/destination-duckdb
  "94bd199c-2ff0-4aa2-b98e-17f0acb72610": {
    "connectionType": "database"
  },
  # airbyte/destination-dev-null
  "a7bcc9d8-13b3-4e49-b80d-d020b90045e3": {
    "connectionType": "file"
  }
}


@asset(group_name=GROUP_NAME)
def overrode_metadata_definitions(catalog_derived_metadata_definitions):
    overrode_definition = []
    for metadata_definition in catalog_derived_metadata_definitions:
        definition_id = metadata_definition["data"]["definitionId"]
        if definition_id in OVERRIDES:
            metadata_definition["data"].update(OVERRIDES[definition_id])
        overrode_definition.append(metadata_definition)

    return overrode_definition

@asset(required_resource_keys={"metadata_file_directory"}, group_name=GROUP_NAME)
def persist_metadata_definitions(context, overrode_metadata_definitions):
    files = []
    for metadata in overrode_metadata_definitions:
        connector_dir_name = metadata["data"]["dockerRepository"].replace("airbyte/", "")
        definitionId = metadata["data"]["definitionId"]

        key = f"{connector_dir_name}-{definitionId}"

        yaml_string = yaml.dump(metadata)

        file = context.resources.metadata_file_directory.write_data(yaml_string.encode(), ext="yaml", key=key)
        files.append(file)

    file_paths = [file.path for file in files]
    file_paths_str = "\n".join(file_paths)

    return Output(files, metadata={"count": len(files), "file_paths": file_paths_str})
