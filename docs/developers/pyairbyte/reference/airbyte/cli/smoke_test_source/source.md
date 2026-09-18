---
id: airbyte-cli-smoke_test_source-source
title: "airbyte.cli.smoke_test_source.source Module"
sidebar_label: "airbyte.cli.smoke_test_source.source"
toc_max_heading_level: 5
---

# `airbyte.cli.smoke_test_source.source` Module

Smoke test source for destination regression testing.

This source generates synthetic test data covering common edge cases
that break destinations: type variations, null handling, naming edge cases,
schema variations, and batch size variations.

Predefined scenarios are always available. Additional scenarios can be
injected dynamically via the ``custom_scenarios`` config field.

.. warning::
    This module is experimental and subject to change without notice.
    The APIs and behavior may be modified or removed in future versions.

### `SourceSmokeTest` {#airbyte.cli.smoke_test_source.source.SourceSmokeTest}

<ApiMember kind="class">

<ApiSignature>

```python
class SourceSmokeTest()
```

</ApiSignature>

Smoke test source for destination regression testing.

Generates synthetic data across predefined scenarios that cover
common destination failure patterns. Supports dynamic injection
of additional scenarios via the ``custom_scenarios`` config field.

#### Bases {#airbyte.cli.smoke_test_source.source.SourceSmokeTest--bases}

`airbyte_cdk.sources.source.Source`
#### Methods {#airbyte.cli.smoke_test_source.source.SourceSmokeTest--methods}

##### `check` {#airbyte.cli.smoke_test_source.source.SourceSmokeTest.check}

<ApiMember kind="method">

<ApiSignature>

```python
def check(
    self,
    logger: logging.Logger,
    config: Mapping[str, Any],
) -> AirbyteConnectionStatus
```

</ApiSignature>

Validate the configuration.

</ApiMember>

##### `discover` {#airbyte.cli.smoke_test_source.source.SourceSmokeTest.discover}

<ApiMember kind="method">

<ApiSignature>

```python
def discover(
    self,
    logger: logging.Logger,
    config: Mapping[str, Any],
) -> AirbyteCatalog
```

</ApiSignature>

Return the catalog with all test scenario streams.

</ApiMember>

##### `read` {#airbyte.cli.smoke_test_source.source.SourceSmokeTest.read}

<ApiMember kind="method">

<ApiSignature>

```python
def read(
    self,
    logger: logging.Logger,
    config: Mapping[str, Any],
    catalog: ConfiguredAirbyteCatalog,
    state: list[Any] | None = None,
) -> Iterable[AirbyteMessage]
```

</ApiSignature>

Read records from selected smoke test streams.

</ApiMember>

##### `spec` {#airbyte.cli.smoke_test_source.source.SourceSmokeTest.spec}

<ApiMember kind="method">

<ApiSignature>

```python
def spec(
    self,
    logger: logging.Logger,
) -> airbyte_cdk.models.airbyte_protocol.ConnectorSpecification
```

</ApiSignature>

Return the connector specification.

</ApiMember>

</ApiMember>