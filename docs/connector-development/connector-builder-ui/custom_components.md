# Custom components
Most low-code components can be overloaded with a custom Python class. See the [low-code's advanced section on custom components
for more details](../config-based/advanced-topics.md#custom-components).

Custom components cannot be directly edited in the builder, but the OSS docker-compose deployment of the builder application can load them dynamically from your local filesystem.

:::warning 
Connectors using custom components cannot be directly exported to your workspace. You'll need to create a custom connector, build a docker image, and upload it to the platform by [following these instructions](https://docs.airbyte.com/integrations/custom-connectors#adding-your-connectors-in-the-ui).
:::

Here's how you can do it:

1. Run the OSS platform locally with builder docker-compose extension
    1. Example command: PATH_TO_CONNECTORS=/Users/alex/code/airbyte/airbyte-integrations/connectors docker compose -f docker-compose.yaml -f docker-compose.builder.yaml up
    2. Where PATH_TO_CONNECTORS points to the airbyte-integrations/connectors subdirectory in the opensource airbyte repository
2. Open the connector builder and develop your connector
3. When needing a custom componentt:
    1. Switch to the YAML view
    2. Define the custom component
4. Write the custom components and its unit tests
5. Run test read

Follow these additional instructions if the connector requires 3rd party libraries that are not available in the CDK:

Developing connectors that require 3rd party libraries can be done by running the connector-builder-server locally and pointing to a custom virtual environment.

From the [airbyte-platform repository](https://github.com/airbytehq/airbyte-platform):
1. Create a virtual environment and install the CDK + any 3rd party library required
2. export CDK_PYTHON=<path_to_virtual_environment>
3. export CDK_ENTRYPOINT=<path_to_CDK_connector_builder_main.py>
4. ./gradlew -p oss airbyte-connector-builder-server:run
    1. The server is now reachable on localhost:80
5. Update the server to point to port 80 by editing .env and replacing
    
    CONNECTOR_BUILDER_SERVER_API_HOST=[http://airbyte-connector-builder-server:80](http://airbyte-connector-builder-server/)WithCONNECTOR_BUILDER_SERVER_API_HOST=[http://host.docker.internal:80](http://host.docker.internal/)
    
6. Follow the standard instructions
