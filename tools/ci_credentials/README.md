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

After making a change, you have to reinstall it to run the bash command: `pip install --quiet -e ./tools/ci_*`

## Run it

The `VERSION=dev` will make it so it knows to use your local current working directory and not the Github Action one.

Pass in a connector name. For example:

```bash
VERSION=dev ci_credentials destination-snowflake
```

To make sure it get's all changes every time, you can run this:

```bash
pip install --quiet -e ./tools/ci_* && VERSION=dev ci_credentials destination-snowflake
```