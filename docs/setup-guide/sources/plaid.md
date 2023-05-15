# Plaid

This page contains the setup guide and reference information for Plaid.

## Prerequisites
* Plaid API key
* Client ID
* Access token

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

## Setup guide

### Step 1: Obtain Plaid setup details

1. **Visit your [Plaid dashboard](https://dashboard.plaid.com/overview):** Click **Keys** from the **Team Settings** dropdown.
![Plaid Keys](../../.gitbook/assets/plaid-keys.jpg "Plaid Keys")

2. **Get Client id and API key:** On the Keys page, copy your **client_id** and Sandbox **secret**.
![Plaid Client Id Secret](../../.gitbook/assets/plaid-client-id-secret.jpg "Plaid Client Id Secret")

3. **Create an Access Token:** First you have to create a public token key and then you can create an access token.

* **Create public key:** Make this API call described in [Plaid docs](https://plaid.com/docs/api/sandbox/#sandboxpublic_tokencreate)
```
curl --location --request POST 'https://sandbox.plaid.com/sandbox/public_token/create' \
  --header 'Content-Type: application/json;charset=UTF-16' \
  --data-raw '{
      "client_id": "<your-client-id>",
      "secret": "<your-sandbox-api-key>",
      "institution_id": "ins_43",
      "initial_products": ["auth", "transactions"]
  }'
```

* **Exchange public key for access token:** Make this API call described in [Plaid docs](https://plaid.com/docs/api/tokens/#itempublic_tokenexchange). The public token used in this request, is the token returned in the response of the previous request.
```
curl --location --request POST 'https://sandbox.plaid.com/item/public_token/exchange' \
  --header 'Content-Type: application/json;charset=UTF-16' \
  --data-raw '{
      "client_id": "<your-client-id>",
      "secret": "<your-sandbox-api-key>",
      "public_token": "<public-token-returned-by-previous-request>"
  }'
```

4. You're ready to set up Plaid in Daspire!

### Step 2: Set up Plaid in Daspire

1. Select **Plaid** from the Source list.

2. Enter a **Source Name**.

3. Enter your Plaid **API key**.

4. Enter your Plaid **Client ID**.

5. Select your Plaid environment from **sandbox**, **development**, or **production**.

6. Enter your Plaid **Access Token**.

7. Click **Save & Test**.

## Supported streams

This source is capable of syncing the following streams:

* [Balance](https://plaid.com/docs/api/products/#balance)

## Performance considerations

The Plaid connector should not run into Stripe API limitations under normal usage. Please [contact us](mailto:support@daspire.com) if you see any rate limit issues that are not automatically retried successfully.

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.