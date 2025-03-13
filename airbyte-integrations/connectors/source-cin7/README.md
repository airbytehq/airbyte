# Cin7
This directory contains the manifest-only connector for `source-cin7`.

This is the Cin7 source that ingests data from the Cin7 API.

Cin7 (Connector Inventory Performance), If you’re a business that wants to grow, you need an inventory solution you can count on - both now and in the future. With Cin7 you get a real-time picture of your products across systems, channels, marketplaces and regions, plus NEW ForesightAI advanced inventory forecasting that empowers you to see around corners and stay three steps ahead of demand! https://www.cin7.com/

To use this source, you must first create an account. Once logged in, head to Integrations -&gt; API -&gt; Cin7 Core API.
Create an application and note down the Account Id and the API key, you will need to enter these in the input fields. You can find more information about the API here https://dearinventory.docs.apiary.io/#reference


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
This will create a dev image (`source-cin7:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-cin7 build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-cin7 test
```

