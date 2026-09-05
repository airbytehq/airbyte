---
id: airbyte-validate
title: "airbyte.validate Module"
sidebar_label: "airbyte.validate"
toc_max_heading_level: 5
---

# `airbyte.validate` Module

Defines the `airbyte-lib-validate-source` CLI.

This tool checks if connectors are compatible with PyAirbyte.

### `full_tests` {#airbyte.validate.full_tests}

<ApiMember kind="function">

<ApiSignature>

```python
def full_tests(connector_name: str, sample_config: str) -> None
```

</ApiSignature>

Run full tests on the connector.

</ApiMember>

### `install_only_test` {#airbyte.validate.install_only_test}

<ApiMember kind="function">

<ApiSignature>

```python
def install_only_test(connector_name: str) -> None
```

</ApiSignature>

Test that the connector can be installed and spec can be printed.

</ApiMember>

### `run` {#airbyte.validate.run}

<ApiMember kind="function">

<ApiSignature>

```python
def run() -> None
```

</ApiSignature>

Handle CLI entrypoint for the `airbyte-lib-validate-source` command.

It's called like this:
> airbyte-lib-validate-source —connector-dir . -—sample-config secrets/config.json

It performs a basic smoke test to make sure the connector in question is PyAirbyte compliant:
* Can be installed into a venv
* Can be called via cli entrypoint
* Answers according to the Airbyte protocol when called with spec, check, discover and read.

</ApiMember>

### `validate` {#airbyte.validate.validate}

<ApiMember kind="function">

<ApiSignature>

```python
def validate(
    connector_dir: str,
    sample_config: str,
    *,
    validate_install_only: bool,
) -> None
```

</ApiSignature>

Validate a connector.

</ApiMember>