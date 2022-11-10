# Fauna Airbyte Source

This is a source for Airbyte, a tool which allows users to export data from Fauna into a number of destinations, such as
Snowflake, Big Query, Redshift, and more. Airbyte allows this source to export to any destination, as Airbyte provides a
common data format that all destinations must use. This means that this connector can support all Airbyte destinations,
listed here.

The Source can be configured to export a single collection. To export another collection, you must setup multiple
sources within Airbyte. When I say “Fauna documents,” I really mean the documents in the collection.

# Sync Modes

The Sync Mode is how data should be extracted from the Fauna Source and how it should be written to the destination.

The Fauna Source provides support for 2 export modes, Full Sync and Incremental Sync. Destinations provide support for 3
import modes, Overwrite, Append, and Append Deduped. Only specific combinations of these modes are valid, and are listed
below.

## Full Sync - Overwrite

This imports all data from fauna, and clears the destination. This is the simplest mode, and is the slowest.

This is useful when you want to keep the destination synced with fauna at all times. This doesn’t provide any method of
finding the state of Fauna in the past.

## Full Sync - Append

This imports all data from fauna, and appends it to the destination. This is slightly more complex, and stores the most
data.

This allows for easy queries to lookup the state of the whole Fauna database at a specific date.

## Incremental Sync - Append

This pulls all new records from fauna, and appends them to the destination. This provides a list of all documents over
all time, but doesn’t have any notion of when an old document has been replaced.

For example, this is useful when you want to export a list of logs, and you only care about the new ones each day.

## Incremental Sync - Append Deduped

This pulls all new records from fauna, and appends them to the destination. This also uses a primary key, so it knows
which documents have become out of date. This allows for a query which can lookup the state of the whole Fauna database
at a specific date, and stores only the new data each sync.

This mode is slower to query, but stores the least about of data, and is the most useful.

# Record Format

Each document in Fauna is converted to an Airbyte record. Records are essentially rows, and they have a pre-defined list
of columns. Because Fauna doesn’t support a specific shape of data, we rely on the user to specify their data format
before any data can be exported.

## Required Columns

The resulting record will always have at least 2 columns, named ref and ts. The ref is a string, which is the document
ID. This can be used as a primary key in the destination, as it is a unique identifier for each document. The ts is an
integer, which is the time since the document was last modified, stored in microseconds since the Unix Epoch.

The record has 1 optional column, named data. If this is enabled by the user, then the resulting record will contain all
of the fauna document data within a column. This is most useful when you simply wish to dump all of your data in the
destination, and you don’t need to worry about re-shaping it.

## Additional Columns

The remaining columns are all user-configurable. When the user is setting up the connector, they can specify any number
of “Additional Columns.” Each column has a name, a type, and a path. All of these fields are specified by the user.

Additional columns are implemented to provide an easy way to flatten fauna data into columns. This is because Airbyte
doesn’t have another easy-to-use method of reshaping records, so we implemented this as part of the Fauna Source.

The name of the additional column is the name that it will have in the destination. Additional columns must have unique
names, and cannot be named ref, ts, or data, as that would conflict with the required columns.

The type of the additional column is the type in the destination. This is used so that destinations like Snowflake can
know the type of the column before any data is sent.

The path of the additional column is the path within each Fauna Document for this data. This allows you to pick out a
single field, even if it is nested in fauna, and store it in a column in the destination.

# Deleted Documents

If a document is deleted in Fauna, some users would like a record that within their destination. However, in the
destination, they would like to know that it existed for some time, and then was removed at a specific date.

To support this, we allow for an optional deleted_at column. This column will be null for all present documents, and is
set to a date after a document is deleted.

This deleted_at column is only supported in incremental syncs. If you combine this with the incremental append deduped
mode, you can easily query for documents that are present at a certain time.

# Data Serialization

Fauna documents have a lot of extra types. These types need to be converted into the Airbyte JSON format. Below is an
exhaustive list of how all fauna documents are converted.


|  Fauna Type   |                              Format                                 |                        Note                        |
| ------------- | ------------------------------------------------------------------- | -------------------------------------------------- |
| Document Ref  | `{ id: "id", "collection": "collection-name", "type": "document" }` |                                                    |
| Other Ref     | `{ id: "id", "type": "ref-type" }`                                  | This includes collection refs, database refs, etc. |
| Byte Array    | base64 url formatted string                                         |                                                    |
| Timestamp     | date-time, or an iso-format timestamp                               |                                                    |
| Query, SetRef | a string containing the wire protocol of this value                 | The wire protocol is not documented.               |

## Ref Types

Every ref is serialized as a JSON object with 2 or 3 fields, as listed above. The type field will be a string, which is
the type of the reference. For example, a document ref would have the type document, and a collection reference would
have the type collection.

For all other refs (for example if you stored the result of Collections()), the type will be "unknown".
