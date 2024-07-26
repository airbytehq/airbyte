from airbyte_cdk.models.airbyte_protocol import AirbyteStream, SyncMode, DestinationSyncMode, AirbyteRecordMessage, \
    ConfiguredAirbyteStream

from destination_palantir_foundry.config.foundry_config import FoundryConfig, ClientCredentialsAuth, DestinationConfig, \
    FoundryStreamsMaterializationMode
from destination_palantir_foundry.foundry_api.stream_catalog import CreateStreamOrViewResponse, StreamView, \
    GetStreamResponse, \
    StreamSettings, MaybeGetStreamResponse
from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema, StringFieldSchema

FOUNDRY_HOST = "acme.palantirfoundry.com"
CLIENT_ID = "testclientid"
CLIENT_SECRET = "testclientsecret"

PROJECT_RID = "ri.compass..folder.id"

FOUNDRY_STREAMS_MATERIALIZATION_MODE = FoundryStreamsMaterializationMode(instance="foundry_streams")

FOUNDRY_CONFIG = FoundryConfig(
    host=FOUNDRY_HOST,
    auth=ClientCredentialsAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    ),
    destination_config=DestinationConfig(
        project_rid=PROJECT_RID,
        materialization_mode=FOUNDRY_STREAMS_MATERIALIZATION_MODE
    )
)

DATASET_RID = "ri.foundry.main.dataset.id1"

VIEW_RID = "ri.foundry.main.view.id1"
TOPIC_RID = "ri.foundry-streaming..topic.id1"
TRANSACTION_RID = "ri.foundry.main.transaction.id1"

BRANCH_MASTER = "master"

STREAM_VIEW = StreamView(
    viewRid=VIEW_RID,
    datasetRid=DATASET_RID,
    branch=BRANCH_MASTER,
    topicRid=TOPIC_RID,
    startTransactionRid=TRANSACTION_RID,
    isRaw=True
)

CREATE_STREAM_OR_VIEW_RESPONSE = CreateStreamOrViewResponse(view=STREAM_VIEW)

STREAM_SETTINGS = StreamSettings(
    partitions=1,
    streamTypes=["HIGH_THROUGHPUT"]
)

GET_STREAM_RESPONSE = MaybeGetStreamResponse(GetStreamResponse(view=STREAM_VIEW, streamSettings=STREAM_SETTINGS))

NAMESPACE = "test-namespace"
STREAM_NAME = "test-stream-name"

EMPTY_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object"
}

MINIMAL_AIRBYTE_STREAM = AirbyteStream(
    name=STREAM_NAME,
    json_schema=EMPTY_JSON_SCHEMA,
    namespace=NAMESPACE,
    supported_sync_modes=[SyncMode.incremental],
)

MINIMAL_CONFIGURED_AIRBYTE_STREAM = ConfiguredAirbyteStream(
    stream=MINIMAL_AIRBYTE_STREAM,
    sync_mode=SyncMode.incremental,
    destination_sync_mode=DestinationSyncMode.append,
)

MINIMAL_AIRBYTE_RECORD_MESSAGE = AirbyteRecordMessage(
    namespace=NAMESPACE,
    stream=STREAM_NAME,
    data={"test": "test"},
    emitted_at=0
)

FOUNDRY_SCHEMA = FoundrySchema(
    fieldSchemaList=[StringFieldSchema(name="test", nullable=False)],
    dataFrameReaderClass="",
    customMetadata={}
)
