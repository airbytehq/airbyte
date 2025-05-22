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

- While connectors are being migrating from `airbyte-ci` to the new Dockerfile images here in this directory, some connectors will build using the legacy `airbyte-ci` method and some will build using the new `Dockerfile`-based method.
- _This is the preferred and recommended method of building Docker files for all JVM-based connectors._
- By default, this builds an image matching your local architecture (`arm64` on M-series Macs).

### `airbyte-ci`-based Image Builds

We are in the process of phasing this out, but for now it is still the official method of building connector images:

`airbyte-ci connectors --connector-name=source-foo build`

Note:

- This method is _not_ using the Dockerfile images in this directory. Instead it is using custom Dagger code, which is currently at its end-of-life (EOL) and will no longer be supported going forward.
- You need to be careful about which platform(s) you are building for in this method. Use `--help` for info on how to build `arm64` images vs `amd64` images, etc.
- This is not guaranteed to work for JVM connectors that have migrated over to the new gradle flow. Gradle commands are recommended instead.
### `airbyte-cdk`-based Builds

This new method is faster, easier to type, and builds using the Dockerfiles in this directory, using the connector directory that is active:

```
cd airbyte-integrations/connectors/source-mysql
airbyte-cdk image build
```

Note:
- Until `airybte-ci` is phased out, the images created this way will not exactly match the ones that would be built by the connector publish flow.
- This method will automatically build arm64 and amd64 images - defaulting your `dev` image to `arm64` (since Mac M-series laptops are standard at Airbyte), while still providing an `amd64` based image, which you will need if uploading to `amd64`-based Platform instances.
- All connector types are supported using this method, since the code is only thin wrapper around the `Dockerfile`-based build process.

## GitHub Actions Workflow for Building and Publishing Images

A GitHub Actions workflow is now available for manually building and publishing connector base images:

### Using the Workflow

1. Go to the [Docker Connector Image Publishing workflow](https://github.com/airbytehq/airbyte/actions/workflows/docker-connector-image-publishing.yml)
2. Click "Run workflow"
3. Configure the options:
   - **Connector Type**: `java` or `python`
   - **Image Type**: `base` (currently only base images are supported)
   - **Tag or Version Number**: The tag to apply to the image (e.g., `dev-test` or `2.0.2`)
   - **Repository Root**: Choose between:
     - `docker.io/airbyte` for production images
     - `ghcr.io/airbytehq` for testing
   - **Dry Run**: If enabled, builds the image but doesn't publish it
   - **Require Security Check**: If enabled, fails the workflow if HIGH/CRITICAL vulnerabilities are found

### Key Features

- **Multi-Architecture Support**: Builds images for both `linux/amd64` and `linux/arm64` architectures
- **Vulnerability Scanning**: Automatically scans images for security vulnerabilities
- **Registry Options**: Supports publishing to either DockerHub or GitHub Container Registry
- **Dry-Run Mode**: Test builds without publishing

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

