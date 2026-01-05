---
sidebar_label: registry_spec
title: airbyte._util.registry_spec
---

Helper functions for fetching connector specs from the registry.

## annotations

## logging

## Any

## Literal

## jsonschema

## requests

## exc

## get\_connector\_metadata

## get\_version

#### logger

#### \_SPEC\_URL\_TEMPLATE

#### \_DEFAULT\_TIMEOUT

seconds

#### get\_connector\_spec\_from\_registry

```python
def get_connector_spec_from_registry(
        connector_name: str,
        *,
        version: str | None = None,
        platform: Literal["cloud", "oss"] = "oss",
        timeout: int = _DEFAULT_TIMEOUT) -> dict[str, Any] | None
```

Fetch connector spec from the registry.

**Arguments**:

- `connector_name` - Name of the connector (e.g., &quot;source-faker&quot;)
- `version` - Version of the connector. If None, uses latest_available_version from metadata.
- `platform` - Platform to fetch spec for (&quot;cloud&quot; or &quot;oss&quot;). Defaults to &quot;oss&quot;.
- `timeout` - Timeout in seconds for the HTTP request. Defaults to 10.
  

**Returns**:

  The connector spec JSON schema (connectionSpecification), or None if not found.
  

**Raises**:

- `AirbyteConnectorNotRegisteredError` - If the connector is not found in the registry.

#### validate\_connector\_config\_from\_registry

```python
def validate_connector_config_from_registry(
        connector_name: str,
        config: dict[str, Any],
        *,
        version: str | None = None,
        platform: Literal["cloud", "oss"] = "oss",
        timeout: int = _DEFAULT_TIMEOUT) -> tuple[bool, str | None]
```

Validate connector config against spec from registry.

**Arguments**:

- `connector_name` - Name of the connector (e.g., &quot;source-faker&quot;)
- `config` - Configuration dictionary to validate
- `version` - Version of the connector. If None, uses latest_available_version from metadata.
- `platform` - Platform to fetch spec for (&quot;cloud&quot; or &quot;oss&quot;). Defaults to &quot;oss&quot;.
- `timeout` - Timeout in seconds for the HTTP request. Defaults to 10.
  

**Returns**:

  Tuple of (is_valid, error_message). If valid, error_message is None.

#### \_\_all\_\_

