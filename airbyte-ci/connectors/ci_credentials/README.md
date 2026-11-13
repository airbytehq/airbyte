# CI Credentials

CLI tooling to read and manage GSM secrets:

- `write-to-storage` download a connector's secrets locally in the connector's `secrets` folder
- `update-secrets` uploads new connector secret version that were locally updated.

## Requirements

This project requires Python 3.11 and `pipx`.

## Installation

The recommended way to install `ci_credentials` is using pipx. This ensures the tool and its dependencies are isolated from your other Python projects.

First, install `pyenv`. If you don't have it yet, you can install it using Homebrew:

```bash
brew update
brew install pyenv
```

If you haven't installed pipx, you can do it with pip:

```bash
cd airbyte-ci/connectors/ci_credentials/
pyenv install # ensure you have the correct python version
python -m pip install --user pipx
python -m pipx ensurepath
```

Once pyenv and pipx is installed then run the following (assuming you're in Airbyte repo root):

```bash
pipx install --editable --force --python=python3.11 airbyte-ci/connectors/ci_credentials/
```

Or install with a link to the default branch of the repo:

```bash
pipx install git+https://github.com/airbytehq/airbyte.git#subdirectory=airbyte-ci/connectors/ci_credentials
```

This command installs `ci_credentials` and makes it globally available in your terminal.

> [!Note]
>
> - `--force` is required to ensure updates are applied on subsequent installs.
> - `--python=python3.11` is required to ensure the correct python version is used.

## Get GSM access

Download a Service account json key that has access to Google Secrets Manager.
`ci_credentials` expects `GCP_GSM_CREDENTIALS` to be set in environment to be able to access secrets.

### Create Service Account

- Go to https://console.cloud.google.com/iam-admin/serviceaccounts/create?project=dataline-integration-testing
- In step #1 `Service account details`, set a name and a relevant description
- In step #2 `Grant this service account access to project`, select role `Owner` (there is a role that is more scope but I based this decision on others `<user>-testing` service account)

### Create Service Account Token

- Go to https://console.cloud.google.com/iam-admin/serviceaccounts?project=dataline-integration-testing
- Find your service account and click on it
- Go in the tab "KEYS"
- Click on "ADD KEY -> Create new key" and select JSON. This will download a file on your computer

### Setup ci_credentials

- In your .zshrc, add: `export GCP_GSM_CREDENTIALS=$(cat <path to JSON file>)`

## Development

During development, you can use the `--editable` option to make changes to the `ci_credentials` package and have them immediately take effect without needing to reinstall the package:

```bash
pipx install --editable airbyte-ci/connectors/ci_credentials/
```

This is useful when you are making changes to the package and want to test them in real-time.

> [!Note]
>
> - The package name is `ci_credentials`, not `airbyte-ci`. You will need this when uninstalling or reinstalling.

## Usage

After installation, you can use the `ci_credentials` command in your terminal.

## Run it

The `VERSION=dev` will make it so it knows to use your local current working directory and not the Github Action one.

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

## FAQ

### Help

```bash
VERSION=dev ci_credentials --help
```

### What is `VERSION=dev`?

This is a way to tell the tool to write secrets using your local current working directory and not the Github Action runner one.
