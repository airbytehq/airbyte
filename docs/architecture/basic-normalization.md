# Basic Normalization

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
    "_cars_hashid" VARCHAR, -- uuid assigned by airbyte derived from a hash of the data.
    "emitted_at" TIMESTAMP_WITH_TIMEZONE, -- time at which the record was emitted.
    "normalized_at" TIMESTAMP_WITH_TIMEZONE, -- time at which the record was normalized.

    -- data
    "make" VARCHAR,
    "model" VARCHAR,
    "horsepower" INTEGER
);
```

You'll notice that we add some metadata to keep track of important information about each record.

The [normalization rules](basic-normalization.md#Rules) are _not_ configurable. They are designed to pick a reasonable set of defaults to hit the 80/20 rule of data normalization. We respect that normalization is a detail-oriented problem and that with a fixed set of rules, we cannot normalize your data in such a way that covers all use cases. If this feature does not meet your normalization needs, we always put the full json blob in destination as well, so that you can parse that object however best meets your use case. We will be adding more advanced normalization functionality shortly. Airbyte is focused on the EL of ELT. If you need a really featureful tool for the transformations then, we suggest trying out DBT.

Airbyte places the json blob version of your data in a table called `<stream name>_raw`. If basic normalization is turned on, it will place a separate copy of the data in a table called `<stream name>`. Under the hood, Airbyte is using DBT, which means that the data only ingresses into the data store one time. The normalization happens as a query within the datastore. This implementation avoids extra network time and costs.

## Destinations that Support Basic Normalization

* [BigQuery](../integrations/destinations/bigquery.md)
* [Postgres](../integrations/destinations/postgres.md)
* [Snowflake](../integrations/destinations/snowflake.md)
* \(_coming soon_\) Redshift

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
    "_cars_hashid" VARCHAR,
    "emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "normalized_at" TIMESTAMP_WITH_TIMEZONE,

    "make" VARCHAR,
    "model" VARCHAR,
);

CREATE TABLE "limited_editions" (
    "_limited_editions_hashid" VARCHAR,
    "_cars_foreign_hashid" VARCHAR,
    "emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "normalized_at" TIMESTAMP_WITH_TIMEZONE,

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
    "_cars_hashid" VARCHAR,
    "emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "normalized_at" TIMESTAMP_WITH_TIMEZONE,

    "make" VARCHAR,
    "model" VARCHAR,
);

CREATE TABLE "limited_editions" (
    "_limited_editions_hashid" VARCHAR,
    "_cars_foreign_hashid" VARCHAR,
    "emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "normalized_at" TIMESTAMP_WITH_TIMEZONE,

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
    "_cars_hashid" VARCHAR,
    "emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "normalized_at" TIMESTAMP_WITH_TIMEZONE,

    "make" VARCHAR,
    "model" VARCHAR,
);

CREATE TABLE "powertrain_specs" (
    "_powertrain_hashid" VARCHAR,
    "_cars_foreign_hashid" VARCHAR,
    "emitted_at" TIMESTAMP_WITH_TIMEZONE,
    "normalized_at" TIMESTAMP_WITH_TIMEZONE,

    "horsepower" INTEGER,
    "transmission" VARCHAR
);
```

