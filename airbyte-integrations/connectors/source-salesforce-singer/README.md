# Salesforce Test Configuration

This integration wraps the existing singer [tap-salesforce](https://github.com/singer-io/tap-salesforce). In order to test the Salesforce source, you will need a Salesforce account and appropriate OAuth creds. For more information on how to obtain these, check out the [docs](https://docs.airbyte.io/integrations/destinations/salesforce).

## Community Contributor

1. Create a file at `secrets/config.json` with the following format using your client secret and account id:
```
{
  "client_id": "<Consume Key in your Salesforce app>",
  "client_secret": "<Consumer Secret in your Salesforce app>",
  "refresh_token": "<refresh token, follow instruction in our docs to obtain it from your existing Salesforce app>",
  "start_date": "2020-01-02T00:00:00Z",
  "is_sandbox": false,
  "api_type": "BULK"
}
```

## Airbyte Employee

1. Access the `salesforce-integration-test-config` secret note on Rippling under the `Engineering` folder. It contains the full json for the `config.json`.

