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

### Building a Connector Image

```bash
DOCKER_BUILDKIT=1
ARCH=amd64

docker build \
    --platform linux/${ARCH} \
    --label io.airbyte.version=3.11.15\
    --label io.airbyte.name=airbyte/source-mysql \
    --file ../../../docker-images/Dockerfile.java-connector \
    --build-arg=BASE_IMAGE=docker.io/airbyte/java-connector-base:2.0.1@sha256:ec89bd1a89e825514dd2fc8730ba299a3ae1544580a078df0e35c5202c2085b3 \
    --build-arg=CONNECTOR_NAME=source-mysql \
    --build-arg=EXTRA_BUILD_SCRIPT= \
    -t airbyte/source-mysql:dev-${ARCH} .
```

## Common Build Args

- `BASE_IMAGE` - The image tag to use when building the connector.
- `CONNECTOR_NAME`: The connector name, in kebab format: `source-mysql`
- `EXTRA_BUILD_SCRIPT`: Optional `build_customization.py` script. An additional prereq-installation script that is custom to this connector.

## FAQ

### Why is `DOCKER_BUILDKIT=1` needed?

This uses Buildkit in Docker, which allows us to use custom `.dockerignore` files, which is normally not allowed. Instead, docker will accept a `{Dockerfile-name}.dockerignore` in the same directory as the Dockerfile, saving us from needing to store `.dockerignore` files redundantly in each connector directory.

### Why don't the base image definitions have a `.dockerignore` file

The base images don't need to copy in any files from the host computer. That is why they don't require a dockerfile, since nothing is copied in, nothing is needed to be ignored.

### Where should I source the build args?

The build args should be scraped from the connector's `metadata.yml` file.
