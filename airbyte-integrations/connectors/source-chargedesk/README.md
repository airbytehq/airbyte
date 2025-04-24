# Chargedesk
This directory contains the manifest-only connector for `source-chargedesk`.

This is the setup for the Chargedesk source that ingests data from the chargedesk API.

ChargeDesk integrates directly with many of the most popular payment gateways including Stripe, WooCommerce, PayPal, Braintree Payments, Recurly, Authorize.Net, Zuora &amp; Shopify https://chargedesk.com/

In order to use this source, you must first create an account. Once verified and logged in, head over to Setup -&gt; API &amp; Webhooks -&gt; Issue New Key to generate your API key.

You can find more about the API here https://chargedesk.com/api-docs

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
This will create a dev image (`source-chargedesk:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-chargedesk build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-chargedesk test
```

