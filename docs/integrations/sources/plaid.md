# Plaid

## Overview

The Plaid source supports Full Refresh syncs. It currently only supports pulling from the balances endpoint. It will soon support other data streams \(e.g. transactions\).

### Output schema

Output streams:

- [Balance](https://plaid.com/docs/api/products/#balance)

### Features

| Feature                       | Supported?  |
| :---------------------------- | :---------- |
| Full Refresh Sync             | Yes         |
| Incremental - Append Sync     | Coming soon |
| Replicate Incremental Deletes | Coming soon |
| SSL connection                | Yes         |
| Namespaces                    | No          |

### Performance considerations

The Plaid connector should not run into Stripe API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Plaid Account \(with client_id and API key\)
- Access Token

### Setup guide for Sandbox

This guide will walk through how to create the credentials you need to run this source in the sandbox of a new plaid account. For production use, consider using the Link functionality that Plaid provides [here](https://plaid.com/docs/api/tokens/#linktokencreate)

- **Create a Plaid account** Go to the [plaid website](https://plaid.com/) and click "Get API Keys". Follow the instructions to create an account.
- **Get Client id and API key** Go to the [keys page](https://dashboard.plaid.com/team/keys) where you will find the client id and your Sandbox API Key \(in the UI this key is just called "Sandbox"\).
- **Create an Access Token** First you have to create a public token key and then you can create an access token.

  - **Create public key** Make this API call described in [plaid docs](https://plaid.com/docs/api/sandbox/#sandboxpublic_tokencreate)

    ```bash
      curl --location --request POST 'https://sandbox.plaid.com/sandbox/public_token/create' \
          --header 'Content-Type: application/json;charset=UTF-16' \
          --data-raw '{
              "client_id": "<your-client-id>",
              "secret": "<your-sandbox-api-key>",
              "institution_id": "ins_43",
              "initial_products": ["auth", "transactions"]
          }'
    ```

  - **Exchange public key for access token** Make this API call described in [plaid docs](https://plaid.com/docs/api/tokens/#itempublic_tokenexchange). The public token used in this request, is the token returned in the response of the previous request. This request will return an `access_token`, which is the last field we need to generate for the config for this source!

    ```bash
    curl --location --request POST 'https://sandbox.plaid.com/item/public_token/exchange' \
      --header 'Content-Type: application/json;charset=UTF-16' \
      --data-raw '{
          "client_id": "<your-client-id>",
          "secret": "<your-sandbox-api-key>",
          "public_token": "<public-token-returned-by-previous-request>"
      }'
    ```

- We should now have everything we need to configure this source in the UI.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                       |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------ |
| 0.3.2   | 2022-08-02 | [15231](https://github.com/airbytehq/airbyte/pull/15231) | Added min_last_updated_datetime support for Capital One items |
| 0.3.1   | 2022-03-31 | [11104](https://github.com/airbytehq/airbyte/pull/11104) | Fix 100 record limit and added start_date                     |
| 0.3.0   | 2022-01-05 | [7977](https://github.com/airbytehq/airbyte/pull/7977)   | Migrate to Python CDK + add transaction stream                |
