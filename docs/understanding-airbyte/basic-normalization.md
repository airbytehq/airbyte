# Basic Normalization

At its core, Airbyte is geared to handle the EL \(Extract Load\) steps of an ELT process. These steps can also be referred in Airbyte's dialect as "Source" and "Destination".

However, this is actually producing a table in the destination with a JSON blob column... For the typical analytics use case, you probably want this json blob normalized so that each field is its own column.

So, after EL, comes the T \(transformation\) and the first T step that Airbyte actually applies on top of the extracted data is called "Normalization".

Airbyte runs this step before handing the final data over to other tools that will manage further transformation down the line.

To summarize, we can represent the ELT process in the diagram below. These are steps that happens between your "Source Database or API" and the final "Replicated Tables" with examples of implementation underneath:

![](../.gitbook/assets/connecting-EL-with-T-4.png)

In Airbyte, the current normalization option is implemented using a dbt Transformer composed of:
- Airbyte base-normalization python package to generate dbt SQL models files
- dbt to compile and executes the models on top of the data in the destinations that supports it.

## Overview

Basic Normalization uses a fixed set of rules to map a json object from a source to the types and format that are native to the destination. For example if a source emits data that looks like this:

```javascript
{
  "make": "alfa romeo",
  "model": "4C coupe",
  "horsepower": "247"
}
```

Then basic normalization would create the following table:

```sql
CREATE TABLE "cars" (
    -- metadata added by airbyte
    "_airbyte_cars_hashid" VARCHAR, -- uuid assigned by airbyte derived from a hash of the data.
    "_airbyte_emitted_at" TIMESTAMP_WITH_TIMEZONE, -- time at which the record was emitted.
    "_airbyte_normalized_at" TIMESTAMP_WITH_TIMEZONE, -- time at which the record was normalized.

    -- data
    "make" VARCHAR,
    "model" VARCHAR,
    "horsepower" INTEGER
);
```

You'll notice that we add some metadata to keep track of important information about each record.

The [normalization rules](basic-normalization.md#Rules) are _not_ configurable. They are designed to pick a reasonable set of defaults to hit the 80/20 rule of data normalization. We respect that normalization is a detail-oriented problem and that with a fixed set of rules, we cannot normalize your data in such a way that covers all use cases. If this feature does not meet your normalization needs, we always put the full json blob in destination as well, so that you can parse that object however best meets your use case. We will be adding more advanced normalization functionality shortly. Airbyte is focused on the EL of ELT. If you need a really featureful tool for the transformations then, we suggest trying out dbt.

Airbyte places the json blob version of your data in a table called `_airbyte_raw_<stream name>`. If basic normalization is turned on, it will place a separate copy of the data in a table called `<stream name>`. Under the hood, Airbyte is using dbt, which means that the data only ingresses into the data store one time. The normalization happens as a query within the datastore. This implementation avoids extra network time and costs.

## Destinations that Support Basic Normalization

* [BigQuery](../integrations/destinations/bigquery.md)
* [MySQL](../integrations/destinations/mysql.md)
  * The server must support the `WITH` keyword.
  * Require MySQL >= 8.0, or MariaDB >= 10.2.1.
* [Postgres](../integrations/destinations/postgres.md)
* [Snowflake](../integrations/destinations/snowflake.md)
* [Redshift](../integrations/destinations/redshift.md)

Basic Normalization can be used in each of these destinations by configuring the "basic normalization" field to true when configuring the destination in the UI.

## Rules

### Typing

Airbyte tracks types using JsonSchema's primitive types. Here is how these types will map onto standard SQL types. Note: The names of the types may differ slightly across different destinations.

Airbyte uses the types described in the catalog to determine the correct type for each column. It does not try to use the values themselves to infer the type.

| JsonSchema Type | Resulting Type | Notes |
| :--- | :--- | :--- |
| `number` | float |  |
| `integer` | integer |  |
| `string` | string |  |
| `bit` | boolean |  |
| `boolean` | boolean |  |
| `array` | new table | see [nesting](basic-normalization.md#Nesting) |
| `object` | new table | see [nesting](basic-normalization.md#Nesting) |

### Nesting

Basic Normalization attempts to expand any nested arrays or objects it receives into separate tables in order to allow more ergonomic querying of your data.

#### Arrays

Basic Normalization expands arrays into separate tables. For example if the source provides the following data:

```javascript
{
  "make": "alfa romeo",
  "model": "4C coupe",
  "limited_editions": [
    { "name": "4C spider", "release_year": 2013 },
    { "name" : "4C spider italia" , "release_year":  2018 }
  ]
}
```

The resulting normalized schema would be:

```sql
CREATE TABLE "cars" (
    "_airbyte_cars_hashid" VARCHAR,
    "_airbyte_emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "_airbyte_normalized_at" TIMESTAMP_WITH_TIMEZONE,

    "make" VARCHAR,
    "model" VARCHAR
);

CREATE TABLE "limited_editions" (
    "_airbyte_limited_editions_hashid" VARCHAR,
    "_airbyte_cars_foreign_hashid" VARCHAR,
    "_airbyte_emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "_airbyte_normalized_at" TIMESTAMP_WITH_TIMEZONE,

    "name" VARCHAR,
    "release_year" VARCHAR
);
```

If the nested items in the array are not objects then they are expanded into a string field of comma separated values e.g.:

```javascript
{
  "make": "alfa romeo",
  "model": "4C coupe",
  "limited_editions": [ "4C spider", "4C spider italia"]
}
```

The resulting normalized schema would be:

```sql
CREATE TABLE "cars" (
    "_airbyte_cars_hashid" VARCHAR,
    "_airbyte_emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "_airbyte_normalized_at" TIMESTAMP_WITH_TIMEZONE,

    "make" VARCHAR,
    "model" VARCHAR
);

CREATE TABLE "limited_editions" (
    "_airbyte_limited_editions_hashid" VARCHAR,
    "_airbyte_cars_foreign_hashid" VARCHAR,
    "_airbyte_emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "_airbyte_normalized_at" TIMESTAMP_WITH_TIMEZONE,

    "data" VARCHAR
);
```

#### Objects

In the case of a nested object e.g.:

```javascript
{
  "make": "alfa romeo",
  "model": "4C coupe",
  "powertrain_specs": { "horsepower": 247, "transmission": "6-speed" }
}
```

The normalized schema would be:

```sql
CREATE TABLE "cars" (
    "_airbyte_cars_hashid" VARCHAR,
    "_airbyte_emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "_airbyte_normalized_at" TIMESTAMP_WITH_TIMEZONE,

    "make" VARCHAR,
    "model" VARCHAR
);

CREATE TABLE "powertrain_specs" (
    "_airbyte_powertrain_hashid" VARCHAR,
    "_airbyte_cars_foreign_hashid" VARCHAR,
    "_airbyte_emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "_airbyte_normalized_at" TIMESTAMP_WITH_TIMEZONE,

    "horsepower" INTEGER,
    "transmission" VARCHAR
);
```

### Naming Collisions for un-nested objects

When extracting nested objects or arrays, the Basic Normalization process needs to figure out new names for the expanded tables.

For example, if we had a `cars` table with a nested column `cars` containing an object whose schema is identical to the parent table.

```javascript
{
  "make": "alfa romeo",
  "model": "4C coupe",
  "cars": [
    { "make": "audi", "model": "A7" },
    { "make" : "lotus" , "model":  "elise" }
    { "make" : "chevrolet" , "model":  "mustang" }
  ]
}
```

The expanded table would have a conflict in terms of naming since both are named `cars`. To avoid name collisions and ensure a more consistent naming scheme, Basic Normalization chooses the expanded name as follows:

* `cars` for the original parent table
* `cars_da3_cars` for the expanded nested columns following this naming scheme in 3 parts: `<Json path>_<Hash>_<nested column name>`
* Json path: The entire json path string with '\_' characters used as delimiters to reach the table that contains the nested column name.
* Hash: Hash of the entire json path to reach the nested column reduced to 3 characters. This is to make sure we have a unique name \(in case part of the name gets truncated, see below\)
* Nested column name: name of the column being expanded into its own table.

By following this strategy, nested columns should "never" collide with other table names. If it does, an exception will probably be thrown either by the normalization process or by dbt that runs afterward.

```sql
CREATE TABLE "cars" (
    "_airbyte_cars_hashid" VARCHAR,
    "_airbyte_emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "_airbyte_normalized_at" TIMESTAMP_WITH_TIMEZONE,

    "make" VARCHAR,
    "model" VARCHAR
);

CREATE TABLE "cars_da3_cars" (
    "_airbyte_cars_hashid" VARCHAR,
    "_airbyte_cars_foreign_hashid" VARCHAR,
    "_airbyte_emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "_airbyte_normalized_at" TIMESTAMP_WITH_TIMEZONE,

    "make" VARCHAR,
    "model" VARCHAR
);
```

### Naming limitations & truncation

Note that different destinations have various naming limitations, most commonly on how long names can be. For instance, the Postgres documentation states:

> The system uses no more than NAMEDATALEN-1 bytes of an identifier; longer names can be written in commands, but they will be truncated. By default, NAMEDATALEN is 64 so the maximum identifier length is 63 bytes

Most modern data warehouses have name lengths limits on the longer side, so this should not affect us that often. Basic Normalization will fallback to the following rules:

1. No Truncate if under destination's character limits

However, in the rare cases where these limits are reached:

1. Truncate only the `Json path` to fit into destination's character limits
2. Truncate the `Json path` to at least the 10 first characters, then truncate the nested column name starting in the middle to preserve prefix/suffix substrings intact \(whenever a truncate in the middle is made, two '\_\_' characters are also inserted to denote where it happened\) to fit into destination's character limits 

As an example from the hubspot source, we could have the following tables with nested columns:

| Description | Example 1 | Example 2 |
| :--- | :--- | :--- |
| Original Stream Name | companies | deals |
| Json path to the nested column | `companies/property_engagements_last_meeting_booked_campaign` | `deals/properties/engagements_last_meeting_booked_medium` |
| Final table name of expanded nested column on BigQuery | companies\_2e8\_property\_engag**ements\_last\_meeting\_bo**oked\_campaign | deals\_prop**erties**\_6e6\_engagements\_l**ast\_meeting\_**booked\_medium |
| Final table name of expanded nested column on Postgres | companies\_2e8\_property\_engag**\_\_**oked\_campaign | deals\_prop\_6e6\_engagements\_l**\_\_**booked\_medium |

As mentioned in the overview:

- Airbyte places the json blob version of your data in a table called `_airbyte_raw_<stream name>`.
- If basic normalization is turned on, it will place a separate copy of the data in a table called `<stream name>`.
- In certain pathological cases, basic normalization is required to generate large models with many columns and multiple intermediate transformation steps for a stream. This may break down the "ephemeral" materialization strategy and require the use of additional intermediate views or tables instead. As a result, you may notice additional temporary tables being generated in the destination to handle these checkpoints.

## UI Configurations

To enable basic normalization (which is optional), you can toggle it on or disable it in the "Normalization and Transformation" section when setting up your connection:

![](../.gitbook/assets/basic-normalization-configuration.png)

## Extending Basic Normalization

Note that all the choices made by Normalization as described in this documentation page in terms of naming could be overridden by your own custom choices. To do so, you can follow the following tutorials:

* to build a [custom SQL view](../operator-guides/transformation-and-normalization/transformations-with-sql.md) with your own naming conventions
* to export, edit and run [custom dbt normalization](../operator-guides/transformation-and-normalization/transformations-with-dbt.md) yourself
* or further, you can configure the use of a custom dbt project within Airbyte by following [this guide](../operator-guides/transformation-and-normalization/transformations-with-airbyte.md).

## CHANGELOG

### airbyte-integration/bases/base-normalization

Note that Basic Normalization is packaged in a docker image `airbyte/normalization`.
This image is tied to and released along with a specific Airbyte version.
It is not configurable independently like it is possible to do with connectors (source & destinations)

Therefore, in order to "upgrade" to the desired normalization version, you need to use the corresponding Airbyte version that it's being released in:

| Airbyte Version | Normalization Version | Date | Pull Request | Subject |
| :--- | :---  | :--- | :--- | :--- |
| 0.29.8-alpha | 0.1.40 | 2021-08-18 | [#5433](https://github.com/airbytehq/airbyte/pull/5433) | Allow optional credentials_json for BigQuery  |
| 0.29.5-alpha | 0.1.39 | 2021-08-11 | [#4557](https://github.com/airbytehq/airbyte/pull/4557) | Handle date times and solve conflict name btw stream/field |
| 0.28.2-alpha | 0.1.38 | 2021-07-28 | [#5027](https://github.com/airbytehq/airbyte/pull/5027) | Handle quotes in column names when parsing JSON blob |
| 0.27.5-alpha | 0.1.37 | 2021-07-22 | [#3947](https://github.com/airbytehq/airbyte/pull/4881/) | Handle `NULL` cursor field values when deduping |
| 0.27.2-alpha | 0.1.36 | 2021-07-09 | [#3947](https://github.com/airbytehq/airbyte/pull/4163/) | Enable normalization for MySQL destination |
