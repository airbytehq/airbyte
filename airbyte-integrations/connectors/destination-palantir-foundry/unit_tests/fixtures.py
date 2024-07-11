from destination_palantir_foundry.config.foundry_config import FoundryConfig, ClientCredentialsAuth, DestinationConfig

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
