# Salesforce source connector

This is the repository for the Salesforce source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/salesforce).

## Local development

### Prerequisites

- Python (~=3.9)
- Poetry (~=1.7) - installation instructions [here](https://python-poetry.org/docs/#installation)

### Installing the connector

From this connector directory, run:

```bash
poetry install --with dev
```

### Create credentials

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/sources/salesforce)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_salesforce/spec.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.

The connector supports two authentication methods:

1. **Refresh Token Authentication** (default): Uses OAuth 2.0 refresh token flow. See `integration_tests/sample_config.json` for a sample config file.
2. **Client Credentials Authentication**: Uses OAuth 2.0 client credentials flow. See `integration_tests/sample_config_client_credentials.json` for a sample config file.

For client credentials authentication, you need to:
- Set `auth_type` to `"client_credentials"`
- Provide your Salesforce domain URL in the format: `https://your-domain.my.salesforce.com`
- Ensure your connected app has the appropriate permissions for client credentials flow

### Locally running the connector

```
poetry run source-salesforce spec
poetry run source-salesforce check --config secrets/config.json
poetry run source-salesforce discover --config secrets/config.json
poetry run source-salesforce read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Running unit tests

To run unit tests locally, from the connector directory run:

```
poetry run pytest unit_tests
```

### Building the docker image

#### Using Poe (Recommended)

We recommend using Poe the Poet tasks defined in `pyproject.toml`:

```bash
# Install Poe (if not already available)
curl -LsSf https://astral.sh/uv/install.sh | sh
~/.local/bin/uv tool install poethepoet

# Or using alternative methods:
# brew install uv && uv tool install poethepoet
# pip install poethepoet
```

From the connector directory, run:

```bash
# Install dependencies
poe install

# Run tests
poe pytest

# Run fast tests
poe pytest-fast

# Check code quality
poe check-all

# Fix formatting and linting issues
poe fix-all

# Build Docker images
poe build         # Build local dev image
poe build-arm     # Build ARM64: airbyte/source-salesforce:arm
poe build-amd     # Build AMD64: airbyte/source-salesforce:amd
poe build-all     # Build both architectures
```

**Available Poe tasks for this connector:**
- `poe install` - Install dependencies
- `poe pytest` - Run all tests
- `poe pytest-fast` - Run fast subset of tests
- `poe coverage` - Generate test coverage report
- `poe coverage-html` - Generate HTML coverage report
- `poe check-ruff-lint` - Check code linting
- `poe check-ruff-format` - Check code formatting
- `poe check-ruff` - Check both linting and formatting
- `poe check-mypy` - Run type checking
- `poe check-all` - Run all code quality checks
- `poe fix-ruff-format` - Fix formatting issues
- `poe fix-ruff-lint` - Fix linting issues
- `poe fix-ruff` - Fix both formatting and linting
- `poe fix-all` - Fix all auto-fixable issues
- `poe fix-and-check` - Fix issues and then run checks
- `poe build` - Build local dev image
- `poe build-arm` - Build ARM64 image
- `poe build-amd` - Build AMD64 image
- `poe build-all` - Build both architectures
- `poe release` - End-to-end release (build + push + manifest)

Run `poe --help` from the connector directory to see all available tasks.

#### Legacy Method (Deprecated)

**Note**: `airbyte-ci` is now deprecated and will be phased out shortly.

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) (deprecated)
2. Run the following command to build the docker image:

```bash
airbyte-ci connectors --name=source-salesforce build
```

An image will be available on your host with the tag `airbyte/source-salesforce:dev`.

### Running as a docker container

Then run any of the connector commands as follows:

```
docker run --rm airbyte/source-salesforce:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-salesforce:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-salesforce:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-salesforce:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Running our CI test suite

You can run our full test suite locally using **Poe** (recommended):

```bash
# Run all tests
poe pytest

# Run fast tests (subset)
poe pytest-fast

# Check code quality (includes linting, formatting, type checking)
poe check-all

# Generate test coverage report
poe coverage
```

**Legacy method (deprecated)**: You can also use [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md), though this is deprecated:

```bash
airbyte-ci connectors --name=source-salesforce test
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

1. Make sure your changes are passing our test suite: `poe pytest` and `poe check-all` (or legacy: `airbyte-ci connectors --name=source-salesforce test`)
2. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)):
   - bump the `dockerImageTag` value in in `metadata.yaml`
   - bump the `version` value in `pyproject.toml`
3. Make sure the `metadata.yaml` content is up to date.
4. Make sure the connector documentation and its changelog is up to date (`docs/integrations/sources/salesforce.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.

# Fabrix Build

## Using Poe (Recommended)

Run from the connector directory:

```bash
# Install dependencies and prepare for building
poe install

# Run tests before building
poe pytest

# Check code quality
poe check-all

# Build Docker images
poe build-all    # Build both ARM64 and AMD64 images
```

## Legacy Method (Deprecated)

Run from Devcontainer (so airbyte-ci is runnable)

**Note**: `airbyte-ci` is deprecated. Use Poe commands above when available.

Build for arm
```bash
airbyte-ci connectors --name=source-salesforce build --architecture linux/arm64 -t arm
```

Build for AMD64
```bash
airbyte-ci connectors --name=source-salesforce build --architecture linux/amd64 -t amd
```

Export images to files - Extract for dev container to local docker for ECR push

```bash
# Export ARM image to tar file
docker save airbyte/source-salesforce:arm -o salesforce-connector-arm.tar

# Export AMD64 image to tar file
docker save airbyte/source-salesforce:amd -o salesforce-connector-amd.tar

# You can then copy these tar files to your host machine and load them into Docker
# On your host machine:
docker load -i salesforce-connector-arm.tar
docker load -i salesforce-connector-amd.tar
```

## Push to ECR

### Quick Deploy (Recommended)

Use the provided Poe tasks for streamlined deployment:

```bash
# 1) ECR login (HOST)
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin \
    794038212761.dkr.ecr.us-east-1.amazonaws.com

# 2) Version and optional registry
export VERSION=2.7.5
export REGISTRY=${REGISTRY:-794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker}

# 3) Build both architectures (run in connector dir)
poe build-all

# 4) Push images
poe ecr-tag-push-arm
poe ecr-tag-push-amd

# 5) Manifests
poe manifest-push-version
poe manifest-push-latest
```

### One-shot release with Poe

If you're already logged into ECR, you can run the entire flow in one command:

```bash
# Optional: override REGISTRY
export REGISTRY=794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker

poe release 2.7.5
```

### Manual Deploy Commands

After loading the Docker images, you can tag and push them to your ECR repository:

```bash
# Login to ECR (ensure AWS credentials are configured)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 794038212761.dkr.ecr.us-east-1.amazonaws.com

# Version tag to use
VERSION="1.0.0"

# Tag and push ARM image with version and 'arm' tag
docker tag airbyte/source-salesforce:arm 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:${VERSION}-arm
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:${VERSION}-arm

# Also push as 'arm' tag for latest reference
docker tag airbyte/source-salesforce:arm 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:arm
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:arm

# Tag and push AMD64 image with version and 'amd' tag
docker tag airbyte/source-salesforce:amd 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:${VERSION}-amd
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:${VERSION}-amd

# Also push as 'amd' tag for latest reference
docker tag airbyte/source-salesforce:amd 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:amd
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:amd

# Create and push a multi-architecture manifest
# This will create a manifest that points to both ARM and AMD images and selects the right one based on the cluster's architecture
docker manifest create 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:${VERSION} \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:${VERSION}-arm \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:${VERSION}-amd

# Annotate the manifest with architecture information
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:${VERSION} \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:${VERSION}-arm --os linux --arch arm64
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:${VERSION} \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:${VERSION}-amd --os linux --arch amd64

# Push the manifest
docker manifest push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:${VERSION}

# Also create a 'latest' manifest for convenience
docker manifest create 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:latest \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:arm \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:amd

# Annotate the latest manifest
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:latest \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:arm --os linux --arch arm64
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:latest \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:amd --os linux --arch amd64

# Push the latest manifest
docker manifest push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-salesforce/docker:latest
```

## Alternative: Using airbyte-cdk CLI

The `airbyte-cdk` CLI is now available and provides additional functionality:

```bash
# Install the airbyte-cdk CLI using uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
~/.local/bin/uv tool install 'airbyte-cdk[dev]'

# Or using pip
pip install 'airbyte-cdk[dev]'

# Available commands
airbyte-cdk --help

# Manage secrets
airbyte-cdk secrets list
airbyte-cdk secrets fetch

# Other connector operations
airbyte-cdk build --connector source-salesforce
airbyte-cdk test --connector source-salesforce
```

For the most up-to-date commands, check the [Airbyte CDK documentation](https://docs.airbyte.com/platform/connector-development/cdk-python/).