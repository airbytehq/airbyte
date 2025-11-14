# Connector Image Build and Push Action

This GitHub Action builds and pushes Docker images for Airbyte connectors (Python and manifest-only connectors). It was converted from the original `connector-image-build-push.yml` workflow to provide a reusable action that can be used across multiple workflows.

## Features

- **Multi-language Support**: Supports Python and manifest-only connectors
- **Smart Image Management**: Checks if images already exist before building/pushing
- **Multi-architecture Builds**: Builds images for both `linux/amd64` and `linux/arm64`
- **Security Scanning**: Includes vulnerability scanning with Anchore
- **Flexible Tagging**: Supports custom tags and automatic latest tag pushing
- **Dry Run Mode**: Build without pushing for testing purposes
- **Force Publishing**: Override existing images when needed

## Usage

### Basic Usage

```yaml
- name: Build and Push Connector
  uses: ./.github/actions/connector-image-build-push
  with:
    connector-name: 'source-faker'
    docker-hub-username: ${{ secrets.DOCKER_HUB_USERNAME }}
    docker-hub-password: ${{ secrets.DOCKER_HUB_PASSWORD }}
    dry-run: 'false'
```

### Advanced Usage

```yaml
- name: Build and Push Connector with Custom Settings
  uses: ./.github/actions/connector-image-build-push
  with:
    connector-name: 'source-postgres'
    registry: 'docker.io/airbyte'
    tag-override: 'v1.2.3'
    push-latest: 'true'
    force-publish: 'true'
    docker-hub-username: ${{ secrets.DOCKER_HUB_USERNAME }}
    docker-hub-password: ${{ secrets.DOCKER_HUB_PASSWORD }}
    dry-run: 'false'
```

### Dry Run for Testing

```yaml
- name: Test Build Connector Image
  uses: ./.github/actions/connector-image-build-push
  with:
    connector-name: 'destination-bigquery'
    dry-run: 'true'
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `connector-name` | Connector name (e.g., source-faker, destination-postgres) | **Yes** | - |
| `registry` | Docker registry | No | `docker.io/airbyte` |
| `tag-override` | Override the image tag. If not provided, uses tag from metadata.yaml | No | `""` |
| `push-latest` | Also push image with 'latest' tag | No | `false` |
| `dry-run` | Build but don't push (for testing) | No | `true` |
| `force-publish` | Force publish even if image exists (CAUTION!) | No | `false` |
| `docker-hub-username` | Docker Hub username for authentication | Yes | - |
| `docker-hub-password` | Docker Hub password for authentication | Yes | - |

## Outputs

| Output | Description |
|--------|-------------|
| `connector-name` | The validated connector name |
| `connector-type` | The connector type (python or manifest-only) |
| `connector-dir` | The connector directory path |
| `base-image` | The base image from metadata.yaml |
| `connector-version-tag` | The version tag used for the image |
| `connector-image-name` | The full image name with tag |
| `docker-tags` | All Docker tags used for pushing |
| `image-exists` | Whether the image already exists on the registry |
| `build-executed` | Whether the build was executed |
| `push-executed` | Whether the push was executed |

## How It Works

### 1. Validation Phase
- Validates that the connector directory exists
- Checks for `metadata.yaml` file
- Ensures connector language is supported (Python or manifest-only)
- Extracts base image and version information
- Validates registry and input combinations

### 2. Image Existence Check
- Queries Docker Hub API to check if the image already exists
- Uses exponential backoff retry logic for API reliability
- Makes build/push decisions based on existence and input flags

### 3. Build Phase (if needed)
- Sets up Docker Buildx for multi-architecture builds
- First builds a local image for testing
- Runs a `spec` command test to validate the image
- Then builds the multi-architecture image for publishing

### 4. Security Scan
- Runs Anchore vulnerability scanning on the built image
- Uses "high" severity cutoff but doesn't fail the build

### 5. Push Phase (if enabled)
- Authenticates with Docker Hub (if credentials provided)
- Pushes the multi-architecture image with specified tags
- Can include both versioned and latest tags

## Requirements

### Repository Structure
- Connector must be located in `airbyte-integrations/connectors/<connector-name>/`
- Must have a valid `metadata.yaml` file
- Must be a Python or manifest-only connector type

### Dependencies
- The action installs `uv`, `poethepoet`, and `yq` automatically
- Requires appropriate Dockerfile templates in `docker-images/`
- Needs access to `poe` tasks for connector metadata extraction

### Permissions
- `contents: read` - To checkout code
