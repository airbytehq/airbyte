# Building New Connectors

A connector takes the form of a Docker image which follows the [Airbyte specification](../../architecture/airbyte-specification.md).

We support 2 types of connectors: Sources and Destinations.  
To build a new connector, we provide templates so you don't need to start everything from scratch.

## The Airbyte specification

Before you can start building your own connector, you need to understand [Airbyte's data protocol specification](../../architecture/airbyte-specification.md).

## Creating a new connector

First, make sure you built the project by running

```text
./gradlew build
```

from the project root directory \(more details on [developing locally](../developing-locally.md)\).

Then, from the `airbyte-integrations/connector-templates/generator` directory, run:

```text
npm run generate
```

and follow the interactive prompt.

This will generate a new connector in the `airbyte-integrations/connectors/<your-connector>` directory.

Follow the instructions generated in the `CHECKLIST.md` file to bootstrap the connector.

The generated `README.md` will also contain instructions on how to iterate.

## Updating a connector

Once you've finished iterating on the changes to a connector as specified in its `README.md`, follow these instructions to tell Airbyte to use the latest version of your connector.

1. Bump the version in the `Dockerfile` of the connector \(`LABEL io.airbyte.version=X.X.X`\).
2. Update the connector version in:
   * `STANDARD_SOURCE_DEFINITION` if it is a source
   * `STANDARD_DESTINATION_DEFINITION` if it is a destination.
3. Build the connector with the semantic version tag locally:

   ```text
   ./tools/integrations/manage.sh build airbyte-integrations/connectors/<connector-name>
   ```

4. Submit a PR containing the changes you made.
5. One of Airbyte maintainers will review the change and publish the new version of the connector do Docker hub:

   ```text
   ./tools/integrations/manage.sh publish airbyte-integrations/connectors/<connector-name>
   ```

6. The new version of the connector is now available for everyone who uses it. Thank you!

