# Conduit Configuration Data Model

## Requirements

This section enumerates the full set of features we expect to give to these models. Only the ones with the (**MVP**) tag are to be included in the MVP.

### Persona: UI user

1. Test Connection (**MVP**)
1. Discover Schema (**MVP**)
1. Discover Schema with complex configuration (e.g. multi-nested file systems)
1. Sync Data
   1. Full refresh (**MVP**)
   1. Append only - no concept of a primary key, simply ads new data to the end of a table. (**MVP**)???
   1. Full deltas - detects when a record is already present in the data set and updates it. (**MVP**)???
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
      1. **Note: For MVP we will only be supporting declaring the needed configuration, not the auto-rendering the UI. Someone who is implementing an integration will need to write the HTML pages for test connection and sync configurations.**
   1. Implement: test connector, discover schema, and sync. These functions should only rely on the configurations defined in the json and should return objects that match the interfaces that are described below.
   1. (Note: Not doing this means that we need to create custom html pages for each integration.)
1. Support "easy" integration of singer taps
1. A well-documented path that is easy to follow if you were the creator of a singer tap / target.
1. Documentation on how to contribute. Also describes the interface that the contributor must code against. (**MVP**)

## Two-Step Configuration

Some singer taps allow the user to put in some subset of the needed configuration before running a "discovery" process. The output of this discovery process is a json object (catalog.json) that can then optionally be edited and used as input configuration for the sync process. e.g. [singer postgres tap](https://github.com/singer-io/tap-postgres).

Fivetran has a similar feature, where at configuration time, it detects the scheme of the data source and allows a user to select a subset of the columns discovered.

## Source

The source object needs to be able to do 2 things:

1. **test connection**: run a process that tests that given the information provided by the user, the docker image can reach that source.

   1. _input_: any credentials needed to establish a connection with the data source. this is defined _per_ source.

      e.g. for postgres source

      ```json
      {
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
            "validation": "^.{0,63}$",
            "_validation": "string less than or equal to characters"
          },
          "password": {
            "type": "string",
            "validation": "^.{0,63}$",
            "_validation": "string less than or equal to characters"
          },
          "database": {
            "type": "string"
          }
        }
      }
      ```

   1. _output_: information on whether a connection was successful. this interface is the _same_ for all sources.

      ```json
      {
        "connectionStatus": "failed",
        "errorMessage": "invalid username"
      }
      ```

   (`connectionStatus` would be an enum of: success and failed)

1. **schema discovery**: run a process that can detect the schema that exists in the data source. (note: if irrelevant to an integration, this can be a no op)
   1. input: while in the future we may potentially want to allow for custom configuration for now we will assume there is no additional user-specified configuration allowed.
      1. the test_connection configuration will be available to the schema discovery function.
   1. output: while in the future we may potentially want to allow for a custom output. for now we will use this standard output.
      ```json
      {
        "tables": [
          {
            "tableName": "users",
            "columns": [
              {
                "columnName": "user_id",
                "dataType": "uuid"
              },
              {
                "columnName": "name",
                "dataType": "string"
              },
              {
                "columnName": "parking_lot_number",
                "dataType": "int"
              }
            ]
          }
        ]
      }
      ```

## Connected Source

_note: picking a purposefully verbose name here for clarity. we should change it. this is an object that describes the configuration and state of data transfer to a single destination. aka a "line", a "connection"_

The connected source object needs to be able to do 2 things:

1.  **(manual) sync**: this includes detecting if there is in fact new data to sync. if there is, it transfers it to the destination.

    1. _input_: part of this configuration will be specific to connection.

       1. connection specific configuration:
          e.g. for postgres. allows for an optional configuration where the user can specify which columns should by synced.

          ```json
          {
            "required": [],
            "properties": {
              "extraction_configuration": {
                "type": "object",
                "properties": {
                  "tables": {
                    "type": "list",
                    "items": {
                      "type": "object",
                      "properties": {
                        "tableName": {
                          "type": "string"
                        },
                        "columns": {
                          "type": "list",
                          "items": {
                            "type": "string"
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

       1. standard configuration: will include the configuration provided in test_connection as well as the following.
          ```json
          {
            "sync_mode": "full_refresh"
          }
          ```
          (`sync_mode` is an enum of full_refresh and incremental)

    1. _output_: the sync will output one standard object that is the same for all taps. then optionally it will also return one that is tap-specific.
        1. standard:

           ```json
           {
             "status": "completed",
             "records_synced": "10",
             "checkpoint": 1596143669
           }
           ```
        1. tap-specific:
        

       (`status` will be an enum of: completed, failed, cancelled)

1.  **scheduled sync**: this feature will require some additional configuration that will be standard across all pull sources. syncs triggered by scheduled sync will consume all of the same configuration as the manual sync.
    ```json
    {
      "timeUnit": "days",
      "units": 4
    }
    ```
