# Conduit Configuration Data Model

## Requirements

This section enumerates the full set of features we expect to give to these models. Only the ones with the (**MVP**) tag are to be included in the MVP.

### Persona: UI user

1. Test Connection (**MVP**)
1. Discover Schema (**MVP**)
1. Discover Schema with complex configuration (e.g. multi-nested file systems)
1. Sync Data
   1. Full refresh (**MVP**)
   1. Append only - no concept of a primary key, simply ads new data to the end of a table. (**MVP**)
   1. Full deltas - detects when a record is already present in the data set and updates it.
   1. Historical mode - detects when a record is already present, groups it on a primary key, but retains old and new versions of the record. ([fivetran historical mode docs](https://fivetran.com/docs/getting-started/feature/history-mode))
1. Support for "pull" connections. (**MVP**)
   1. These are all connections that can be polled.
1. Support for "push" connections.
   1. Fivetran supports push connections that accept data when the data provider emits the data (instead of polling for it).
1. Scheduled syncs
   1. Every X minutes / hours / days (**MVP**)
   1. Full linux crontab scheduling
1. Ability to use any singer tap / target by providing existing config, catalog, and state. (**MVP**)???
1. Transformations - allow basic transformations e.g. upper-casing, column name changes, hashing of values etc. Otherwise, data will be transported "as is".
1. Determine when a record was last synced in the target warehouse

### Persona: OSS Contributor

1. Add a source _without_ needing to write HTML. They should be responsible for only 2 things:
   1. Define Configuration: define a json object which describes which properties need to be collected by a user. Then the UI figures out how to render it.
   1. Implement: `testConnection`, `discoverSchema`, and `sync`. These functions should only rely on the configurations defined in the json and should return objects that match the interfaces that are described below.
   1. (Note: Not doing this means that we need to create custom html pages for each integration.)
1. Support "easy" integration of singer taps
1. A well-documented path that is easy to follow if you were the creator of a singer tap / target.
1. Documentation on how to contribute. Also describes the interface that the contributor must code against. (**MVP**)

## User Flow

The basic flow will go as follows:
* Insert credentials for a source.
* Receive feedback on whether Dataline was able to reach the source with the given credentials.
* Insert credentials for a destination.
* Receive feedback on whether Dataline was able to reach the destination with the given credentials.
* Show intent to connect source to destination.
* Receives schema of the source.
* Selects which part of the schema will be synced.
* Triggers a manual sync or inputs schedule on which syncs should take place.

## Source

### Source Types

#### SourceConnectionConfiguration

Any credentials needed to establish a connection with the data source. This configuration will look difference for each source. Dataline only enforces that it is valid json-schema. Here is an example of one might look like for a postgres tap.

```json
{
  "description": "all configuration information needed for creating a connection.",
  "type": "object",
  "required": ["host", "port", "user"],
  "properties": {
    "host": {
      "type": "string",
      "format": "hostname"
    },
    "port": {
      "type": "integer"
    },
    "user": {
      "type": "string",
      "minLength": 1,
      "maxLength": 63
    },
    "password": {
      "type": "string",
      "minLength": 1,
      "maxLength": 63
    },
    "database": {
      "type": "string"
    },
    "sshConnection": {
      "type": "object",
      "oneOf": [
        {
          "title": "https",
          "type": "null"
        },
        {
          "title": "ssh",
          "properties": {
            "sshHost": {
              "title": "ssh host",
              "type": "string"
            },
            "sshPort": {
              "title": "ssh port",
              "type": "integer"
            },
            "sshUser": {
              "title": "ssh user",
              "type": "string"
            },
            "publicKey": {
              "title": "public key",
              "type": "string"
            }
          }
        }
      ]
    }
  }
}
```

#### StandardConnectionStatus

This is the output of the `testConnection` method. It is the same schema for ALL taps.

```json
{
  "description": "describes the result of a 'test connection' action.",
  "type": "object",
  "required": ["status"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["success", "failure"]
    },
    "message": {
      "type": "string"
    }
  }
}
```

#### StandardDiscoveryOutput

This is the output of the `discoverSchema` method. It is the same schema for ALL taps.

The schema for the `schema` field. This will get reused elsewhere.

```json
{
  "id": "http://json-schema.org/geo",
  "$schema": "http://json-schema.org/draft-06/schema#",
  "description": "sync configurations needed to configure a postgres tap",
  "type": "object",
  "definitions": {
    "schema": {
      "description": "describes the available schema.",
      "type": "object",
      "properties": {
        "tables": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name", "columns"],
            "properties": {
              "name": {
                "type": "string"
              },
              "columns": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["name", "dataType"],
                  "properties": {
                    "name": {
                      "type": "string"
                    },
                    "dataType": {
                      "type": "string",
                      "enum": ["string", "number", "uuid", "boolean"]
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

```json
{
  "description": "describes the standard output for any discovery run.",
  "type": "object",
  "required": ["schema"],
  "properties": {
    "schema": {
      "description": "describes the available schema.",
      "$ref": "#/definitions/schema"
    }
  }
}
```

### Source Methods

The source object needs to be able to do 2 things:

#### testConnection

Tests that the docker image can reach that source given the information provided by the user.

```
testConnection(SourceConnectionConfiguration) => StandardConnectionStatus
```

#### discoverSchema

Detects the schema that exists in the data source. We want the output to be standardized for easy consumption by the UI.

(note: if irrelevant to an integration, this can be a no op)

(note: we will need to write a converter to and from singer catalog.json)

```
discoverSchema(SourceConnectionConfiguration) => StandardDiscoveryOutput
```

## Destination

### Destination Types

#### DestinationConnectionConfiguration

Same as [SourceConnectionConfiguration](#SourceConnectionConfiguration) but for the destination.

### Destination Methods

#### testConnection

Tests that the docker image can reach that destination given the information provided by the user.

```
testConnection(DestinationConnectionConfiguration) => StandardConnectionStatus
```

## Conduit

_aka: a "line", a "connection"._

### Conduit Types

#### StandardConduitConfiguration

Configuration that is the SAME for all tap / target combinations. Describes the sync mode (full refresh or append) as well what part of the schema will be synced.

```json
{
  "description": "configuration required for sync for ALL taps",
  "type": "object",
  "properties": {
    "syncMode": {
      "type": "string",
      "enum": ["full_refresh", "append"]
    },
    "schema": {
      "description": "describes the elements of the schema that will be synced.",
      "$ref": "#/definitions/schema"
    }
  }
}
```

(note: we may need to add some notion that some sources or destinations are only compatible with full_refresh)

#### StandardConduitOutput

This object tracks metadata on where the run ended. Our hope is that it can replace the ConduitState object (see [below](#ConduitState)) entirely. The reason to define this type now is so that in the UI we can provide feedback to the user on where the sync has gotten to.

```json
{
  "description": "standard information output by ALL taps for a sync step (our version of state.json)",
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["completed", "failed", "cancelled"]
    },
    "recordsSynced": {
      "type": "integer"
    },
    "version": {
      "type": "integer"
    },
    "tables": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "lastRecord": {
            "description": "blob of the last record",
            "type": "object"
          },
          "version": {
            "type": "integer"
          }
        }
      }
    }
  }
}
```

#### ConduitState

This field will be treated as a json blob that will _only_ be used inside the implementation of the integration. This is our escape strategy to handle any special state that needs to be tracked specially for specific taps.

#### ScheduleConfiguration

This object defines the schedule for a given conduit. It is the same for all taps / targets.

```json
{
  "timeUnit": "days",
  "units": 4
}
```

### Conduit Methods

The connected source object needs to be able to do 2 things:

### (manual) sync

This includes detecting if there is in fact new data to sync. if there is, it transfers it to the destination.

```
sync(
    SourceConnectionConfiguration,
    DestinationConnectionConfiguration,
    StandardConduitConfiguration,
    StandardSyncOutput,
    ConduitState
) => [StandardSyncOutput, ConduitState]
```

#### scheduledSync

This feature will require some additional configuration that will be standard across all pull sources. syncs triggered by scheduled sync will consume all of the same configuration as the manual sync.

```
scheduleSync(
    ScheduleConfiguration,
    SourceConnectionConfiguration,
    DestinationConnectionConfiguration,
    StandardConduitConfiguration,
    StandardSyncOutput,
    ConduitState
) => void
```
