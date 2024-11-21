# Revolut Merchant
This directory contains the manifest-only connector for `source-revolut-merchant`.

This is the Revolut Merchant source that ingests data from the Revolut Merchant API.

Revolut helps you spend, send, and save smarter https://www.revolut.com/

The Revolut Merchant account is a sub-account of your Revolut Business account. While a Business account is for managing your business finances, the Merchant account is dedicated to helping you accept online payments from your e-commerce customers.

This source uses the Merchant API and has the orders, customers and location endpoints. In order to use this API, you must first create a Revolut account. 
Log in to your Revolut Business account: Access the Revolut Business log in page and enter your credentials.
Navigate to Merchant API settings: Once logged in, access the Merchant API settings page by clicking your profile icon in the top left corner, then selecting APIs &gt; Merchant API. 
Here you can access your Production API keys (Public, Secret) specific to your Merchant account.
Get API keys: If you&#39;re visiting this page for the first time, you&#39;ll need to initiate the process by clicking the Get started button. To generate your Production API Secret key, click the Generate button.
You can find more about the API here https://developer.revolut.com/docs/merchant/merchant-api

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
This will create a dev image (`source-revolut-merchant:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-revolut-merchant build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-revolut-merchant test
```

