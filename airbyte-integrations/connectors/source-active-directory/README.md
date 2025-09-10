# Active Directory Source

This connector pulls data from Active Directory. It supports connecting to Active Directory servers and extracting user, group, and organizational unit information.

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

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/sources/active-directory)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_active_directory/spec.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

### Locally running the connector

```bash
poetry run source-active-directory spec
poetry run source-active-directory check --config secrets/config.json
poetry run source-active-directory discover --config secrets/config.json
poetry run source-active-directory read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Running unit tests

To run unit tests locally, from the connector directory run:

```bash
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
poe build-arm     # Build ARM64: airbyte/source-active-directory:arm
poe build-amd     # Build AMD64: airbyte/source-active-directory:amd
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
airbyte-ci connectors --name=source-active-directory build
```

An image will be available on your host with the tag `airbyte/source-active-directory:dev`.

### Running as a docker container

Then run any of the connector commands as follows:

```bash
docker run --rm airbyte/source-active-directory:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-active-directory:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-active-directory:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-active-directory:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
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
airbyte-ci connectors --name=source-active-directory test
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

1. Make sure your changes are passing our test suite: `poe pytest` and `poe check-all` (or legacy: `airbyte-ci connectors --name=source-active-directory test`)
2. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)):
   - bump the `dockerImageTag` value in in `metadata.yaml`
   - bump the `version` value in `pyproject.toml`
3. Make sure the `metadata.yaml` content is up to date.
4. Make sure the connector documentation and its changelog is up to date (`docs/integrations/sources/active-directory.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.

# Fabrix

## Active Directory Connection Setup

When running the Active Directory connector locally, you'll need to configure the connection to your Active Directory server.

Ensure you have the proper network connectivity and credentials to connect to your Active Directory server. The connector may need to connect to domain controllers on ports 389 (LDAP) or 636 (LDAPS).

**Connection Configuration:**

Create a `secrets/config.json` file with your Active Directory connection details:
```json
{
  "host": "your-ad-server.domain.com",
  "port": 389,
  "username": "your-username",
  "password": "your-password",
  "base_dn": "DC=domain,DC=com",
  "use_ssl": false
}
```

## Fabrix Build

### Using Poe (Recommended)

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

### Legacy Method (Deprecated)

Run from Devcontainer (so airbyte-ci is runnable)

**Note**: `airbyte-ci` is deprecated. Use Poe commands above when available.

Build for arm
```bash
airbyte-ci connectors --name=source-active-directory build --architecture linux/arm64 -t arm
```

Build for AMD64
```bash
airbyte-ci connectors --name=source-active-directory build --architecture linux/amd64 -t amd
```

Export images to files - Extract for dev container to local docker for ECR push

```bash
# Export ARM image to tar file
docker save airbyte/source-active-directory:arm -o active-directory-connector-arm.tar

# Export AMD64 image to tar file
docker save airbyte/source-active-directory:amd -o active-directory-connector-amd.tar

# You can then copy these tar files to your host machine and load them into Docker
# On your host machine:
docker load -i active-directory-connector-arm.tar
docker load -i active-directory-connector-amd.tar
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
export VERSION=1.0.0
export REGISTRY=${REGISTRY:-794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker}

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
export REGISTRY=794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker

poe release 1.0.0
```

### Manual Deploy Commands

After loading the Docker images, you can tag and push them to your ECR repository:

```bash
# Login to ECR (ensure AWS credentials are configured)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 794038212761.dkr.ecr.us-east-1.amazonaws.com

# Version tag to use
VERSION="1.0.0"

# Tag and push ARM image with version and 'arm' tag
docker tag airbyte/source-active-directory:arm 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:${VERSION}-arm
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:${VERSION}-arm

# Also push as 'arm' tag for latest reference
docker tag airbyte/source-active-directory:arm 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:arm
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:arm

# Tag and push AMD64 image with version and 'amd' tag
docker tag airbyte/source-active-directory:amd 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:${VERSION}-amd
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:${VERSION}-amd

# Also push as 'amd' tag for latest reference
docker tag airbyte/source-active-directory:amd 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:amd
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:amd

# Create and push a multi-architecture manifest
# This will create a manifest that points to both ARM and AMD images and selects the right one based on the cluster's architecture
docker manifest create 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:${VERSION} \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:${VERSION}-arm \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:${VERSION}-amd

# Annotate the manifest with architecture information
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:${VERSION} \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:${VERSION}-arm --os linux --arch arm64
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:${VERSION} \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:${VERSION}-amd --os linux --arch amd64

# Push the manifest
docker manifest push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:${VERSION}

# Also create a 'latest' manifest for convenience
docker manifest create 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:latest \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:arm \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:amd

# Annotate the latest manifest
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:latest \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:arm --os linux --arch arm64
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:latest \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:amd --os linux --arch amd64

# Push the latest manifest
docker manifest push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-active-directory/docker:latest
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
airbyte-cdk build --connector source-active-directory
airbyte-cdk test --connector source-active-directory
```

For the most up-to-date commands, check the [Airbyte CDK documentation](https://docs.airbyte.com/platform/connector-development/cdk-python/).
