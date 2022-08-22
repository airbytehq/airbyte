# Normalization

* [Normalization](#normalization)
    * [Under the hood](#under-the-hood)
        * [Incremental updates with dedup-history sync mode](#incremental-updates-with-dedup-history-sync-mode)
    * [Developer workflow](#developer-workflow)
        * [Setting up your environment](#setting-up-your-environment)
        * [Running dbt](#running-dbt)
    * [Testing normalization](#testing-normalization)
        * [Build & Activate Virtual Environment and install dependencies](#build--activate-virtual-environment-and-install-dependencies)
        * [Unit Tests](#unit-tests)
            * [test_transform_config.py:](#test_transform_configpy)
            * [test_stream_processor.py and test_table_name_registry.py:](#test_stream_processorpy-and-test_table_name_registrypy)
            * [test_destination_name_transformer.py:](#test_destination_name_transformerpy)
        * [Integration Tests](#integration-tests)
            * [Integration Tests Definitions for test_ephemeral.py:](#integration-tests-definitions-for-test_ephemeralpy)
            * [Integration Tests Definitions for test_normalization.py:](#integration-tests-definitions-for-test_normalizationpy)
                * [README.md:](#readmemd)
            * [Integration Test Data Input:](#integration-test-data-input)
                * [data_input/catalog.json:](#data_inputcatalogjson)
                * [data_input/messages.txt:](#data_inputmessagestxt)
                * [data_input/replace_identifiers.json:](#data_inputreplace_identifiersjson)
            * [Integration Test Execution Flow:](#integration-test-execution-flow)
            * [Integration Test Checks:](#integration-test-checks)
                * [dbt schema tests:](#dbt-schema-tests)
                * [dbt data tests:](#dbt-data-tests)
                * [Notes using dbt seeds:](#notes-using-dbt-seeds)
            * [Debug dbt operations with local database](#debug-dbt-operations-with-local-database)
        * [Standard Destination Tests](#standard-destination-tests)
        * [Acceptance Tests](#acceptance-tests)

Related documentation on normalization is available here:

* [architecture / Basic Normalization](../../../docs/understanding-airbyte/basic-normalization.md)
* [tutorials / Custom dbt normalization](../../../docs/operator-guides/transformation-and-normalization/transformations-with-dbt.md)

## Under the hood

Normalization has two Python modules:
* `transform_config` parses the destination connector config and generates a profile.yml file,
  which configures how dbt will connect to the destination database.
* `transform_catalog` parses the connection's catalog and generates a dbt_project.yml file,
  which configures the models that dbt will run and how they should be materialized.

`entrypoint.sh` (the entrypoint to normalization's Docker image) invokes these two modules, then calls `dbt run` on their output.

### Incremental updates with dedup-history sync mode

When generating the final table, we need to pull data from the SCD model.
A naive implementation would require reading the entire SCD table and completely regenerating the final table on each run.
This is obviously inefficient, so we instead use dbt's [incremental materialization mode](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/configuring-incremental-models).
At each stage of the dbt pipeline, normalization will query the target table for the newest `_airbyte_emitted_at` value.
Then we only need to find records from the source table with `_airbyte_emitted_at` greater than or equal to that value
(equal to is necessary in case a previous normalization run was interrupted).

This handles the two error scenarios quite cleanly:
* If a sync fails but succeeds after a retry, such that the first attempt commits some records and the retry commits a superset
  of those records, then normalization will see that the SCD table has none of those records. The SCD model has a deduping stage,
  which removes the records which were synced multiple times.
* If normalization fails partway through, such that (for example) the SCD model is updated but the final table is not, and then the sync
  is retried, then the source will not re-emit any old records (because the destination will have emitted a state message ack-ing
  all of the records). If the retry emits some new records, then normalization will append them to the SCD table as usual
  (because, from the SCD's point of view, this is just a normal sync). Then the final table's latest `__airbyte_emitted_at`
  will be older than the original attempt, so it will pull both the new records _and_ the first attempt's records from the SCD table.

## Developer workflow

At a high level, this is the recommended workflow for updating base-normalization:
1. Manually edit the models in `integration_tests/normalization_test_output/postgres/test_simple_streams/models/generated`.
   Run `dbt compile` and manually execute the SQL queries. This requires manual setup and validation, but allows you to quickly experiment
   with different inputs.
    1. You can substitute your preferred database/warehouse. This document will use Postgres because it's easy to set up.
1. Run `dbt run` and verify that it generates the data correctly.
1. Once `dbt run` succeeds, edit `stream_processor.py` until it generates the models you hand-wrote in step 1.
1. Run the `test_normalization[DestinationType.POSTGRES-test_simple_streams]` integration test case.
1. Run the full [integration test suite](#integration-tests).
1. Commit the changes in `integration_tests/normalization_test_output`.

### Setting up your environment

If you have a fully-featured Python dev environment, you can just set a breakpoint at [this line]([integration_tests/test_normalization.py#L105](https://github.com/airbytehq/airbyte/blob/17ee3ad44ff71164765b97ff439c7ffd51bf9bfe/airbyte-integrations/bases/base-normalization/integration_tests/test_normalization.py#L108))
and run the `test_normalization[DestinationType.POSTGRES-test_simple_streams]` test case. You can terminate the run after it hits the
breakpoint. This will start Postgres in a Docker container with some prepopulated data and configure profiles.yml to match the container.

Otherwise, you can run this command:
```shell
docker run \
  --rm \
  --name "normalization_dev_postgres" \
  -e "integration-tests" \
  -e "integration-tests" \
  -p "9001:5432" \
  -d \
  marcosmarxm/postgres-ssl:dev \
  -c ssl=on \
  -c ssl_cert_file=/var/lib/postgresql/server.crt \
  -c ssl_key_file=/var/lib/postgresql/server.key \
```

Then you'll need to edit `integration_tests/normalization_test_output/postgres/test_simple_streams/profiles.yml` and set the port to 9001.

If you manually start an external Postgres instance (or whatever destination you're working on), you can set the [`NORMALIZATION_TEST_POSTGRES_DB_PORT`](https://github.com/airbytehq/airbyte/blob/8ed3fb5379bf5a93d011a78a3be435cf9de8ab74/airbyte-integrations/bases/base-normalization/integration_tests/dbt_integration_test.py#L26)
variable to run tests against that instance.

### Running dbt

Once you have a database available, you can run dbt commands. We recommend running dbt from inside the `airbyte/normalization:dev` image.
This saves you the effort of installing dbt and reconfiguring dbt_project.yml. You should build the image locally with `./gradlew :airbyte-integrations:bases:base-normalization:airbyteDocker`.

First, `cd integration_tests/normalization_test_output/postgres/test_simple_streams`. Then install dbt's dependencies:
```shell
docker run \
  --rm \
  --init \
  -v $(pwd):/workspace \
  -v $(pwd)/build:/build \
  -v $(pwd)/logs:/logs \
  -v $(pwd)/build/dbt_packages/:/dbt \
  --entrypoint /usr/local/bin/dbt \
  --network host \
  -i airbyte/normalization:dev \
  deps \
  --profiles-dir=/workspace \
  --project-dir=/workspace
```

You should be able to run `dbt compile` now:
```shell
docker run \
  --rm \
  --init \
  -v $(pwd):/workspace \
  -v $(pwd)/build:/build \
  -v $(pwd)/logs:/logs \
  -v $(pwd)/build/dbt_packages/:/dbt \
  --entrypoint /usr/local/bin/dbt \
  --network host \
  -i airbyte/normalization:dev \
  compile \
  --profiles-dir=/workspace \
  --project-dir=/workspace
```

This will modify the files in `build/compiled/airbyte_utils/models/generated`.
For example, if you edit `models/generated/airbyte_incremental/scd/test_normalization/dedup_cdc_excluded_scd.sql`, then after compiling,
you can see the results in `build/compiled/airbyte_utils/models/generated/airbyte_incremental/scd/test_normalization/dedup_cdc_excluded_scd.sql`.

You can also use `dbt run` to have dbt actually execute your models:
```shell
docker run \
  --rm \
  --init \
  -v $(pwd):/workspace \
  -v $(pwd)/build:/build \
  -v $(pwd)/logs:/logs \
  -v $(pwd)/build/dbt_packages/:/dbt \
  --entrypoint /usr/local/bin/dbt \
  --network host \
  -i airbyte/normalization:dev \
  run \
  --profiles-dir=/workspace \
  --project-dir=/workspace
```
Like `dbt compile`, this will modify the files in `build/compiled/airbyte_utils/models/generated`. It will also modify the files in
`build/run/airbyte_utils/models/generated`.

## Testing normalization

Below are short descriptions of the kind of tests that may be affected by changes to the normalization code.

### Build & Activate Virtual Environment and install dependencies
From this connector directory, create a virtual environment:
```
python3 -m venv .venv
```

This will generate a virtualenv for this module in `.venv/`. Make sure this venv is active in your
development environment of choice. To activate it from the terminal, run:
```
source .venv/bin/activate
pip install -r requirements.txt
```
If you are in an IDE, follow your IDE's instructions to activate the virtualenv.

Note that while we are installing dependencies from `requirements.txt`, you should only edit `setup.py` for your dependencies. `requirements.txt` is
used for editable installs (`pip install -e`) to pull in Python dependencies from the monorepo and will call `setup.py`.
If this is mumbo jumbo to you, don't worry about it, just put your deps in `setup.py` but install using `pip install -r requirements.txt` and everything
should work as you expect.

### Unit Tests

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

#### test_stream_processor.py and test_table_name_registry.py:

These unit tests functions check how each stream is converted to dbt models files.
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

* [bigquery](../../../docs/integrations/destinations/bigquery.md)
* [postgres](../../../docs/integrations/destinations/postgres.md)
* [redshift](../../../docs/integrations/destinations/redshift.md)
* [snowflake](../../../docs/integrations/destinations/snowflake.md)
* [mysql](../../../docs/integrations/destinations/mysql.md)
* [oracle](../../../docs/integrations/destinations/oracle.md)
* [mssql](../../../docs/integrations/destinations/mssql.md)

Rules about truncations, for example for both of these strings which are too long for the postgres 64 limit:
* `Aaaa_Bbbb_Cccc_Dddd_Eeee_Ffff_Gggg_Hhhh_Iiii`
* `Aaaa_Bbbb_Cccc_Dddd_a_very_long_name_Ffff_Gggg_Hhhh_Iiii`

Deciding on how to truncate (in the middle) are being verified in these tests.
In this instance, both strings ends up as:

* `Aaaa_Bbbb_Cccc_Dddd___e_Ffff_Gggg_Hhhh_Iiii`

The truncate operation gets rid of characters in the middle of the string to preserve the start
and end characters as it may contain more useful information in table naming. However the final
truncated name can still potentially cause collisions in table names...

Note that dealing with such collisions is not part of `destination_name_transformer` but of the
`stream_processor` since one is focused on destination conventions and the other on putting together
identifier names from streams and catalogs.

### Integration Tests

Look at the `./setup/*.md` (e.g. `./setup/snowflake.md`) for how to set up integration environments.

With Gradle:

    ./gradlew :airbyte-integrations:bases:base-normalization:integrationTest

or directly with pytest:

    pytest airbyte-integrations/bases/base-normalization/integration_tests

or can also be invoked on github, thanks to the slash commands posted as comments:

    /test connector=bases/base-normalization

You can restrict the tests to a subset of destinations by specifying a comma separated list of destinations.
For example, let's say you are working on a change to normalization for Postgres, with Gradle:

    NORMALIZATION_TEST_TARGET=postgres ./gradlew :airbyte-integrations:bases:base-normalization:integrationTest

or directly with pytest:

    NORMALIZATION_TEST_TARGET=postgres  pytest airbyte-integrations/bases/base-normalization/integration_tests

Note that these tests are connecting and processing data on top of real data warehouse destinations.
Therefore, valid credentials files are expected to be injected in the `secrets/` folder in order to run
(not included in git repository).

This is usually automatically done by the CI thanks to the `tools/bin/ci_credentials.sh` script or you can
re-use the `destination_config.json` passed to destination connectors.

As normalization supports more and more destinations, tests are relying on an increasing number of destinations.
As a result, it is possible that the docker garbage collector is triggered to wipe "unused" docker images while the
integration tests for normalization are running. Thus, if you encounter errors about a connector's docker image not being
present locally (even though it was built beforehand), make sure to increase the docker image storage size of your docker engine ("defaultKeepStorage" for mac for example).

#### Integration Tests Definitions for test_ephemeral.py:
The test here focus on benchmarking the "ephemeral" materialization mode of dbt. Depending on the number of
columns in a catalog, this may throw exceptions and fail. This test ensures that we support reasonable number of columns in destination tables.

For example, known limitations that are now supported were:
* Ephemeral materialization with some generated models break with more than 490 columns with "maximum recursion depth exceeded", we now automatically switch to a little more scalable mode when generating dbt models by using views materialization.
* The tests are currently checking that at least a reasonably large number (1500) of columns can complete successfully.

However, limits on the destination still exists and can break for higher number of columns...

#### Integration Tests Definitions for test_normalization.py:

Some test suites can be selected to be versioned control in Airbyte git repository (or not).
This is useful to see direct impacts of code changes on downstream files generated or compiled
by normalization and dbt (directly in PR too). (_Simply refer to your test suite name in the
`git_versioned_tests` variable in the `base-normalization/integration_tests/test_normalization.py` file_)

We would typically choose small and meaningful test suites to include in git while others more complex tests
can be left out. They would still be run in a temporary directory and thrown away at the end of the tests.

They are defined, each one of them, in a separate directory in the resource folder.
For example, below, we would have 2 different tests "suites" with this hierarchy:

      base-normalization/integration_tests/resources/
      ├── test_suite1/
      │   ├── data_input/
      │   │   ├── catalog.json
      │   │   ├── messages.txt
      │   │   └── replace_identifiers.json
      │   ├── dbt_data_tests/
      │   │   ├── file1.sql
      │   │   └── file2.sql
      │   ├── dbt_schema_tests/
      │   │   ├── file1.yml
      │   │   └── file2.yml
      │   └── README.md
      └── test_suite2/
          ├── data_input/
          │   ├── catalog.json
          │   └── messages.txt
          ├── dbt_data_tests/
          ├── dbt_schema_tests/
          └── README.md

##### README.md:

Each test suite should have an optional `README.md` to include further details and descriptions of what the test is trying to verify and
how it is specifically built.

#### Integration Test Data Input:

##### data_input/catalog.json:

The `catalog.json` is the main input for normalization from which the dbt models files are being
generated from as it describes in JSON Schema format what the data structure is.

##### data_input/messages.txt:

The `messages.txt` are serialized Airbyte JSON records that should be sent to the destination as if they were
transmitted by a source. In this integration test, the files is read and "cat" through to the docker image of
each destination connectors to populate `_airbyte_raw_tables`. These tables are finally used as input
data for dbt to run from.

Note that `test_simple_streams` has additional message files, each representing a separate sync
(`messages_incremental.txt` and `messages_schema_change.txt`).

##### data_input/replace_identifiers.json:
The `replace_identifiers.json` contains maps of string patterns and values to replace in the `dbt_schema_tests`
and `dbt_data_tests` files to handle cross database compatibility.

Note that an additional step is added before replacing identifiers to change capitalization of identifiers in those
tests files. (to uppercase on snowflake and lowercase on redshift).

#### Integration Test Execution Flow:

These integration tests are run against all destinations that dbt can be executed on.
So, for each target destination, the steps run by the tests are:

1. Prepare the test execution workspace folder (copy skeleton from `dbt-project-template/`)
2. Generate a dbt `profiles.yml` file to connect to the target destination
3. Populate raw tables by running the target destination connectors, reading and uploading the
   `messages.txt` file as data input.
4. Run Normalization step to generate dbt models files from `catalog.json` input file.
5. Execute dbt cli command: `dbt run` from the test workspace folder to compile generated models files
   * from `models/generated/` folder
   * into `../build/(compiled|run)/airbyte_utils/models/generated/` folder
   * The final "run" SQL files are also copied (for archiving) to `final/` folder by the test script.
6. Deploy the `schema_tests` and `data_tests` files into the test workspace folder.
7. Execute dbt cli command: `dbt tests` from the test workspace folder to run verifications and checks with dbt.
8. Optional checks (nothing for the moment)

Note that the tests are using the normalization code from the python files directly, so it is not necessary to rebuild the docker images
in between when iterating on the code base. However, dbt cli and destination connectors are invoked via the dev docker images.
This means that if your `airbyte/normalization:dev` image doesn't have a working dbt installation, tests _will_ fail.
Similarly, if your `destination-xyz:dev` image doesn't work, then the base-normalization integration tests will fail.

#### Integration Test Checks:

##### dbt schema tests:

dbt allows out of the box to configure some tests as properties for an existing model (or source, seed, or snapshot).
This can be done in yaml format as described in the following documentation pages:

* [dbt schema-tests](https://docs.getdbt.com/docs/building-a-dbt-project/tests#schema-tests)
* [custom schema test](https://docs.getdbt.com/docs/guides/writing-custom-schema-tests)
* [dbt expectations](https://github.com/calogica/dbt-expectations)

We are leveraging these capabilities in these integration tests to verify some relationships in our
generated tables on the destinations.

##### dbt data tests:

Additionally, dbt also supports "data tests" which are specified as SQL queries.
A data test is a select statement that returns 0 records when the test is successful.

* [dbt data-tests](https://docs.getdbt.com/docs/building-a-dbt-project/tests#data-tests)

##### Notes using dbt seeds:

Because some functionalities are not stable enough on dbt side, it is difficult to properly use
`dbt seed` commands to populate a set of expected data tables at the moment. Hopefully, this can be
more easily be done in the future...

Related issues to watch on dbt progress to improve this aspects:
* <https://github.com/fishtown-analytics/dbt/issues/2959#issuecomment-747509782>
* <https://medium.com/hashmapinc/unit-testing-on-dbt-models-using-a-static-test-dataset-in-snowflake-dfd35549b5e2>

A nice improvement would be to add csv/json seed files as expected output data from tables.
The integration tests would verify that the content of such tables in the destination would match
these seed files or fail.

#### Debug dbt operations with local database
This only works for testing databases launched in local containers (e.g. postgres and mysql).

* In `dbt_integration_test.py`, comment out the `tear_down_db` method so that the relevant database container is not deleted.
* Find the name of the database container in the logs (e.g. by searching `Executing`).
* Connect to the container by running `docker exec -it <container-name> bash` in the commandline.
* Connect to the database inside the container (e.g. `mysql -u root` for mysql).
* Test the generated dbt operations directly in the database.

### Standard Destination Tests

Generally, to invoke standard destination tests, you run with gradle using:

    ./gradlew :airbyte-integrations:connectors:destination-<connector name>:integrationTest

For more details and options, you can also refer to the [testing connectors docs](../../../docs/connector-development/testing-connectors/README.md).

### Acceptance Tests

Please refer to the [developing docs](../../../docs/contributing-to-airbyte/developing-locally.md) on how to run Acceptance Tests.
