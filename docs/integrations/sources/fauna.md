# Fauna

This page guides you through setting up a [Fauna](https://fauna.com/) source.

# Overview

The Fauna source supports the following sync modes:

- **Full Sync** - export all the data from a Fauna collection.
- **Incremental Sync** - export data incrementally from a Fauna collection.

You will need to create a seperate source per collection you want to export.

## Preliminary setup

1. Choose the Fauna collection you want to export and enter that in the "Collection" field on the left.
2. Enter the domain of the collection's database you are exporting. The url can be found on [the docs](https://docs.fauna.com/fauna/current/learn/understanding/region_groups#how-to-use-region-groups).

## Full Sync

Follow these steps if you want full sync for this connection.

1. Create a role that can read the collection you are exporting. You can create the role with the in your dashboard or the [fauna shell](https://github.com/fauna/fauna-shell) with the following code:
```javascript
CreateRole({
  name: "airbyte-readonly",
  privileges: [{
    resource: Collection("COLLECTION_NAME"),
    actions: { read: true }
  }],
})
```
2. Create a key with that role. You can create a key using this code:
```javascript
CreateKey({
  name: "airbyte-readonly",
  role: Role("airbyte-readonly"),
})
```
3. Copy the `secret` output by the `CreateKey` command and enter that as the "Fauna Secret" on the left.

## Incremental Sync

Follow these steps if you want incremental sync for this connection.

1. Create the "Incremental Sync Index" which contains the `ts` and `ref` of the document as the first two values and no terms. This will enable the Fauna source to perform incremental syncs. You can create the index with the [fauna shell](https://github.com/fauna/fauna-shell) or in your dashboard with the following code:
```javascript
CreateIndex({
  name: "INDEX_NAME",
  source: Collection("COLLECTION_NAME"),
  terms: [],
  values: [
    { "field": "ts" },
    { "field": "ref" }
  ]
})
```
2. Create a role that can read the collection, the index, and the metadata of all indexes. It needs access to index metadata in order to validate the index settings. You can create the role with this code:
```javascript
CreateRole({
  name: "airbyte-readonly",
  privileges: [
    {
      resource: Collection("COLLECTION_NAME"),
      actions: { read: true }
    },
    {
      resource: Index("INDEX_NAME"),
      actions: { read: true }
    },
    {
      resource: Indexes(),
      actions: { read: true }
    }
  ],
})
```
3. Create a key with that role. You can create a key using this code:
```javascript
CreateKey({
  name: "airbyte-readonly",
  role: Role("airbyte-readonly"),
})
```
4. Copy the `secret` output by the `CreateKey` command and enter that as the "Fauna Secret" on the left.

## Export Formats

This section captures export formats for all special case data stored in Fauna. This list is exhaustive.

Note that the `ref` column in the exported database will just contain the ref id of every document.
Because we can only export one collection, it is inferred that this ref is a document which is part
of the collection being exported.

|                                  Fauna Type                                         |                             Format                                  |                        Note                        |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------- | -------------------------------------------------- |
| [Document Ref](https://docs.fauna.com/fauna/current/learn/understanding/types#ref)  | `{ id: "id", "collection": "collection-name", "type": "document" }` |                                                    |
| [Other Ref](https://docs.fauna.com/fauna/current/learn/understanding/types#ref)     | `{ id: "id", "type": "ref-type" }`                                  | This includes collection refs, database refs, etc. |
| [Byte Array](https://docs.fauna.com/fauna/current/learn/understanding/types#byte)   | base64 url formatting                                               |                                                    |
| [Timestamp](https://docs.fauna.com/fauna/current/learn/understanding/types#date)    | date-time, or an iso-format timestamp                               |                                                    |
| [Query, SetRef](https://docs.fauna.com/fauna/current/learn/understanding/types#set) | a string containing the wire protocol of this value                 | The wire protocol is not documented.               |

### Ref Types

Every ref is serialized as a json object with 2 or 3 fields, as listed above. The `type` field will be
one of these strings:
|                                    Reference Type                                       |    `type` string    |
| --------------------------------------------------------------------------------------- | ------------------- |
| Document                                                                                | `"document"`        |
| [Collection](https://docs.fauna.com/fauna/current/api/fql/functions/collection)         | `"collection"`      |
| [Database](https://docs.fauna.com/fauna/current/api/fql/functions/database)             | `"database"`        |
| [Index](https://docs.fauna.com/fauna/current/api/fql/functions/iindex)                  | `"index"`           |
| [Function](https://docs.fauna.com/fauna/current/api/fql/functions/function)             | `"function"`        |
| [Role](https://docs.fauna.com/fauna/current/api/fql/functions/role)                     | `"role"`            |
| [AccessProvider](https://docs.fauna.com/fauna/current/api/fql/functions/accessprovider) | `"access_provider"` |
| [Key](https://docs.fauna.com/fauna/current/api/fql/functions/keys)                      | `"key"`             |
| [Token](https://docs.fauna.com/fauna/current/api/fql/functions/tokens)                  | `"token"`           |
| [Credential](https://docs.fauna.com/fauna/current/api/fql/functions/credentials)        | `"credential"`      |

For all other refs (for example if you stored the result of `Collections()`), the `type` will be `"unknown"`.

If you wish to select the id of a ref, simply add `"id"` to the "Path" of the additional column. If
you wish to select the collection id, add `["collection", "id"]` to the additional column path. This
is because we pass the path to the [Select function](https://docs.fauna.com/fauna/current/api/fql/functions/select).

## Changelog

| Version | Date       | Pull Request                                             | Subject          |
| ------- | ---------- | -------------------------------------------------------- | ---------------- |
| 0.1.0   | 2022-08-03 | [15274](https://github.com/airbytehq/airbyte/pull/15274) | Add Fauna Source |
