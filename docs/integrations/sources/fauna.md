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

## Changelog

| Version | Date       | Pull Request                                             | Subject          |
| ------- | ---------- | -------------------------------------------------------- | ---------------- |
| 0.1.0   | 2022-08-03 | [15274](https://github.com/airbytehq/airbyte/pull/15274) | Add Fauna Source |
