# Manifest Server

An HTTP server for running Airbyte declarative connectors via their manifest files.

## Quick Start

### Installation

The manifest server is available as an extra dependency:

```bash
# Using Poetry (preferred)
poetry install --extras manifest-server

# Using pip
pip install airbyte-cdk[manifest-server]

# Using uv
uv pip install 'airbyte-cdk[manifest-server]'
```

### Running the Server

```bash
# Start the server (default port 8000)
manifest-server start

# Start on a specific port
manifest-server start --port 8080

# Or using Python module
python -m airbyte_cdk.manifest_server.cli.run start
```

The server will start on `http://localhost:8000` by default.

## API Endpoints

### `/v1/manifest/test_read`

Test reading from a specific stream in the manifest.

**POST** - Test stream reading with configurable limits for records, pages, and slices.

### `/v1/manifest/check`

Check configuration against a manifest.

**POST** - Validates connector configuration and returns success/failure status with message.

### `/v1/manifest/discover`

Discover streams from a manifest.

**POST** - Returns the catalog of available streams from the manifest.

### `/v1/manifest/resolve`

Resolve a manifest to its final configuration.

**POST** - Returns the resolved manifest without dynamic stream generation.

### `/v1/manifest/full_resolve`

Fully resolve a manifest including dynamic streams.

**POST** - Generates dynamic streams up to specified limits and includes them in the resolved manifest.

## Custom Components

The manifest server supports custom Python components, but this feature is **disabled by default** for security reasons.

### Enabling Custom Components

To allow custom Python components in your manifest files, set the environment variable:

```bash
export AIRBYTE_ENABLE_UNSAFE_CODE=true
```

## Authentication

The manifest server supports optional JWT bearer token authentication:

### Configuration

Set the environment variable to enable authentication:

```bash
export AB_JWT_SIGNATURE_SECRET="your-jwt-secret-key"
```

### Usage

When authentication is enabled, include a valid JWT token in the Authorization header:

```bash
curl -H "Authorization: Bearer <your-jwt-token>" \
  http://localhost:8000/v1/manifest/test_read
```

### Behavior

- **Without `AB_JWT_SIGNATURE_SECRET`**: All requests pass through
- **With `AB_JWT_SIGNATURE_SECRET`**: Requires valid JWT bearer token using HS256 algorithm

## OpenAPI Specification

The manifest server provides an OpenAPI specification for API client generation:

### Generating the OpenAPI Spec

```bash
# Generate OpenAPI YAML (default location)
manifest-server generate-openapi

# Generate to custom location
manifest-server generate-openapi --output /path/to/openapi.yaml
```

The generated OpenAPI specification is consumed by other applications and tools to:

- Generate API clients in various programming languages
- Create SDK bindings for the manifest server
- Provide API documentation and validation
- Enable integration with API development tools

### Interactive API Documentation

When running, interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run the manifest server tests from the repository root:

```bash
# Run all manifest server tests
poetry run pytest unit_tests/manifest_server/ -v
```

## Docker

The manifest server can be containerized using the included Dockerfile. Build from the repository root:

```bash
# Build from repository root (not from manifest_server subdirectory)
docker build -f airbyte_cdk/manifest_server/Dockerfile -t manifest-server .

# Run the container
docker run -p 8080:8080 manifest-server
```

Note: The container runs on port 8080 by default.

## Datadog APM

The manifest server supports Datadog APM tracing for monitoring and observability:

### Configuration

To enable Datadog tracing, set the environment variable:

```bash
export DD_ENABLED=true
```

This requires the `ddtrace` dependency, which is included in the `manifest-server` extra. For additional configuration options via environment variables, see [ddtrace configuration](https://ddtrace.readthedocs.io/en/stable/configuration.html).

### Usage

```bash
# Run with Datadog tracing enabled
DD_ENABLED=true manifest-server start
```

