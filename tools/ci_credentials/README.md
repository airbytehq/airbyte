# CI Credentials

Connects to GSM to download connection details.

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

I found it necessary to change this code: `base_folder = Path("/actions-runner/_work/airbyte/airbyte")`
to something more local like: `base_folder = Path("/Users/brian/airbytehq/airbyte")`

I assume this is because that's the place the GitHub actions is doing its work.

After making a change, you have to reinstall it to run the bash command: `pip install --quiet -e ./tools/ci_*`

## Run it

Pass in a connector name. For example:

```bash
ci_credentials destination-snowflake
```