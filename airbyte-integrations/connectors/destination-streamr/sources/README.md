# Developing an Airbyte Source

## Requirements

* NodeJS >= 14.x
* Docker
* [Lerna](https://lerna.js.org/) -- Install with `npm i -g lerna`

## Helpful Documentation

The [Airbyte Specification
doc](https://docs.airbyte.io/understanding-airbyte/airbyte-specification)
describes each step of an Airbyte Source in detail. Also read [Airbyte's
development
guide](https://docs.airbyte.io/connector-development#adding-a-new-connector).
This repository will automatically release the sources as Docker images via
Github Actions.

## Development

### 1: Create source subproject

Clone the repo and copy the `sources/example-source` folder into a new folder
with the name of your new source. In this guide we will name our source
`new-source`, so we will create `sources/new-source`. In your new folder, update
`package.json` and the ExampleSource class in `src/index.ts` with the name of
your source.

Go back to the root folder of the repo and run `lerna bootstrap --hoist` to
install the dependencies for all the sources, including our `new-source`.

### 2: Implement Spec command

The first step of a source is returning specification of the configuration
parameters required to connect to the targeted system (e.g. API credentials,
URLs, etc). The provided Source class does this by returning the JSON-Schema
object in `resources/spec.json`. Update this file with your source's
configuration parameters, making sure to protect any sensitive parameters by
setting `"airbyte_secret": true` in their corresponding properties.

### 3: Implement Check command

After the configuration parameters are populated by the user, the source
verifies that the provided configuration is usable. This is done via the
`checkConnection` method in your source class. The `config` argument is a
dictionary of the parameters provided by the user. This method should verify
that all credentials in the configuration are valid, URLs are correct and
reachable, values are within proper ranges, etc.

The method returns a tuple of `[boolean, error]`, where the boolean indicates
whether or not the configuration is valid, and the error is an optional
[VError](https://github.com/joyent/node-verror) indicating what is invalid about
the configuration. If the boolean is true, the error should be undefined.

### 4: Implement Streams

A source contains one or more streams, which correspond to entity types of the
system your source is fetching data from. For example, a GitHub source would
have streams for users, commits, pull requests, etc. Each stream also has its
own arbitrary state for supporting incremental mode syncs. Implement your
streams, an example of which is in the `Builds` class in `src/stream.ts`,
and include them in your source via the `streams()` method of your source class.

Each stream has a JSON-Schema object defining the schema of the records that
this stream will fetch. This is done in the streams' `getJsonSchema()` method.
The source combines the results of calling this method on every stream to
create the Airbyte Catalog for the source's `discover` command.

The `primaryKey` property defines one or more fields of the record schema that
make up the unique key of each record.

The `cursorField` property defines one or more fields of the record schema that
Airbyte will check to determine whether a record is new or updated. This is
required to support syncing in incremental mode, and all our sources should
support incremental mode unless the data from source's technical system doesn't
have any timestamp-like fields that describe the freshness of each record.

The `readRecords()` method defines the logic for fetching data from your
source's technical system.

The `getUpdatedState()` method defines how to update the stream's arbitrary
state, given the current stream state and the most recent record generated from
`readRecords()`. The source calls this method after each record is generated.

The `stateCheckpointInterval` property determines how often a state message is
outputted and persisted. For example, if the interval is 100, the stream's state
will be persisted after reading every 100 records. It is undefined by default,
meaning the state is only persisted after all streams in the source have
finished reading records. Alternatively, you can implement [Stream
Slicing](https://docs.airbyte.io/connector-development/cdk-python/stream-slices)
by overriding the `streamSlices()` method, but for most cases, setting a
checkpoint interval should be sufficient.


## Testing

Each source must be tested against an Airbyte-provided docker image that runs a
series of tests to validate all the commands of a source.  Pull this image by
running `docker pull airbyte/source-acceptance-test`.

This test suite requires several json files defining a valid source
configuration and various input and expected outputs. The source-acceptance-test
docker image determines the paths for these files via the
`acceptance-test-config.yml` file in your source folder.

First create a valid source configuration for the tests. In your source folder,
create a new folder `secrets` and write your configuration to
`secrets/config.json`. For `example-source`, this JSON would be

```
{
  "server_url":"url",
  "user":"chris",     // only this value is validated by the example-source
  "token":"token"
}
```

Since this configuration would likely contains sensitive values, it cannot be
committed to the repo. To enable the Github Action Workflow to run the source
acceptance test, ask one of the Faros team members to add the configuration JSON
as a Github Repository Secret with the environment variable name
`<SOURCE_NAME>_TEST_CREDS`. So for `new-source`, the name would be
`NEW_SOURCE_TEST_CREDS`.

The `acceptance-test-config.yml` points to several other json files that enable
the tests for each of the source commands. See the [Source Acceptance Tests
Reference](https://docs.airbyte.io/connector-development/testing-connectors/source-acceptance-tests-reference)
for how those files are used. These files should be committed to the repo. If
your test file of expected records for the "basic_read" test contains sensitive
values because they are supposed to be written by the source, remove them from
the test file and set the `expect_records.extra_fields` option to true in the
yaml file. See the aforementioned test documentation for details on that option.

Run the tests with the provided script from the
root repo folder `./scripts/source-acceptance-test.sh <source>`, where
`<source>` is the folder name, e.g. `new-source`.
