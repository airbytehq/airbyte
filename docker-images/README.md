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

## Tools for Local Connector Builds

You have a few options as of now:

### Gradle-based Image Builds

For Docker containers, you can run the `assemble` task to build the docker image for your connector.

Here are some convenient commands:

```bash
./gradlew :airbyte-integrations:connectors:<connector-name>:assemble to just output the Java artifact and docker image.
./gradlew :airbyte-integrations:connectors:<connector-name>:test to unit test.
./gradlew :airbyte-integrations:connectors:<connector-name>:build to unit test, integration test and assemble.
./gradlew :airbyte-integrations:connectors:<connector-name>:integrationTestJava to run integration test, which also runs assemble.
```

Note:

- _This is the preferred and recommended method of building Docker files for all JVM-based connectors._
- By default, this builds an image matching your local architecture (`arm64` on M-series Macs).

### `airbyte-cdk`-based Builds

This new method is faster, easier to type, and builds using the Dockerfiles in this directory, using the connector directory that is active:

```
cd airbyte-integrations/connectors/source-mysql
airbyte-cdk image build
```

Note:

- This method will automatically build arm64 and amd64 images - defaulting your `dev` image to `arm64` (since Mac M-series laptops are standard at Airbyte), while still providing an `amd64` based image, which you will need if uploading to `amd64`-based Platform instances.
- All connector types are supported using this method, since the code is only a thin wrapper around the `Dockerfile`-based build process.

## GitHub Actions Workflow for Building and Publishing Images

A GitHub Actions workflow is available for manually building and publishing connector base images. **This workflow is manual-only (`workflow_dispatch`) and does not run automatically on merge to `master`.** Publishing to DockerHub requires explicit opt-in (see below).

### Using the Workflow

1. Go to the [Docker Connector Image Publishing workflow](https://github.com/airbytehq/airbyte/actions/workflows/docker-connector-image-publishing.yml)
2. Click "Run workflow"
3. Configure the options:
   - **Connector Type**: `java` or `python`
   - **Image Type**: `base` (currently only base images are supported)
   - **Tag or Version Number**: The tag to apply to the image (e.g., `dev-test` or `2.0.2`)
   - **Repository Root**: Choose between:
     - `ghcr.io/airbytehq` for testing (this is the **default**)
     - `docker.io/airbyte` for production images on DockerHub
   - **Dry Run**: If enabled, builds the image but doesn't publish it (**enabled by default**)
   - **Require Security Check**: If enabled, fails the workflow if HIGH/CRITICAL vulnerabilities are found (enabled by default)

### Publishing to DockerHub

> **DockerHub publishing is opt-in.** The workflow defaults are intentionally safe: images are sent to GHCR with dry-run enabled. To actually publish a production image to DockerHub, you must change **both** of the following:
>
> 1. Set **Repository Root** to `docker.io/airbyte`
> 2. Uncheck **Dry Run**
>
> The `docker.io/airbyte` option requires a GitHub Environment approval (`hub.docker.com/r/airbyte`), providing an additional safeguard.

### Automated CI Testing (Pull Requests)

A separate workflow ([Dockerfile Tests](https://github.com/airbytehq/airbyte/actions/workflows/docker-connector-base-image-tests.yml)) runs automatically on pull requests that modify Dockerfiles in this directory. It builds and tests images against GHCR but **does not publish to DockerHub**.

### Key Features

- **Multi-Architecture Support**: Builds images for both `linux/amd64` and `linux/arm64` architectures
- **Vulnerability Scanning**: Automatically scans images for security vulnerabilities
- **Registry Options**: Supports publishing to either DockerHub or GitHub Container Registry
- **Dry-Run Mode**: Test builds without publishing (default)

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

