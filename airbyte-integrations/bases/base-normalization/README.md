# Normalization

Related documentation on normalization is available here:

- [architecture / Basic Normalization](../../../docs/architecture/basic-normalization.md)
* [tutorials / custom DBT normalization](../../../docs/tutorials/connecting-el-with-t-using-dbt.md)

# Testing normalization

Below are short descriptions of the kind of tests that may be affected by changes to the normalization code.

## Unit Tests

Unit tests are automatically included when building the normalization project.
But you could invoke them explicitly by running the following commands for example:

with Gradle:

    ./gradlew :airbyte-integrations:bases:base-normalization:unitTest

or directly with pytest:

    pytest airbyte-integrations/bases/base-normalization/unit_tests

Unit tests are targeted at the main code generation functionality of normalization.
They should verify different logic rules on how to convert an input catalog.json (JSON Schema) file into
dbt files.

#### test_transform_config.py:

This class is testing the transform config functionality that converts a destination_config.json into the adequate profiles.yml file for dbt to use
see [related dbt docs on profiles.yml](https://docs.getdbt.com/reference/profiles.yml) for more context on what it actually is.

#### test_stream_processor.py:

These Unit tests functions check how each stream is converted to dbt models files.
For example, one big focus area is around how table names are chosen.
(especially since some destination like postgres have a very low limit to identifiers length of 64 characters)
In case of nested objects/arrays in a stream, names can be dragged on to even longer names...

So you can find rules of how to truncate and concatenate part of the table names together in here.
Depending on the catalog context and what identifiers have been already used in the past, some naming
may also be affected and requires to choose new identifications to avoid collisions.

Additional helper functions dealing with cursor fields, primary keys and other code generation parts are also being tested here.

#### test_destination_name_transformer.py:

These Unit tests checks implementation of specific rules of SQL identifier naming conventions for each destination.
The specifications rules of each destinations are detailed in the corresponding docs, especially on the
allowed characters, if quotes are needed or not, and the length limitations:

- [bigquery](../../../docs/integrations/destinations/bigquery.md)
- [postgres](../../../docs/integrations/destinations/postgres.md)
- [redshift](../../../docs/integrations/destinations/redshift.md)
- [snowflake](../../../docs/integrations/destinations/snowflake.md)

Rules about truncations, for example for both of these strings which are too long for the postgres 64 limit:
- `Aaaa_Bbbb_Cccc_Dddd_Eeee_Ffff_Gggg_Hhhh_Iiii`
- `Aaaa_Bbbb_Cccc_Dddd_a_very_long_name_Ffff_Gggg_Hhhh_Iiii`

Deciding on how to truncate (in the middle) are being verified in these tests.
In this instance, both strings ends up as:`Aaaa_Bbbb_Cccc_Dddd___e_Ffff_Gggg_Hhhh_Iiii`
and can potentially cause a collision in table names. Note that dealing with such collisions is not part of `destination_name_transformer` but of the `stream_processor`.

## Integration Tests

With Gradle:

    ./gradlew :airbyte-integrations:bases:base-normalization:integrationTest

or directly with pytest:

    pytest airbyte-integrations/bases/base-normalization/integration_tests

or can also be invoked on github, thanks to the slash commands posted as comments:

    /test connector=bases/base-normalization

These tests are run against all destinations that dbt can be executed on.

Some test suites can be selected to be versioned control in Airbyte git repository (or not).
This is useful to see direct impacts of code changes on downstream files generated or compiled
by normalization and dbt (directly in PR too).

We would typically choose small and meaningful test suites to include in git while others more complex tests
can be left out. They would still be run in a temporary directory and thrown away at the end of the tests.

They are defined, each one of them, in a separate directory in the resource folder.
For example, below, we would have 2 different tests "suites" with this hierarchy:

      base-normalization/integration_tests/resources/
      ├── test_suite1/
      │   ├── data_tests/
      │   │   ├── file1.sql
      │   │   └── file2.sql
      │   ├── schema_tests/
      │   │   ├── file1.yml
      │   │   └── file2.yml
      │   ├── catalog.json
      │   └── messages.txt
      └── test_suite2/
          ├── data_tests/
          ├── schema_tests/
          ├── catalog.json
          └── messages.txt

### Integration Test Input:

#### catalog.json:

The catalog.json is the main input for normalization from which the dbt models files are being
generated from as it describes in JSON Schema format what the data structure is.

#### messages.txt:

The `messages.txt` are serialized Airbyte JSON records that should be sent to the destination as if they were
transmitted by a source. In this integration test, the files is read and "cat" through to the docker image of 
each destination connectors to populate `_airbyte_raw_tables`. These tables are finally used as input
data for dbt to run from.

### Integration Test Execution Flow:

1. Preparing test execution workspace folder from dbt project template
2. Generate dbt profiles.yml to connect to destination
3. Populate raw tables by running destination connectors 
4. Normalization generating dbt models files
5. dbt run
6. dbt tests
7. optional checks

### Integration Test Checks:

#### schema tests:

https://docs.getdbt.com/docs/building-a-dbt-project/tests#schema-tests
https://docs.getdbt.com/docs/guides/writing-custom-schema-tests

#### data tests:

https://docs.getdbt.com/docs/building-a-dbt-project/tests#data-tests

### Integration Test Outputs:



## Standard Destination Tests

Generally, to invoke standard destination tests, you run with gradle using:

    ./gradlew :airbyte-integrations:connectors:destination-<connector name>:integrationTest

For more details and options, you can also refer to the [testing connectors docs](../../../docs/contributing-to-airbyte/building-new-connector/testing-connectors.md).

## Acceptance Tests

Please refer to the [developing docs](../../../docs/contributing-to-airbyte/developing-locally.md) on how to run Acceptance Tests.

