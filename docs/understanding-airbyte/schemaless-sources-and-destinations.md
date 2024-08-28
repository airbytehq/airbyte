# "Schemaless" Sources and Destinations

In order to run a sync, Airbyte requires a [catalog](/understanding-airbyte/airbyte-protocol#catalog), which includes a data schema describing the shape of data being emitted by the source.
This schema will be used to prepare the destination to populate the data during the sync.

While having a [strongly-typed](/understanding-airbyte/supported-data-types) catalog/schema is possible for most sources, some won't have a reasonably static schema. This document describes the options available for the subset of sources that do not have a strict schema, aka "schemaless sources".

## What is a Schemaless Source?

Schemaless sources are sources for which there is no requirement or expectation that records will conform to a particular pattern.
For example, in a MongoDB database, there's no requirement that the fields in one document are the same as the fields in the next, or that the type of value in one field is the same as the type for that field in a separate document.
Similarly, for a file-based source such as S3, the files that are present in your source may not all have the same schema.

Although the sources themselves may not conform to an obvious schema, Airbyte still needs to know the shape of the data in order to prepare the destination for the records.
For these sources, during the [`discover`](/understanding-airbyte/airbyte-protocol#discover) method, Airbyte offers two options to create the schema:

1. Dynamic schema inference.
2. A hardcoded "schemaless" schema.

### Dynamic schema inference

If this option is selected, Airbyte will infer the schema dynamically based on the contents of the source.
If your source's content is homogenous, we recommend this option, as the data in your destination will be typed and you can make use of schema evolution features, column selection, and similar Airbyte features which operate against the source's schema.

For MongoDB, you can configure the number of documents that will be used for schema inference (from 1,000 to 10,000 documents; by default, this is set to 10,000).
Airbyte will read in the requested number of documents (sampled randomly) and infer the schema from them.
For file-based sources, we look at up to 10 files (reading up to 1MB per file) and infer the schema based on the contents of those files.

In both cases, as the contents of the source change, the schema can change too.

The schema that's produced from the inference procedure will include all the top-level fields that were observed in the sampled records.
The type assigned to each field will be the widest type observed for that field in any of the sampled data.
So if we observe that a field has an integer type in one record and a string in another, the schema will identify the field as a string.

There are a few drawbacks to be aware of:

- If your dataset is very large, the `discover` process can be very time-consuming.
- Because we may not use 100% of the available data to create the schema, your schema may not contain every field present in your records.
  Airbyte only syncs fields that are in the schema, so you may end up with incomplete data in the destination.

If your data set is very large or you anticipate that it will change often, we recommend using the "schemaless" schema to avoid these issues.

_Note: For MongoDB, knowing how variable your dataset is can help you choose an appropriate value for the number of documents to use for schema inference.
If your data is uniform across all or most records, you can set this to a lower value, providing better performance on discover and during the sync.
If your data varies but you cannot use the Schemaless option, you can set it to a larger value to ensure that as many fields as possible are accounted for._

### Schemaless schema

If this option is selected, the schema will always be `{"data": object}`, regardless of the contents of the data.
During the sync, we "wrap" each record behind a key named `data`.
This means that the destination receives the data with one top-level field only, and the value of the field is the entire record.
This option avoids a time-consuming or inaccurate `discover` phase and guarantees that everything ends up in your destination, at the expense of Airbyte being able to structure the data into different columns.

## Future Enhancements

### File-based Sources: configurable amount of data read for schema inference

Currently, Airbyte chooses the amount of data that we'll use to infer the schema for file-based sources.
We will be surfacing a config option for users to choose how much data to read to infer the schema.

This option is already available for the MongoDB source.

### Unwrapping the data at schemaless Destinations

MongoDB and file storage systems also don't require a schema at the destination.
For this reason, if you are syncing data from a schemaless source to a schemaless destination and chose the "schemaless" schema option, Airbyte will offer the ability to "unwrap" the data at the destination so that it is not nested under the "data" key.

### Column exclusion for schemaless schemas

We are planning to offer a way to exclude fields from being synced when the schemaless option is selected, as column selection is not applicable.
