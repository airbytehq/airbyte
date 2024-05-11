# A Beginner's Guide to the AirbyteCatalog

## Overview

The goal of this article is to make the `AirbyteCatalog` approachable to someone contributing to Airbyte for the first time. If you are looking to get deeper into the details of the catalog, you can read our technical specification on it [here](airbyte-protocol.md#catalog).

The goal of the `AirbyteCatalog` is to describe _what_ data is available in a source. The goal of the `ConfiguredAirbyteCatalog` is to, based on an `AirbyteCatalog`, specify _how_ data from the source is replicated.

## Contents

This article will illustrate how to use `AirbyteCatalog` via a series of examples. We recommend reading the [Database Example](#database-example) first. The other examples, will refer to knowledge described in that section. After that, jump around to whichever example is most pertinent to your inquiry.

- [Postgres Example](#database-example)
- [API Example](#api-examples)
  - [Static Streams Example](#static-streams-example)
  - [Dynamic Streams Example](#dynamic-streams-example)
- [Nested Schema Example](#nested-schema-example)

In order to understand in depth how to configure incremental data replication, head over to the [incremental replication docs](/using-airbyte/core-concepts/sync-modes/incremental-append.md).

## Database Example

Let's jump into an example using a relational database. We will assume we have a database with the following schema:

```sql
CREATE TABLE "airlines" (
    "id"   INTEGER,
    "name" VARCHAR
);

CREATE TABLE "pilots" (
    "id"   INTEGER,
    "airline_id" INTEGER,
    "name" VARCHAR
);
```

### AirbyteCatalog

We would represent this data in a catalog as follows:

```javascript
{
  "streams": [
    {
      "name": "airlines",
      "supported_sync_modes": [
        "full_refresh",
        "incremental"
      ],
      "source_defined_cursor": false,
      "json_schema": {
        "type": "object",
        "properties": {
          "id": {
            "type": "number"
          },
          "name": {
            "type": "string"
          }
        }
      }
    },
    {
      "name": "pilots",
      "supported_sync_modes": [
        "full_refresh",
        "incremental"
      ],
      "source_defined_cursor": false,
      "json_schema": {
        "type": "object",
        "properties": {
          "id": {
            "type": "number"
          },
          "airline_id": {
            "type": "number"
          },
          "name": {
            "type": "string"
          }
        }
      }
    }
  ]
}
```

The catalog is structured as a list of `AirbyteStream`. In the case of a database a "stream" is analogous to a table. \(For APIs the mapping can be a more creative; we will discuss it later in [API Examples](beginners-guide-to-catalog.md#API-Examples)\)

Let's walk through what each field in a stream means.

- `name` - The name of the stream.
- `supported_sync_modes` - This field lists the type of data replication that this source supports. The possible values in this array include `FULL_REFRESH` \([docs](/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite.md)\) and `INCREMENTAL` \([docs](/using-airbyte/core-concepts/sync-modes/incremental-append.md)\).
- `source_defined_cursor` - If the stream supports `INCREMENTAL` replication, then this field signals whether the source can figure out how to detect new records on its own or not.
- `json_schema` - This field is a [JsonSchema](https://json-schema.org/understanding-json-schema) object that describes the structure of the data. Notice that each key in the `properties` object corresponds to a column name in our database table.

Now we understand _what_ data is available from this source. Next we will configure _how_ we want to replicate that data.

### ConfiguredAirbyteCatalog

Let's say that we do not care about replicating the pilot data at all. We do want to replicate the airlines data as a `FULL_REFRESH`. Here's what our `ConfiguredAirbyteCatalog` would look like.

```javascript
{
  "streams": [
    {
      "sync_mode": "FULL_REFRESH",
      "stream": {
        "name": "airlines",
        "supported_sync_modes": [
          "full_refresh",
          "incremental"
        ],
        "source_defined_cursor": false,
        "json_schema": {
          "type": "object",
          "properties": {
            "id": {
              "type": "number"
            },
            "name": {
              "type": "string"
            }
          }
        }
      }
    }
  ]
}
```

Just as with the `AirbyteCatalog` the `ConfiguredAirbyteCatalog` contains a list. This time it is a list of `ConfiguredAirbyteStream` \(instead of just `AirbyteStream`\).

Let's walk through each field in the `ConfiguredAirbyteStream`:

- `sync_mode` - This field must be one of the values that was in `supported_sync_modes` in the `AirbyteStream` - Configures which sync mode will be used when data is replicated.
- `stream` - Hopefully this one looks familiar! This field contains an `AirbyteStream`. It should be _identical_ to the one we saw in the `AirbyteCatalog`.
- `cursor_field` - When `sync_mode` is `INCREMENTAL` and `source_defined_cursor = false`, this field configures which field in the stream will be used to determine if a record should be replicated or not. Read more about this concept in our [documentation of incremental replication](/using-airbyte/core-concepts/sync-modes/incremental-append.md).

### Summary of the Postgres Example

When thinking about `AirbyteCatalog` and `ConfiguredAirbyteCatalog`, remember that the `AirbyteCatalog` describes _what_ data is present in the source \(and metadata around what replication configuration it can support\). It is output by the `discover` method of source. It should be treated as an immutable object; if you are ever manually editing a catalog outside of a source, you've gone off the rails. The `ConfiguredAirbyteCatalog` is a mutable configuration object that specifies, for each `AirbyteStream`, _how_ \(and if\) it should be replicated. The `ConfiguredAirbyteCatalog` does this by wrapping each `AirbyteStream` in an `AirbyteCatalog` inside a `ConfiguredAirbyteStream`.

## API Examples

The `AirbyteCatalog` offers the flexibility in how to model the data for an API. In the next two examples, we will model data from the same API--a stock ticker--in two different ways. In the first, the source will return a single stream called `ticker`, and in the second, the source with return a stream for each stock symbol it is configured to retrieve data for. Each stream's name will be a stock symbol.

### Static Streams Example

Let's imagine we want to create a basic Stock Ticker source. The goal of this source is to take in a single stock symbol and return a single stream. We will call the stream `ticker` and will contain the closing price of the stock. We will assume that you already have a rough understanding of the `AirbyteCatalog` and the `ConfiguredAirbyteCatalog` from the [previous database example](beginners-guide-to-catalog.md#Database-Example).

#### AirbyteCatalog

Here is what the `AirbyteCatalog` might look like.

```javascript
{
  "streams": [
    {
      "name": "ticker",
      "supported_sync_modes": [
        "full_refresh",
        "incremental"
      ],
      "source_defined_cursor": false,
      "json_schema": {
        "type": "object",
        "properties": {
          "symbol": {
            "type": "string"
          },
          "price": {
            "type": "number"
          },
          "date": {
            "type": "string"
          }
        }
      }
    }
  ]
}
```

This catalog looks pretty similar to the `AirbyteCatalog` that we created for the [Database Example](beginners-guide-to-catalog.md#Database-Example). For the data we've picked here, you can think about `ticker` as a table and then each field it returns in a record as a column, so it makes sense that these look pretty similar.

#### ConfiguredAirbyteCatalog

The `ConfiguredAirbyteCatalog` follows the same rules as we described in the [Database Example](beginners-guide-to-catalog.md#Database-Example). It just wraps the `AirbyteCatalog` described above.

### Dynamic Streams Example

Now let's build a stock ticker source that handles returning ticker data for _multiple_ stocks. The name of each stream will be the stock symbol that it represents.

#### AirbyteCatalog

```javascript
{
  "streams": [
    {
      "name": "TSLA",
      "supported_sync_modes": [
        "full_refresh",
        "incremental"
      ],
      "source_defined_cursor": false,
      "json_schema": {
        "type": "object",
        "properties": {
          "symbol": {
            "type": "string"
          },
          "price": {
            "type": "number"
          },
          "date": {
            "type": "string"
          }
        }
      }
    },
    {
      "name": "FB",
      "supported_sync_modes": [
        "full_refresh",
        "incremental"
      ],
      "source_defined_cursor": false,
      "json_schema": {
        "type": "object",
        "properties": {
          "symbol": {
            "type": "string"
          },
          "price": {
            "type": "number"
          },
          "date": {
            "type": "string"
          }
        }
      }
    }
  ]
}
```

This example provides another way of thinking about exposing data in a source. As a developer building a source, you can model the `AirbyteCatalog` for a source however makes most sense to the use case you are trying to fulfill.

## Nested Schema Example

Often, a data source contains "nested" data. In other words this is data where each record contains other objects nested inside it. Cases like this cannot be easily modeled just as tables / columns. This is why Airbyte uses JsonSchema to model the schema of its streams.

Let's imagine we are modeling a flight object. A flight object might look like this:

```javascript
{
  "airline": "alaska",
  "origin": {
    "airport_code": "SFO",
    "terminal": "2",
    "gate": "G23"
  },
  "destination": {
    "airport_code": "JFK",
    "terminal": "7",
    "gate": "1"
  }
}
```

The `AirbyteCatalog` would look like this:

```javascript
{
  "streams": [
    {
      "name": "flights",
      "supported_sync_modes": [
        "full_refresh"
      ],
      "source_defined_cursor": false,
      "json_schema": {
        "type": "object",
        "properties": {
          "airline": {
            "type": "string"
          },
          "origin": {
            "type": "object",
            "properties": {
              "airport_code": {
                "type": "string"
              },
              "terminal": {
                "type": "string"
              },
              "gate": {
                "type": "string"
              }
            }
          },
          "destination": {
            "type": "object",
            "properties": {
              "airport_code": {
                "type": "string"
              },
              "terminal": {
                "type": "string"
              },
              "gate": {
                "type": "string"
              }
            }
          }
        }
      }
    }
  ]
}
```

Because Airbyte uses JsonSchema to model the schema of streams, it is able to handle arbitrary nesting of data in a way that a table / column based model cannot.
