# CI Credentials
CLI tooling to read and manage GSM secrets:
- `write-to-storage` download a connector's secrets locally in the connector's `secret` folder
- `update-secrets` uploads new connector secret version that were locally updated.

## Requirements

This project requires Python 3.10 and pipx.

## Installation

The recommended way to install `ci_credentials` is using pipx. This ensures the tool and its dependencies are isolated from your other Python projects.

If you haven't installed pipx, you can do it with pip:

```bash
python -m pip install --user pipx
python -m pipx ensurepath
```

Once pipx is installed, navigate to the root directory of the project, then run:

```bash
pipx install airbyte-ci/connectors/ci_credentials/
```

This command installs ci_credentials and makes it globally available in your terminal.

## Get GSM access
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

## Development
During development, you can use the `--editable` option to make changes to the `ci_credentials` package and have them immediately take effect without needing to reinstall the package:

```bash
pipx install --editable airbyte-ci/connectors/ci_credentials/
```

This is useful when you are making changes to the package and want to test them in real-time.

## Usage
After installation, you can use the ci_credentials command in your terminal.

## Run it

The `VERSION=dev` will make it so it knows to use your local current working directory and not the Github Action one.

### Help
```bash
VERSION=dev ci_credentials --help
```

### Write credentials for a specific connector to local storage
To download GSM secrets to `airbyte-integrations/connectors/source-bings-ads/secrets`:
```bash
VERSION=dev ci_credentials source-bing-ads write-to-storage
```

### Write credentials for all connectors to local storage
To download GSM secrets to for all available connectors into their respective `secrets` directories:
```bash
VERSION=dev ci_credentials all write-to-storage
```

### Update secrets
To upload to GSM newly updated configurations from `airbyte-integrations/connectors/source-bings-ads/secrets/updated_configurations`:

```bash
VERSION=dev ci_credentials source-bing-ads update-secrets
```

