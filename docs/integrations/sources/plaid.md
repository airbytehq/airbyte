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

To set up the Plaid Source connector in Airbyte:

### Requirements

- Plaid Account \(with client_id and API key\)
- Access Token

### Generating API Keys

You can find your Plaid API keys on the Plaid dashboard. Follow these steps to generate them:

1. **Create a Plaid account** Go to the [plaid website](https://plaid.com/) and click "Get API Keys". Follow the instructions to create an account.

2. **Generate Client id and API key** Go to the [keys page](https://dashboard.plaid.com/team/keys) where you will find the client id and your Sandbox API Key \(in the UI this key is just called "Sandbox"\).

3. **Create an Access Token** Before you create an access token, you need to create a public key. Make an API call to generate a public key by running the following command in your terminal or command-line interface:

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

    This will return a JSON object that includes a `public_token`. Save this `public_token` as you will need it to generate the access token in the next step.

4. **Exchange public key for access token** Using your `public_token` from the previous step, request an access token by running the following command:

    ```bash
    curl --location --request POST 'https://sandbox.plaid.com/item/public_token/exchange' \
      --header 'Content-Type: application/json;charset=UTF-16' \
      --data-raw '{
          "client_id": "<your-client-id>",
          "secret": "<your-sandbox-api-key>",
          "public_token": "<public-token>"
      }'
    ```

   This will return a JSON object that includes an `access_token`. Save this `access_token` as you will need it to set up the Plaid Source connector in Airbyte.

### Configuring the Plaid Source connector in Airbyte

1. Open the Plaid Source connector configuration form in Airbyte.

2. Enter the `access_token`, `api_key`, `client_id`, and `plaid_env` in the fields as follows:
        
    - `access_token` is the access token you generated in step 4 of the previous section.
    - `api_key` is the API key you generated in step 2 of the previous section.
    - `client_id` is the client ID you generated in step 2 of the previous section.
    - `plaid_env` is the Plaid environment you are using (options are sandbox, development, or production).

3. If you wish, you can also set the `start_date` field if you want to replicate data starting from a specific date. The date should be formatted as YYYY-MM-DD.

4. Click "Test connection" to verify that the connection to the Plaid Source is working correctly.

5. Click "Save" to save your configuration.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                       |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------ |
| 0.3.2   | 2022-08-02 | [15231](https://github.com/airbytehq/airbyte/pull/15231) | Added min_last_updated_datetime support for Capital One items |
| 0.3.1   | 2022-03-31 | [11104](https://github.com/airbytehq/airbyte/pull/11104) | Fix 100 record limit and added start_date                     |
| 0.3.0   | 2022-01-05 | [7977](https://github.com/airbytehq/airbyte/pull/7977)   | Migrate to Python CDK + add transaction stream                |