---
id: airbyte_agent_sdk-constants
title: airbyte_agent_sdk.constants
---

Module airbyte_agent_sdk.constants
==================================
Constants used throughout the Airbyte SDK.

This module centralizes configuration defaults and commonly used values to improve
maintainability and consistency across the codebase.

Variables
---------

`DEFAULT_CONNECT_TIMEOUT`
:   Default timeout for establishing a new connection (seconds).

`DEFAULT_INITIAL_DELAY_SECONDS`
:   Default initial delay for retry backoff (seconds).

`DEFAULT_MAX_CONNECTIONS`
:   Maximum number of concurrent HTTP connections to maintain in the pool.

`DEFAULT_MAX_DELAY_SECONDS`
:   Default maximum delay for retry backoff (seconds).

`DEFAULT_MAX_KEEPALIVE_CONNECTIONS`
:   Maximum number of keepalive connections to maintain in the pool.

`DEFAULT_POOL_TIMEOUT`
:   Default timeout for acquiring a connection from the pool (seconds).

`DEFAULT_READ_TIMEOUT`
:   Default timeout for reading response data (seconds).

`DEFAULT_REQUEST_TIMEOUT`
:   Default overall request timeout (seconds).

`DEFAULT_WRITE_TIMEOUT`
:   Default timeout for writing request data (seconds).

`MILLISECONDS_PER_SECOND`
:   Conversion factor from seconds to milliseconds.

`MINIMUM_PYTHON_VERSION`
:   Minimum Python version required to run the SDK.

`OPENAPI_DEFAULT_VERSION`
:   Default version string for connectors that don't specify a version.

`OPENAPI_VERSION_PREFIX`
:   Required OpenAPI version prefix. Only 3.1.x specifications are supported.