# Opinion Stage
This directory contains the manifest-only connector for `source-opinion-stage`.

The Airbyte connector for [OpinionStage](https://opinionstage.com) enables seamless data integration from the OpinionStage platform, facilitating the extraction of interactive content data. It streams data from items such as forms, quizzes, and polls, as well as capturing responses and specific questions associated with each item. This connector is ideal for users looking to analyze audience engagement, response patterns, and question insights from OpinionStage in their data workflows.

## Usage
There are multiple ways to use this connector:
- You can use this connector as any other connector in Airbyte Marketplace.
- You can load this connector in `pyairbyte` using `get_source`!
- You can open this connector in Connector Builder, edit it, and publish to your workspaces.

Please refer to the manifest-only connector documentation for more details.

## Local Development
We recommend you use the Connector Builder to edit this connector.

But, if you want to develop this connector locally, you can use the following steps.

### Environment Setup
You will need `airbyte-ci` installed. You can find the documentation [here](airbyte-ci).

### Build
This will create a dev image (`source-opinion-stage:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-opinion-stage build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-opinion-stage test
```

