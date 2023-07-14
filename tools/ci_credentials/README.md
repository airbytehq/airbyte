# CI Credentials
CLI tooling to read and manage GSM secrets:
- `write-to-storage` download a connector's secrets locally in the connector's `secret` folder
- `update-secrets` uploads new connector secret version that were locally updated.


## Development

Set up the world the same way Google Actions does it in `test-command.yml`.

```
source venv/bin/activate
pip install --quiet tox==3.24.4
tox -r -c ./tools/tox_ci.ini
pip install --quiet -e ./tools/ci_*
```

Download a Service account json key that has access to Google Secrets Manager.

### Create Service Account
* Go to https://console.cloud.google.com/iam-admin/serviceaccounts/create?project=dataline-integration-testing
* In step #1 `Service account details`, set a name and a relevant description
* In step #2 `Grant this service account access to project`, select role `Owner` (there is a role that is more scope but I based this decision on others `<user>-testing` service account)

### Create Service Account Token
* Go to https://console.cloud.google.com/iam-admin/serviceaccounts?project=dataline-integration-testing
* Find your service account and click on it
* Go in the tab "KEYS"
* Click on "ADD KEY -> Create new key" and select JSON. This will download a file on your computer

### Setup ci_credentials
* In your .zshrc, add: `export GCP_GSM_CREDENTIALS=$(cat <path to JSON file>)`
* Follow README.md under `tools/ci_credentials`

After making a change, you have to reinstall it to run the bash command: `pip install --quiet -e ./tools/ci_*`

## Run it

The `VERSION=dev` will make it so it knows to use your local current working directory and not the Github Action one.

### Help
```bash
ci_credentials --help
```

### Write credentials for a specific connector to local storage
To download GSM secrets to `airbyte-integrations/connectors/source-bings-ads/secrets`:
```bash
ci_credentials source-bing-ads write-to-storage
```

### Write credentials for all connectors to local storage
To download GSM secrets to for all available connectors into their respective `secrets` directories:
```bash
ci_credentials all write-to-storage
```

### Update secrets
To upload to GSM newly updated configurations from `airbyte-integrations/connectors/source-bings-ads/secrets/updated_configurations`:

```bash
ci_credentials source-bing-ads update-secrets
```

