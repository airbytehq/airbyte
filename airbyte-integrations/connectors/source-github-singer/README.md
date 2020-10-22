# Github Test Configuration

This integration wraps the existing singer [tap-github](https://github.com/singer-io/tap-github). In order to test the Github source, you will need an access_key key from github. You can generate one by logging into github and then creating a personal access token [here](https://github.com/settings/tokens).

## Community Contributor

1. Create a file at `secrets/config.json` with the following format using your client secret and account id:
```
{
  "access_key": "<the access key that you generated above>",
  "respository": "airbytehq/airbyte singer-io/tap-github",
}
```

## Airbyte Employee

1. Access the `source-github-singer-access-token` secret on Rippling under the `Engineering` folder
1. Using `jq` inject the access token into the config. `jq .access_token=$GH_ACCESS_TOKEN airbyte-integrations/connectors/source-github-singer/config.sample.json > airbyte-integrations/connectors/source-github-singer/secrets/config.json`

