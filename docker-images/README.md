# Docker Images Definitions

This directory contains the Dockerfile resources needed to build Docker connector images.

## About these files

For each connector type, there are three files. Taking Java as the example:

- `Dockerfile.java-connector` - This file defines how to build a Java connector image.
- `Dockerfile.java-connector-base` - This file defines how to build the _base image_ for a Java connector.
- `Dockerfile.java-connector.dockerignore` - This file defines what local files from the context directory to ignore when building the connector image. The best practice is to ignore all files not needed, as this speeds up the build process and reduces the chance of busting layer caches from unrelated file changes.

## How to build images

### Prereqs (java only)

Java connectors require the `.tar` archive to be built before building the Docker image.

```bash
./gradlew :airbyte-integrations:connectors:{connector_name}:distTar
```

For example:

```bash
./gradlew :airbyte-integrations:connectors:source-mysql:distTar
```

### Testing the Base Image Build

The `test-base-image-build.sh` script can be used to build the base image.

`./test-base-image-build.sh CONNECTOR_TYPE [NEW_TAG]`

- `CONNECTOR_TYPE` should be `python` or `java`.
- `NEW_TAG` is the new tag to create, defaults to `dev`.

```bash
# These are identical, building the java base image with the 'dev' tag:
./test-base-image-build.sh java
./test-base-image-build.sh java dev

# These are identical, building the pyhton base image with the 'dev' tag:
./test-base-image-build.sh python
./test-base-image-build.sh python dev
```

### Testing a Connector Image Build

`./test-base-image-build.sh CONNECTOR_TYPE CONNECTOR_NAME`

- `CONNECTOR_TYPE` should be `python` or `java`.
- `CONNECTOR_NAME` is the name of the connector image to build.

```bash
./test-connector-image-build.sh java source-mysql
./test-connector-image-build.sh python source-hubspot
```

## Common Build Args

These are used within the `Dockerfile` definitions and within the image build test scripts.

- `BASE_IMAGE` - The image tag to use when building the connector.
- `CONNECTOR_NAME`: The connector name, in kebab format: `source-mysql`
- `EXTRA_BUILD_SCRIPT`: Optional `build_customization.py` script. An additional prereq-installation script that is custom to this connector.

## FAQ

### Why is `DOCKER_BUILDKIT=1` used in the build scripts?

This uses Buildkit in Docker, which allows us to use custom `.dockerignore` files, which is normally not allowed. With this env var set, docker will accept a `{Dockerfile-name}.dockerignore` in the same directory as the Dockerfile. This eliminates the need for us to store `.dockerignore` files redundantly in each connector directory.

### Why don't the base image definitions have a `.dockerignore` file?

The base images don't need to copy in any files from the host computer. That is why they don't require a dockerfile, since nothing is copied in, nothing is needed to be ignored.

### Where should I source the build args?

The build args should be scraped from the connector's `metadata.yml` file.
