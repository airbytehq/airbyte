# Fauna

This page guides you through setting up a [Fauna](https://fauna.com/) source.

# Overview

The Fauna source supports the following sync modes:

- **Full Sync** - exports all the data from a Fauna collection.
- **Incremental Sync** - exports data incrementally from a Fauna collection.

You need to create a separate source per collection that you want to export.

## Preliminary setup

Enter the domain of the collection's database that you are exporting. The URL can be found in
[the docs](https://docs.fauna.com/fauna/current/learn/understanding/region_groups#how-to-use-region-groups).

## Full sync

Follow these steps if you want this connection to perform a full sync.

1. Create a role that can read the collection that you are exporting. You can create the role in the [Dashboard](https://dashboard.fauna.com/) or the [fauna shell](https://github.com/fauna/fauna-shell) with the following query:
```javascript
CreateRole({
  name: "airbyte-readonly",
  privileges: [
    {
      resource: Collections(),
      actions: { read: true }
    },
    {
      resource: Indexes(),
      actions: { read: true }
    },
    {
      resource: Collection("COLLECTION_NAME"),
      actions: { read: true }
    }
  ],
})
```

Replace `COLLECTION_NAME` with the name of the collection configured for this connector. If you'd like to sync
multiple collections, add an entry for each additional collection you'd like to sync. For example, to sync
`users` and `products`, run this query instead:
```javascript
CreateRole({
  name: "airbyte-readonly",
  privileges: [
    {
      resource: Collections(),
      actions: { read: true }
    },
    {
      resource: Indexes(),
      actions: { read: true }
    },
    {
      resource: Collection("users"),
      actions: { read: true }
    },
    {
      resource: Collection("products"),
      actions: { read: true }
    }
  ],
})
```

2. Create a key with that role. You can create a key using this query:
```javascript
CreateKey({
  name: "airbyte-readonly",
  role: Role("airbyte-readonly"),
})
```
3. Copy the `secret` output by the `CreateKey` command and enter that as the "Fauna Secret" on the left.
   **Important**: The secret is only ever displayed once. If you lose it, you would have to create a new key.

## Incremental sync

Follow these steps if you want this connection to perform incremental syncs.

1. Create the "Incremental Sync Index". This allows the connector to perform incremental syncs. You can create the index with the [fauna shell](https://github.com/fauna/fauna-shell) or in the [Dashboard](https://dashboard.fauna.com/) with the following query:
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

Replace `COLLECTION_NAME` with the name of the collection configured for this connector.
Replace `INDEX_NAME` with the name that you configured for the Incremental Sync Index.

Repeat this step for every collection you'd like to sync.

2. Create a role that can read the collection, the index, and the metadata of all indexes. It needs access to index metadata in order to validate the index settings. You can create the role with this query:
```javascript
CreateRole({
  name: "airbyte-readonly",
  privileges: [
    {
      resource: Collections(),
      actions: { read: true }
    },
    {
      resource: Indexes(),
      actions: { read: true }
    },
    {
      resource: Collection("COLLECTION_NAME"),
      actions: { read: true }
    },
    {
      resource: Index("INDEX_NAME"),
      actions: { read: true }
    }
  ],
})
```

Replace `COLLECTION_NAME` with the name of the collection configured for this connector.
Replace `INDEX_NAME` with the name that you configured for the Incremental Sync Index.

If you'd like to sync multiple collections, add an entry for every collection and index
you'd like to sync. For example, to sync `users` and `products` with Incremental Sync, run
the following query:
```javascript
CreateRole({
  name: "airbyte-readonly",
  privileges: [
    {
      resource: Collections(),
      actions: { read: true }
    },
    {
      resource: Indexes(),
      actions: { read: true }
    },
    {
      resource: Collection("users"),
      actions: { read: true }
    },
    {
      resource: Index("users-ts"),
      actions: { read: true }
    },
    {
      resource: Collection("products"),
      actions: { read: true }
    },
    {
      resource: Index("products-ts"),
      actions: { read: true }
    }
  ],
})
```


3. Create a key with that role. You can create a key using this query:
```javascript
CreateKey({
  name: "airbyte-readonly",
  role: Role("airbyte-readonly"),
})
```
4. Copy the `secret` output by the `CreateKey` command and enter that as the "Fauna Secret" on the left.
   **Important**: The secret is only ever displayed once. If you lose it, you would have to create a new key.

## Export formats

This section captures export formats for all special case data stored in Fauna. This list is exhaustive.

Note that the `ref` column in the exported database contains only the document ID from each document's
reference (or "ref"). Since only one collection is involved in each connector configuration, it is
inferred that the document ID refers to a document within the synced collection.

|                                  Fauna Type                                         |                             Format                                  |                   Note                      |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------- |
| [Document Ref](https://docs.fauna.com/fauna/current/learn/understanding/types#ref)  | `{ id: "id", "collection": "collection-name", "type": "document" }` |                                             |
| [Other Ref](https://docs.fauna.com/fauna/current/learn/understanding/types#ref)     | `{ id: "id", "type": "ref-type" }`                                  | This includes all other refs, listed below. |
| [Byte Array](https://docs.fauna.com/fauna/current/learn/understanding/types#byte)   | base64 url formatting                                               |                                             |
| [Timestamp](https://docs.fauna.com/fauna/current/learn/understanding/types#date)    | date-time, or an iso-format timestamp                               |                                             |
| [Query, SetRef](https://docs.fauna.com/fauna/current/learn/understanding/types#set) | a string containing the wire protocol of this value                 | The wire protocol is not documented.        |

### Ref types

Every ref is serialized as a JSON object with 2 or 3 fields, as listed above. The `type` field must be
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

For all other refs (for example if you stored the result of `Collections()`), the `type` must be `"unknown"`.
There is a difference between a specific collection ref (retrieved with `Collection("name")`), and all the reference
to all collections (retrieved with `Collections()`). This is why the `type` is `"unknown"` for `Collections()`,
but not for `Collection("name")`

To select the document ID from a ref, add `"id"` to the "Path" of the additional column. For example, if "Path"
is `["data", "parent"]`, change the "Path" to `["data", "parent", "id"]`.

To select the collection name, add `"collection", "id"` to the "Path" of the additional column. For example, if
"Path" is `["data", "parent"]`, change the "Path" to `["data", "parent", "collection", "id"]`. Internally, the
FQL [`Select`](https://docs.fauna.com/fauna/current/api/fql/functions/select) is used.

## Changelog

| Version | Date       | Pull Request                                             | Subject          |
| ------- | ---------- | -------------------------------------------------------- | ---------------- |
| 0.1.0   | 2022-11-17 | [15274](https://github.com/airbytehq/airbyte/pull/15274) | Add Fauna Source |
