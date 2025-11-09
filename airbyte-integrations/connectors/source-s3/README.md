# S3 source connector

This is the repository for the S3 source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/s3).

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

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/sources/s3)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_s3/spec.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.
See `sample_files/sample_config.json` for a sample config file.

### Locally running the connector

```
poetry run source-s3 spec
poetry run source-s3 check --config secrets/config.json
poetry run source-s3 discover --config secrets/config.json
poetry run source-s3 read --config secrets/config.json --catalog sample_files/configured_catalog.json
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
poe build-arm     # Build ARM64: airbyte/source-s3:arm
poe build-amd     # Build AMD64: airbyte/source-s3:amd
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
- `poe save-arm` - Save ARM64 image to tarball
- `poe save-amd` - Save AMD64 image to tarball
- `poe ecr-tag-push-arm` - Tag and push ARM image to ECR
- `poe ecr-tag-push-amd` - Tag and push AMD64 image to ECR
- `poe ecr-push-all` - Push both images to ECR
- `poe manifest-push-version` - Create and push versioned manifest
- `poe manifest-push-latest` - Create and push latest manifest
- `poe release` - End-to-end release (build + push + manifest)

Run `poe --help` from the connector directory to see all available tasks.

#### Legacy Method (Deprecated)

**Note**: `airbyte-ci` is now deprecated and will be phased out shortly.

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) (deprecated)
2. Run the following command to build the docker image:

```bash
airbyte-ci connectors --name=source-s3 build
```

An image will be available on your host with the tag `airbyte/source-s3:dev`.

### Running as a docker container

Then run any of the connector commands as follows:

```
docker run --rm airbyte/source-s3:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-s3:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-s3:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-s3:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
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
airbyte-ci connectors --name=source-s3 test
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

1. Make sure your changes are passing our test suite: `poe pytest` and `poe check-all` (or legacy: `airbyte-ci connectors --name=source-s3 test`)
2. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)):
   - bump the `dockerImageTag` value in in `metadata.yaml`
   - bump the `version` value in `pyproject.toml`
3. Make sure the `metadata.yaml` content is up to date.
4. Make sure the connector documentation and its changelog is up to date (`docs/integrations/sources/s3.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.

# Fabrix

## AWS Role Assumption for Running Locally

When running the S3 connector locally using launch.json, you need to assume the AWS role `arn:aws:iam::794038212761:role/FabrixScanner`.

Since the dev container doesn't have AWS CLI installed, you'll need to run the assume-role command from a terminal outside the dev container (e.g., your host machine), then copy the credentials to the dev container.

**From your host machine terminal (or any terminal with AWS CLI):**

```bash
# Run this one-liner to generate export commands
aws sts assume-role --role-arn arn:aws:iam::794038212761:role/FabrixScanner --role-session-name s3-connector-dev | jq -r '.Credentials | "export AWS_ACCESS_KEY_ID=\"\(.AccessKeyId)\"\nexport AWS_SECRET_ACCESS_KEY=\"\(.SecretAccessKey)\"\nexport AWS_SESSION_TOKEN=\"\(.SessionToken)\""'
```

This will output three export commands that you can copy and paste directly into your dev container terminal:
```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
```

Simply copy the entire output and paste it into your dev container terminal to set up the credentials.

Alternatively, you can use tools like `aws-vault` or `aws-sso-util` on your host machine to manage the role assumption.

# Fabrix

## AWS Role Assumption for Running Locally

When running the S3 connector locally using launch.json, you need to assume the AWS role `arn:aws:iam::794038212761:role/FabrixScanner`.

Since the dev container doesn't have AWS CLI installed, you'll need to run the assume-role command from a terminal outside the dev container (e.g., your host machine), then copy the credentials to the dev container.

**From your host machine terminal (or any terminal with AWS CLI):**

```bash
# Run this one-liner to generate export commands
aws sts assume-role --role-arn arn:aws:iam::794038212761:role/FabrixScanner --role-session-name s3-connector-dev | jq -r '.Credentials | "export AWS_ACCESS_KEY_ID=\"\(.AccessKeyId)\"\nexport AWS_SECRET_ACCESS_KEY=\"\(.SecretAccessKey)\"\nexport AWS_SESSION_TOKEN=\"\(.SessionToken)\""'
```

This will output three export commands that you can copy and paste directly into your dev container terminal:
```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
```

Simply copy the entire output and paste it into your dev container terminal to set up the credentials.

Alternatively, you can use tools like `aws-vault` or `aws-sso-util` on your host machine to manage the role assumption.

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
airbyte-ci connectors --name=source-s3 build --architecture linux/arm64 -t arm
```

Build for AMD64
```bash
airbyte-ci connectors --name=source-s3 build --architecture linux/amd64 -t amd
```

Export images to files - Extract for dev container to local docker for ECR push

```bash
# Export ARM image to tar file (using Poe)
poe save-arm

# Export AMD64 image to tar file (using Poe)
poe save-amd

# Legacy method (deprecated):
docker save airbyte/source-s3:arm -o s3-connector-arm.tar
docker save airbyte/source-s3:amd -o s3-connector-amd.tar

# You can then copy these tar files to your host machine and load them into Docker
# On your host machine:
docker load -i s3-connector-arm.tar
docker load -i s3-connector-amd.tar
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
export REGISTRY=${REGISTRY:-794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker}

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
export REGISTRY=794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker

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
docker tag airbyte/source-s3:arm 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:${VERSION}-arm
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:${VERSION}-arm

# Also push as 'arm' tag for latest reference
docker tag airbyte/source-s3:arm 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:arm
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:arm

# Tag and push AMD64 image with version and 'amd' tag
docker tag airbyte/source-s3:amd 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:${VERSION}-amd
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:${VERSION}-amd

# Also push as 'amd' tag for latest reference
docker tag airbyte/source-s3:amd 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:amd
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:amd

# Create and push a multi-architecture manifest
# This will create a manifest that points to both ARM and AMD images and selects the right one based on the cluster's architecture
docker manifest create 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:${VERSION} \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:${VERSION}-arm \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:${VERSION}-amd

# Annotate the manifest with architecture information
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:${VERSION} \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:${VERSION}-arm --os linux --arch arm64
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:${VERSION} \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:${VERSION}-amd --os linux --arch amd64

# Push the manifest
docker manifest push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:${VERSION}

# Also create a 'latest' manifest for convenience
docker manifest create 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:latest \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:arm \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:amd

# Annotate the latest manifest
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:latest \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:arm --os linux --arch arm64
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:latest \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:amd --os linux --arch amd64

# Push the latest manifest
docker manifest push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-s3/docker:latest
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
airbyte-cdk build --connector source-s3
airbyte-cdk test --connector source-s3
```

For the most up-to-date commands, check the [Airbyte CDK documentation](https://docs.airbyte.com/platform/connector-development/cdk-python/).
