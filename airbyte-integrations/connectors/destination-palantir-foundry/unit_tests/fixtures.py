from destination_palantir_foundry.config.foundry_config import FoundryConfig, ClientCredentialsAuth, DestinationConfig
from destination_palantir_foundry.foundry_api.stream_catalog import CreateStreamOrViewResponse, StreamView

FOUNDRY_HOST = "acme.palantirfoundry.com"
CLIENT_ID = "testclientid"
CLIENT_SECRET = "testclientsecret"

PROJECT_RID = "ri.compass..folder.id"

FOUNDRY_CONFIG = FoundryConfig(
    host=FOUNDRY_HOST,
    auth=ClientCredentialsAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    ),
    destination_config=DestinationConfig(
        project_rid=PROJECT_RID
    )
)

NAMESPACE = "test-namespace"
STREAM_NAME = "test-stream-name"

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
