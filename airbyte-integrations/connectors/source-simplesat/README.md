# Simplesat
This directory contains the manifest-only connector for `source-simplesat`.

This is the setup guide for the Simplesat source connector.
The Simplesat source connector which ingests data from the Simplesat API.
Simplesat is a engaging survey tool for service businesses to gather insight and feedback from their customers.

The source supports 3 of the endpoints from the API (questions, surveys and answers)
For more information, checkout the website https://www.simplesat.io/
  
An API key is required for authentication and using this connector.
In order to obtain an API key, you must first create a Simplesat account.
Once logged-in, you will find your API key in the account settings.
You can find more about their API here https://documenter.getpostman.com/view/457268/SVfRt7WJ?version=latest


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
This will create a dev image (`source-simplesat:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-simplesat build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-simplesat test
```

