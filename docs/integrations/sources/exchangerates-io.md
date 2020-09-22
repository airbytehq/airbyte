# exchangerates.io

## Overview

The exchange rates integration is a toy integration to demonstrate how Airbyte works with a very simple source.

#### Output schema

One stream is available Several output streams are available from this source \(customers, charges, invoices, subscriptions, etc.\) For a comprehensive output schema [look at the Singer tap schema files](https://github.com/singer-io/tap-stripe/tree/master/tap_stripe/schemas).

#### Data type mapping

This source casts fields from the [Stripe API](https://stripe.com/docs/api) into types [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types such as `string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`.

#### Features

This section should contain a table with the following format:

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

#### Performance considerations

The Stripe connector should not run into Stripe API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

### Getting started

#### Requirements

* Stripe Account
* Stripe API Secret Key

#### Setup guide

Visit the [Stripe API Keys page](https://dashboard.stripe.com/apikeys) in the Stripe dashboard to access the secret key for your account. Secret keys for the live Stripe environment will be prefixed with `sk_live_`or `rk_live`.

We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access. For ease of use, we recommend using read permissions for all resources and configuring which resource to replicate in the Airbyte UI.

If you would like to test Airbyte using test data on Stripe, `sk_test_` and `rk_test_` API keys are also supported.

