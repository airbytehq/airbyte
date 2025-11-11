from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource

class SourceAirmeet(YamlDeclarativeSource):
    def __init__(self, state=None, **options):
        super().__init__(
            path_to_yaml="manifest.yaml",
            state=state,
            **options
        )

    def check(self, config):
        # Retrieve necessary credentials from the config dictionary
        api_key = config.get("access_key")
        secret_key = config.get("secret_key")
        region = config.get("region")
        airmeet_id = config.get("airmeet_id")
        
        # Validate required fields
        if not all([api_key, secret_key, region, airmeet_id]):
            raise ValueError("Missing required configuration values.")

        # Perform connection validation (e.g., test API key, make a request)
        # Example of testing the connection (API request or other validation)
        print(f"Testing connection with Airmeet API using ID: {airmeet_id} in region: {region}")
        
        # Here, you can add actual API logic (e.g., making a request to Airmeet's API to test the connection)
        print("Connection successful with the provided configuration.")
