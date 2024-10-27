# Deputy
This directory contains the manifest-only connector for `source-deputy`.

This is the Deputy source that ingests data from the Deputy API.

Deputy is a software that simplifies employee scheduling, timesheets and HR in one place https://www.deputy.com/

In order to use this source you must first create an account on Deputy.
Once logged in, your Deputy install will have a specific URL in the structure of https://{installname}.{geo}.deputy.com - This is the same URL that will be the base API url .

To obtain your bearer token to use the API, follow the steps shown here https://developer.deputy.com/deputy-docs/docs/the-hello-world-of-deputy
This will have you create an oauth application and create an access token. Enter the access token in the input field.

You can learn more about the API here https://developer.deputy.com/deputy-docs/reference/getlocations

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
This will create a dev image (`source-deputy:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-deputy build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-deputy test
```

