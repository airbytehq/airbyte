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

```bash
export GCP_GSM_CREDENTIALS=`cat ~/Downloads/key.json`
```

After making a change, you have to reinstall it to run the bash command: `pip install --quiet -e ./tools/ci_*`

## Run it

The `VERSION=dev` will make it so it knows to use your local current working directory and not the Github Action one.


### Help
```bash
ci_credentials --help
```

### Write to storage
To download GSM secrets to `airbyte-integrations/connectors/source-bings-ads/secrets`:
```bash
ci_credentials source-bing-ads write-to-storage
```

### Update secrets
To upload to GSM newly updated configurations from `airbyte-integrations/connectors/source-bings-ads/secrets/updated_configurations`:

```bash
ci_credentials source-bing-ads update-secrets
```

