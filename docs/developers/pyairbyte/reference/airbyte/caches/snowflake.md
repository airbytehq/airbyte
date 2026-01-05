---
sidebar_label: snowflake
title: airbyte.caches.snowflake
---

A Snowflake implementation of the PyAirbyte cache.

## Usage Example

__Password connection:__


```python
from airbyte as ab
from airbyte.caches import SnowflakeCache

cache = SnowflakeCache(
    account="myaccount",
    username="myusername",
    password=ab.get_secret("SNOWFLAKE_PASSWORD"), # optional
    warehouse="mywarehouse",
    database="mydatabase",
    role="myrole",
    schema_name="myschema",
)
```

__Private key connection:__


```python
from airbyte as ab
from airbyte.caches import SnowflakeCache

cache = SnowflakeCache(
    account="myaccount",
    username="myusername",
    private_key=ab.get_secret("SNOWFLAKE_PRIVATE_KEY"),
    private_key_passphrase=ab.get_secret("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"), # optional
    warehouse="mywarehouse",
    database="mydatabase",
    role="myrole",
    schema_name="myschema",
)
```

__Private key path connection:__


```python
from airbyte as ab
from airbyte.caches import SnowflakeCache

cache = SnowflakeCache(
    account="myaccount",
    username="myusername",
    private_key_path="path/to/my/private_key.pem",
    private_key_passphrase=ab.get_secret("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"), # optional
    warehouse="mywarehouse",
    database="mydatabase",
    role="myrole",
    schema_name="myschema",
)
```

## annotations

## ClassVar

## DestinationSnowflake

## SnowflakeConfig

## SnowflakeSqlProcessor

## CacheBase

## snowflake\_cache\_to\_destination\_configuration

## RecordDedupeMode

## SqlProcessorBase

## SnowflakeCache Objects

```python
class SnowflakeCache(SnowflakeConfig, CacheBase)
```

Configuration for the Snowflake cache.

#### dedupe\_mode

#### \_sql\_processor\_class

#### paired\_destination\_name

#### paired\_destination\_config\_class

#### paired\_destination\_config

```python
@property
def paired_destination_config() -> DestinationSnowflake
```

Return a dictionary of destination configuration values.

#### \_\_all\_\_

