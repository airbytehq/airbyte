# Sigma Computing
This directory contains the manifest-only connector for `source-sigma-computing`.

This is the setup for the Sigma Computing source that ingests data from the sigma API. 

Sigma is next-generation analytics and business intelligence that scales billions of records using spreadsheets, SQL, Python, or AI—without compromising speed and security https://www.sigmacomputing.com/

In order to use this source, you must first create an account on Sigma Computing. Go to Account &gt; General Settings and review the Site section for the Cloud provider, this will be used to find the base url of your API. Compare it at https://help.sigmacomputing.com/reference/get-started-sigma-api

Next, head over to Developer Access and click on create. This will generate your Client ID and Client Secret required by the API. You can learn more about the API here https://help.sigmacomputing.com/reference


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
This will create a dev image (`source-sigma-computing:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-sigma-computing build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-sigma-computing test
```

