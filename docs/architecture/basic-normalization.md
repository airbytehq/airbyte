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

The [normalization rules](basic-normalization.md#Rules) are _not_ configurable. They are designed to pick a reasonable set of defaults to hit the 80/20 rule of data normalization. We respect that normalization is a detail-oriented problem and that with a fixed set of rules, we cannot normalize your data in such a way that covers all use cases. If this feature does not meet your normalization needs, we always put the full json blob in destination as well, so that you can parse that object however best meets your use case. We will be adding more advanced normalization functionality shortly. Airbyte is focused on the EL of ELT. If you need a really featureful tool for the transformations then, we suggest trying out DBT.

Airbyte places the json blob version of your data in a table called `_airbyte_raw_<stream name>`. If basic normalization is turned on, it will place a separate copy of the data in a table called `<stream name>`. Under the hood, Airbyte is using DBT, which means that the data only ingresses into the data store one time. The normalization happens as a query within the datastore. This implementation avoids extra network time and costs.

## Destinations that Support Basic Normalization

* [BigQuery](../integrations/destinations/bigquery.md)
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

{% hint style="warning" %}
Normalization is still a work in progress and is very basic for the moment. We are actively working on improving it. Nested Objects and Arrays are not currently handled by Normalization \(only flat jsons are properly mapped out as a table\). You can follow progress as part of this [issue](https://github.com/airbytehq/airbyte/issues/886) and its related children.
{% endhint %}

