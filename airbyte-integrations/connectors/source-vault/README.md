<p align="center">
  <a href="https://airbyte.com"><img src="https://assets.website-files.com/605e01bc25f7e19a82e74788/624d9c4a375a55100be6b257_Airbyte_logo_color_dark.svg" alt="Airbyte"></a>
</p>
<p align="center">
    <em>Data integration platform for ELT pipelines from APIs, databases & files to databases, warehouses & lakes</em>
</p>
<p align="center">
<a href="https://github.com/airbytehq/airbyte/stargazers/" target="_blank">
    <img src="https://img.shields.io/github/stars/airbytehq/airbyte?style=social&label=Star&maxAge=2592000" alt="Test">
</a>
<a href="https://github.com/airbytehq/airbyte/releases" target="_blank">
    <img src="https://img.shields.io/github/v/release/airbytehq/airbyte?color=white" alt="Release">
</a>
<a href="https://airbytehq.slack.com/" target="_blank">
    <img src="https://img.shields.io/badge/slack-join-white.svg?logo=slack" alt="Slack">
</a>
<a href="https://www.youtube.com/c/AirbyteHQ/?sub_confirmation=1" target="_blank">
    <img alt="YouTube Channel Views" src="https://img.shields.io/youtube/channel/views/UCQ_JWEFzs1_INqdhIO3kmrw?style=social">
</a>
<a href="https://github.com/airbytehq/airbyte/actions/workflows/gradle.yml" target="_blank">
    <img src="https://img.shields.io/github/actions/workflow/status/airbytehq/airbyte/gradle.yml?branch=master" alt="Build">
</a>
<a href="https://github.com/airbytehq/airbyte/tree/master/docs/project-overview/licenses" target="_blank">
    <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white" alt="License">
</a>
<a href="https://github.com/airbytehq/airbyte/tree/master/docs/project-overview/licenses" target="_blank">
    <img src="https://img.shields.io/static/v1?label=license&message=ELv2&color=white" alt="License">
</a>
</p>

We believe that only an **open-source solution to data movement** can cover the long tail of data sources while empowering data engineers to customize existing connectors. Our ultimate vision is to help you move data from any source to any destination. Airbyte already provides the largest [catalog](https://docs.airbyte.com/integrations/) of 300+ connectors for APIs, databases, data warehouses, and data lakes.

![Airbyte Connections UI](https://github.com/airbytehq/airbyte/assets/38087517/35b01d0b-00bf-407b-87e6-a5cd5cd720b5)
_Screenshot taken from [Airbyte Cloud](https://cloud.airbyte.com/signup)_.

### Getting Started

- [Deploy Airbyte Open Source](https://docs.airbyte.com/quickstart/deploy-airbyte) or set up [Airbyte Cloud](https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud) to start centralizing your data.
- Create connectors in minutes with our [no-code Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview) or [low-code CDK](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview).
- Explore popular use cases in our [tutorials](https://airbyte.com/tutorials).
- Orchestrate Airbyte syncs with [Airflow](https://docs.airbyte.com/operator-guides/using-the-airflow-airbyte-operator), [Prefect](https://docs.airbyte.com/operator-guides/using-prefect-task), [Dagster](https://docs.airbyte.com/operator-guides/using-dagster-integration), [Kestra](https://docs.airbyte.com/operator-guides/using-kestra-plugin), or the [Airbyte API](https://reference.airbyte.com/reference/start).

Try it out yourself with our [demo app](https://demo.airbyte.io/), visit our [full documentation](https://docs.airbyte.com/), and learn more about [recent announcements](https://airbyte.com/blog-categories/company-updates). See our [registry](https://connectors.airbyte.com/files/generated_reports/connector_registry_report.html) for a full list of connectors already available in Airbyte or Airbyte Cloud.

### Join the Airbyte Community

The Airbyte community can be found in the [Airbyte Community Slack](https://airbyte.com/community), where you can ask questions and voice ideas. You can also ask for help in our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions), or join our [Office Hours](https://airbyte.io/daily-office-hours/). Airbyte's roadmap is publicly viewable on [GitHub](https://github.com/orgs/airbytehq/projects/37/views/1?pane=issue&itemId=26937554).

For videos and blogs on data engineering and building your data stack, check out Airbyte's [Content Hub](https://airbyte.com/content-hub), [YouTube](https://www.youtube.com/c/AirbyteHQ), and sign up for our [newsletter](https://airbyte.com/newsletter).

### Contributing

If you've found a problem with Airbyte, please open a [GitHub issue](https://github.com/airbytehq/airbyte/issues/new/choose). To contribute to Airbyte and see our Code of Conduct, please see the [contributing guide](https://docs.airbyte.com/contributing-to-airbyte/). We have a list of [good first issues](https://github.com/airbytehq/airbyte/labels/contributor-program) that contain bugs that have a relatively limited scope. This is a great place to get started, gain experience, and get familiar with our contribution process.

### Security

Airbyte takes security issues very seriously. **Please do not file GitHub issues or post on our public forum for security vulnerabilities**. Email `security@airbyte.io` if you believe you have uncovered a vulnerability. In the message, try to provide a description of the issue and ideally a way of reproducing it. The security team will get back to you as soon as possible.

[Airbyte Enterprise](https://airbyte.com/airbyte-enterprise) also offers additional security features (among others) on top of Airbyte open-source.

### License

See the [LICENSE](docs/project-overview/licenses/) file for licensing information, and our [FAQ](docs/project-overview/licenses/license-faq.md) for any questions you may have on that topic.

### Thank You

Airbyte would not be possible without the support and assistance of other open-source tools and companies! Visit our [thank you page](THANK-YOU.md) to learn more about how we build Airbyte.

<a href="https://github.com/airbytehq/airbyte/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=airbytehq/airbyte"/>
</a>

# HashiCorp Vault Source

This is the repository for the HashiCorp Vault source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/vault).

## Local development

### Prerequisites

- Python (~=3.10)
- Poetry (~=1.7) - installation instructions [here](https://python-poetry.org/docs/#installation)

### Installing the connector

From this connector directory, run:

```bash
poetry install --with dev
```

### Create credentials

You'll need a HashiCorp Vault instance with AppRole authentication enabled. Create a `secrets/config.json` file with the following structure:

```json
{
  "vault_url": "https://your-vault-instance.com",
  "role_id": "your-role-id",
  "secret_id": "your-secret-id",
  "namespace": "admin",
  "verify_ssl": true
}
```

Note that the `namespace` parameter is optional:
- For HCP Vault (HashiCorp Cloud Platform), use `"admin"`
- For self-hosted Vault, use `"root"` or leave empty (`""`)

### Setting up Vault AppRole Authentication

Use the provided setup script to create the necessary AppRole and policy:

```bash
# Make the script executable
chmod +x setup-fabrix-read.sh

# Run the setup script (requires vault CLI and authentication)
./setup-fabrix-read.sh
```

This script will:
1. Enable AppRole authentication
2. Create a read-only policy with appropriate permissions
3. Create an AppRole role with non-expiring secret IDs
4. Generate Role ID and Secret ID for use in the connector

### Locally running the connector

```bash
poetry run source-vault spec
poetry run source-vault check --config secrets/config.json
poetry run source-vault discover --config secrets/config.json
poetry run source-vault read --config secrets/config.json --catalog sample_files/configured_catalog.json
```

### Running unit tests

To run unit tests locally, from the connector directory run:

```bash
poetry run pytest unit_tests
```

### Building the docker image

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
2. Run the following command to build the docker image:

```bash
airbyte-ci connectors --name=source-vault build
```

An image will be available on your host with the tag `airbyte/source-vault:dev`.

### Running as a docker container

Then run any of the connector commands as follows:

```bash
docker run --rm airbyte/source-vault:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-vault:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-vault:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-vault:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Running our CI test suite

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=source-vault test
```

### Customizing acceptance Tests

Customize `acceptance-test-config.yml` file to configure acceptance tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.

### Dependency Management

All of your dependencies should be managed via Poetry.
To add a new dependency, run:

```bash
poetry add <package-name>
```

Please commit the changes to `pyproject.toml` and `poetry.lock` files.

## Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?

1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=source-vault test`
2. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)):
   - bump the `dockerImageTag` value in in `metadata.yaml`
   - bump the `version` value in `pyproject.toml`
3. Make sure the `metadata.yaml` content is up to date.
4. Make sure the connector documentation and its changelog is up to date (`docs/integrations/sources/vault.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.

# Fabrix

## Vault Credentials Setup for Running Locally

When running the Vault connector locally using launch.json, you need valid Vault credentials. The connector uses AppRole authentication.

### Setting up AppRole in Vault

1. **Enable AppRole authentication** (if not already enabled):
   ```bash
   vault auth enable approle
   ```

2. **Create the read-only policy** using the provided script:
   ```bash
   ./setup-fabrix-read.sh
   ```

3. **Update your secrets/config.json** with the generated credentials:
   ```json
   {
     "vault_url": "https://your-vault-instance.com:8200",
     "role_id": "your-role-id-from-script",
     "secret_id": "your-secret-id-from-script",
     "namespace": "admin",
     "verify_ssl": true
   }
   ```

### Regenerating Secret IDs

If your secret ID expires, generate a new one:

```bash
vault write -f auth/approle/role/fabrix-read/secret-id
```

## Fabrix Build

Run from Devcontainer (so airbyte-ci is runnable)

### Quick Build (Recommended)

Use the provided build script for a complete build:

```bash
# Build both ARM and AMD64 architectures and export tar files
./build.sh
```

This script will:
1. Build for both ARM64 and AMD64 architectures
2. Export images to tar files
3. Show next steps for deployment

### Manual Build Commands

If you prefer to build manually:

#### Build for ARM
```bash
airbyte-ci connectors --name=source-vault build --architecture linux/arm64 -t arm
```

#### Build for AMD64
```bash
airbyte-ci connectors --name=source-vault build --architecture linux/amd64 -t amd
```

#### Export images to files - Extract for dev container to local docker for ECR push

```bash
# Export ARM image to tar file
docker save airbyte/source-vault:arm -o vault-connector-arm.tar

# Export AMD64 image to tar file
docker save airbyte/source-vault:amd -o vault-connector-amd.tar

# You can then copy these tar files to your host machine and load them into Docker
# On your host machine:
docker load -i vault-connector-arm.tar
docker load -i vault-connector-amd.tar
```

## Push to ECR

### Quick Deploy (Recommended)

Use the provided deployment script:

```bash
# Deploy to ECR (requires AWS credentials)
./deploy-ecr.sh

# Or deploy a specific version
./deploy-ecr.sh 1.0.1
```

This script will:
1. Login to ECR
2. Load images from tar files (if present)
3. Tag and push both ARM and AMD64 images
4. Create multi-architecture manifests
5. Push versioned and latest tags

### Manual Deploy Commands

After loading the Docker images, you can tag and push them to your ECR repository manually:

```bash
# Login to ECR (ensure AWS credentials are configured)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 794038212761.dkr.ecr.us-east-1.amazonaws.com

# Version tag to use
VERSION="1.0.0"

# Tag and push ARM image with version and 'arm' tag
docker tag airbyte/source-vault:arm 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:${VERSION}-arm
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:${VERSION}-arm

# Also push as 'arm' tag for latest reference
docker tag airbyte/source-vault:arm 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:arm
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:arm

# Tag and push AMD64 image with version and 'amd' tag
docker tag airbyte/source-vault:amd 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:${VERSION}-amd
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:${VERSION}-amd

# Also push as 'amd' tag for latest reference
docker tag airbyte/source-vault:amd 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:amd
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:amd

# Create and push a multi-architecture manifest
# This will create a manifest that points to both ARM and AMD images and selects the right one based on the cluster's architecture
docker manifest create 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:${VERSION} \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:${VERSION}-arm \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:${VERSION}-amd

# Annotate the manifest with architecture information
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:${VERSION} \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:${VERSION}-arm --os linux --arch arm64
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:${VERSION} \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:${VERSION}-amd --os linux --arch amd64

# Push the manifest
docker manifest push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:${VERSION}

# Also create a 'latest' manifest for convenience
docker manifest create 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:latest \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:arm \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:amd

# Annotate the latest manifest
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:latest \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:arm --os linux --arch arm64
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:latest \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:amd --os linux --arch amd64

# Push the latest manifest
docker manifest push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-vault/docker:latest
```

## Streams

This connector supports the following streams:

1. **vault_info** - Information about the Vault instance
2. **users** - Human user entities from Vault's identity system and user-based auth methods (userpass, ldap, okta, radius)
3. **service_accounts** - Service account entities from Vault's identity system and AppRole auth methods
4. **policies** - Access control policies
5. **groups** - Group entities from Vault's identity system
6. **namespaces** - Namespaces (Enterprise feature, recursive)
7. **secrets** - Secret names without values (recursive)
8. **identity_providers** - OIDC identity providers
9. **auth_methods** - Authentication methods

## Features

- Supports AppRole authentication
- Handles both HCP Vault and self-hosted Vault instances
- Recursively discovers namespaces and secrets
- Retrieves metadata without exposing secret values
- Configurable SSL verification
- Non-expiring secret IDs for production deployment
- Separates human users from service accounts for better data organization
- Comprehensive AppRole support with detailed configuration information

## User vs Service Account Classification

The connector separates users from service accounts based on auth method types:

### Users Stream
- Identity entities with aliases from user-based auth methods: `userpass`, `ldap`, `okta`, `radius`, `oidc`, `jwt`, `github`
- Users from user-based auth methods: `userpass`, `ldap`, `okta`, `radius`, `oidc`, `jwt`, `github`

### Service Accounts Stream
- AppRole roles with detailed configuration (role_id, token settings, policies)
- Identity entities without user-based auth method aliases (machine/service accounts)
- Service-oriented auth methods: `approle`, `aws`, `gcp`, `azure`, `kubernetes`, `cert`, `tls`, etc.

This classification ensures that human users (authenticated via traditional user-based methods) are clearly separated from automated service accounts and machine identities.

## Configuration

### TTL Settings

The connector is configured with the following TTL settings for production use:

- **Secret ID TTL**: `0` (never expires) - Perfect for production deployment
- **Token TTL**: `12h` (12 hours) - Tokens expire and are renewed automatically
- **Token Max TTL**: `24h` (24 hours) - Maximum token lifetime

This configuration provides:
- **Operational simplicity**: Secret IDs never expire once deployed
- **Security best practices**: Tokens refresh regularly
- **Automatic renewal**: HVAC client handles token renewal automatically

### Permissions

The connector requires a Vault policy with read access to:
- System health and status endpoints
- Identity entities and groups
- Authentication methods and roles
- Policies
- Secret engines metadata
- Namespaces (if using Vault Enterprise)

See `setup-fabrix-read.sh` for the complete policy definition.
