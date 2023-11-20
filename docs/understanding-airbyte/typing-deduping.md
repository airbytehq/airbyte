# Typing and Deduping

This page refers to new functionality added by [Destinations V2](/release_notes/upgrading_to_destinations_v2/). Typing and deduping is the default method of transforming datasets within data warehouse and database destinations after they've been replicated. Please check each destination to learn if Typing and deduping is supported.

## What is Destinations V2?

[Airbyte Destinations V2](/release_notes/upgrading_to_destinations_v2) provide:

- One-to-one table mapping: Data in one stream will always be mapped to one table in your data warehouse. No more sub-tables.
- Improved per-row error handling with `_airbyte_meta`: Airbyte will now populate typing errors in the `_airbyte_meta` column instead of failing your sync. You can query these results to audit misformatted or unexpected data.
- Internal Airbyte tables in the `airbyte_internal` schema: Airbyte will now generate all raw tables in the `airbyte_internal` schema. We no longer clutter your desired schema with raw data tables.
- Incremental delivery for large syncs: Data will be incrementally delivered to your final tables when possible. No more waiting hours to see the first rows in your destination table.

## `_airbyte_meta` Errors

"Per-row error handling" is a new paradigm for Airbyte which provides greater flexibility for our users. Airbyte now separates `data-moving problems` from `data-content problems`. Prior to Destinations V2, both types of errors were handled the same way: by failing the sync. Now, a failing sync means that Airbyte could not _move_ all of your data. You can query the `_airbyte_meta` column to see which rows failed for _content_ reasons, and why. This is a more flexible approach, as you can now decide how to handle rows with errors on a case-by-case basis.

:::tip
When using data downstream from Airbyte, we generally recommend you only include rows which do not have an error, e.g:

```sql
-- postgres syntax
SELECT COUNT(*) FROM _table_ WHERE json_array_length(_airbyte_meta ->> errors) = 0
```

:::

The types of errors which will be stored in `_airbyte_meta.errors` include:

- **Typing errors**: the source declared that the type of the column `id` should be an integer, but a string value was returned.
- **Size errors**: the source returned content which cannot be stored within this this row or column (e.g. [a Redshift Super column has a 16mb limit](https://docs.aws.amazon.com/redshift/latest/dg/limitations-super.html)).

Depending on your use-case, it may still be valuable to consider rows with errors, especially for aggregations. For example, you may have a table `user_reviews`, and you would like to know the count of new reviews received today. You can choose to include reviews regardless of whether your data warehouse had difficulty storing the full contents of the `message` column. For this use case, `SELECT COUNT(*) from user_reviews WHERE DATE(created_at) = DATE(NOW())` is still valid.

## Destinations V2 Example

Consider the following [source schema](https://docs.airbyte.com/integrations/sources/faker) for stream `users`:

```json
{
  "id": "number",
  "first_name": "string",
  "age": "number",
  "address": {
    "city": "string",
    "zip": "string"
  }
}
```

The data from one stream will now be mapped to one table in your schema as below:

#### Destination Table Name: _public.users_

| _(note, not in actual table)_                | \_airbyte_raw_id | \_airbyte_extracted_at | \_airbyte_meta                                               | id  | first_name | age  | address                                 |
| -------------------------------------------- | ---------------- | ---------------------- | ------------------------------------------------------------ | --- | ---------- | ---- | --------------------------------------- |
| Successful typing and de-duping ⟶            | xxx-xxx-xxx      | 2022-01-01 12:00:00    | {}                                                           | 1   | sarah      | 39   | { city: “San Francisco”, zip: “94131” } |
| Failed typing that didn’t break other rows ⟶ | yyy-yyy-yyy      | 2022-01-01 12:00:00    | { errors: {[“fish” is not a valid integer for column “age”]} | 2   | evan       | NULL | { city: “Menlo Park”, zip: “94002” }    |
| Not-yet-typed ⟶                              |                  |                        |                                                              |     |            |      |                                         |

In legacy normalization, columns of [Airbyte type](https://docs.airbyte.com/understanding-airbyte/supported-data-types/#the-types) `Object` in the Destination were "unnested" into separate tables. In this example, with Destinations V2, the previously unnested `public.users_address` table with columns `city` and `zip` will no longer be generated.

#### Destination Table Name: _airbyte.raw_public_users_ (`airbyte.{namespace}_{stream}`)

| _(note, not in actual table)_                | \_airbyte_raw_id | \_airbyte_data﻿                                                                           | \_airbyte_loaded_at  | \_airbyte_extracted_at |
| -------------------------------------------- | ---------------- | ----------------------------------------------------------------------------------------- | -------------------- | ---------------------- |
| Successful typing and de-duping ⟶            | xxx-xxx-xxx      | { id: 1, first_name: “sarah”, age: 39, address: { city: “San Francisco”, zip: “94131” } } | 2022-01-01 12:00:001 | 2022-01-01 12:00:00﻿   |
| Failed typing that didn’t break other rows ⟶ | yyy-yyy-yyy      | { id: 2, first_name: “evan”, age: “fish”, address: { city: “Menlo Park”, zip: “94002” } } | 2022-01-01 12:00:001 | 2022-01-01 12:00:00﻿   |
| Not-yet-typed ⟶                              | zzz-zzz-zzz      | { id: 3, first_name: “edward”, age: 35, address: { city: “Sunnyvale”, zip: “94003” } }    | NULL                 | 2022-01-01 13:00:00﻿   |

You also now see the following changes in Airbyte-provided columns:

![Airbyte Destinations V2 Column Changes](../release_notes/assets/updated_table_columns.png)
