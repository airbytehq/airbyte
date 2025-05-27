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

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
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

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

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

1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=source-s3 test`
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

## Fabrix Build

Run from Devcontainer (so airbyte-ci is runnable)

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
# Export ARM image to tar file
docker save airbyte/source-s3:arm -o s3-connector-arm.tar

# Export AMD64 image to tar file
docker save airbyte/source-s3:amd -o s3-connector-amd.tar

# You can then copy these tar files to your host machine and load them into Docker
# On your host machine:
docker load -i s3-connector-arm.tar
docker load -i s3-connector-amd.tar
```

## Push to ECR

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
