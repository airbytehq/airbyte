# AWS IAM Source

This connector pulls data from AWS IAM using boto3. It supports assuming a role by providing a Role ARN and optional External ID.

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

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/sources/aws-iam)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_aws_iam/spec.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

### Locally running the connector

```bash
poetry run source-aws-iam spec
poetry run source-aws-iam check --config secrets/config.json
poetry run source-aws-iam discover --config secrets/config.json
poetry run source-aws-iam read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Running unit tests

To run unit tests locally, from the connector directory run:

```bash
poetry run pytest unit_tests
```

### Building the docker image

#### Using Poe (Recommended)

Airbyte now uses **Poe the Poet** as the primary task runner for connector development. Install Poe using:

```bash
# Install Poe the Poet
brew tap nat-n/poethepoet
brew install nat-n/poethepoet/poethepoet

# Or using uv (recommended Python package manager)
brew install uv
uv tool install poethepoet
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

Run `poe --help` from the connector directory to see all available tasks.

**Note**: The connector includes a basic `metadata.yaml` file with the required `dockerImageTag` field. You may need to adjust the version number and other metadata fields as needed for your specific deployment.

#### Legacy Method (Deprecated)

**Note**: `airbyte-ci` is now deprecated and will be phased out shortly.

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) (deprecated)
2. Run the following command to build the docker image:

```bash
airbyte-ci connectors --name=source-aws-iam build
```

An image will be available on your host with the tag `airbyte/source-aws-iam:dev`.

### Running as a docker container

Then run any of the connector commands as follows:

```bash
docker run --rm airbyte/source-aws-iam:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-aws-iam:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-aws-iam:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-aws-iam:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
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
airbyte-ci connectors --name=source-aws-iam test
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

1. Make sure your changes are passing our test suite: `poe pytest` and `poe check-all` (or legacy: `airbyte-ci connectors --name=source-aws-iam test`)
2. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)):
   - bump the `dockerImageTag` value in in `metadata.yaml`
   - bump the `version` value in `pyproject.toml`
3. Make sure the `metadata.yaml` content is up to date.
4. Make sure the connector documentation and its changelog is up to date (`docs/integrations/sources/aws-iam.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.

# Fabrix

## AWS Role Assumption for Running Locally

When running the AWS IAM connector locally using launch.json, you need to assume the AWS role `arn:aws:iam::794038212761:role/FabrixScanner`.

Since the dev container doesn't have AWS CLI installed, you'll need to run the assume-role command from a terminal outside the dev container (e.g., your host machine), then copy the credentials to the dev container.

**From your host machine terminal (or any terminal with AWS CLI):**

```bash
# Run this one-liner to generate export commands
aws sts assume-role --role-arn arn:aws:iam::794038212761:role/FabrixScanner --role-session-name iam-connector-dev | jq -r '.Credentials | "export AWS_ACCESS_KEY_ID=\"\(.AccessKeyId)\"\nexport AWS_SECRET_ACCESS_KEY=\"\(.SecretAccessKey)\"\nexport AWS_SESSION_TOKEN=\"\(.SessionToken)\""'
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

# Note: Docker image building still requires airbyte-ci or manual Docker commands
# as this connector doesn't have a 'build' Poe task yet
```

### Legacy Method (Deprecated)

Run from Devcontainer (so airbyte-ci is runnable)

**Note**: `airbyte-ci` is deprecated. Use Poe commands above when available.

**Important**: Before building, ensure the `metadata.yaml` file is properly configured with all required fields including `dockerImageTag`. The connector now includes basic metadata configuration.

Build for arm
```bash
airbyte-ci connectors --name=source-aws-iam build --architecture linux/arm64 -t arm
```

Build for AMD64
```bash
airbyte-ci connectors --name=source-aws-iam build --architecture linux/amd64 -t amd
```

Export images to files - Extract for dev container to local docker for ECR push

```bash
# Export ARM image to tar file
docker save airbyte/source-aws-iam:arm -o aws-iam-connector-arm.tar

# Export AMD64 image to tar file
docker save airbyte/source-aws-iam:amd -o aws-iam-connector-amd.tar

# You can then copy these tar files to your host machine and load them into Docker
# On your host machine:
docker load -i aws-iam-connector-arm.tar
docker load -i aws-iam-connector-amd.tar
```

## Push to ECR

After loading the Docker images, you can tag and push them to your ECR repository:

```bash
# Login to ECR (ensure AWS credentials are configured)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 794038212761.dkr.ecr.us-east-1.amazonaws.com

# Version tag to use
VERSION="1.2.0"

# Tag and push ARM image with version and 'arm' tag
docker tag airbyte/source-aws-iam:arm 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:${VERSION}-arm
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:${VERSION}-arm

# Also push as 'arm' tag for latest reference
docker tag airbyte/source-aws-iam:arm 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:arm
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:arm

# Tag and push AMD64 image with version and 'amd' tag
docker tag airbyte/source-aws-iam:amd 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:${VERSION}-amd
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:${VERSION}-amd

# Also push as 'amd' tag for latest reference
docker tag airbyte/source-aws-iam:amd 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:amd
docker push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:amd

# Create and push a multi-architecture manifest
# This will create a manifest that points to both ARM and AMD images and selects the right one based on the cluster's architecture
docker manifest create 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:${VERSION} \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:${VERSION}-arm \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:${VERSION}-amd

# Annotate the manifest with architecture information
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:${VERSION} \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:${VERSION}-arm --os linux --arch arm64
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:${VERSION} \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:${VERSION}-amd --os linux --arch amd64

# Push the manifest
docker manifest push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:${VERSION}

# Also create a 'latest' manifest for convenience
docker manifest create 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:latest \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:arm \
  --amend 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:amd

# Annotate the latest manifest
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:latest \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:arm --os linux --arch arm64
docker manifest annotate 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:latest \
  794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:amd --os linux --arch amd64

# Push the latest manifest
docker manifest push 794038212761.dkr.ecr.us-east-1.amazonaws.com/airbyte/source-aws-iam/docker:latest
```

## Alternative: Using airbyte-cdk CLI

The `airbyte-cdk` CLI is now available and provides additional functionality:

```bash
# Install the airbyte-cdk CLI
uv tool install 'airbyte-cdk[dev]'

# Available commands
airbyte-cdk --help

# Manage secrets
airbyte-cdk secrets list
airbyte-cdk secrets fetch

# Other connector operations
airbyte-cdk build --connector source-aws-iam
airbyte-cdk test --connector source-aws-iam
```

For the most up-to-date commands, check the [Airbyte CDK documentation](https://docs.airbyte.com/platform/connector-development/cdk-python/).
