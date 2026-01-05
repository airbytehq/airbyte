---
sidebar_label: connector_info
title: airbyte._util.connector_info
---

Connector info classes for PyAirbyte.

Used for telemetry and logging.

## annotations

## asdict

## dataclass

## Any

## RuntimeInfoBase Objects

```python
@dataclass
class RuntimeInfoBase()
```

#### to\_dict

```python
def to_dict() -> dict[str, Any]
```

## WriterRuntimeInfo Objects

```python
@dataclass
class WriterRuntimeInfo(RuntimeInfoBase)
```

#### type

#### config\_hash

## ConnectorRuntimeInfo Objects

```python
@dataclass(kw_only=True)
class ConnectorRuntimeInfo(RuntimeInfoBase)
```

#### name

#### executor\_type

#### version

#### config\_hash

