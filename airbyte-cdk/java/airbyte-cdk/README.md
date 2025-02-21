# Developing with the Java CDK

This page will walk through the process of developing with the Java CDK.

- [Developing with the Java CDK](#developing-with-the-java-cdk)
  - [Intro to the Java CDK](#intro-to-the-java-cdk)
    - [What is included in the Java CDK?](#what-is-included-in-the-java-cdk)
    - [How is the CDK published?](#how-is-the-cdk-published)
  - [Using the Java CDK](#using-the-java-cdk)
    - [Building the CDK](#building-the-cdk)
    - [Bumping the CDK version](#bumping-the-cdk-version)
    - [Publishing the CDK](#publishing-the-cdk)
  - [Developing Connectors with the Java CDK](#developing-connectors-with-the-java-cdk)
    - [Referencing the CDK from Java connectors](#referencing-the-cdk-from-java-connectors)
    - [Developing a connector alongside the CDK](#developing-a-connector-alongside-the-cdk)
    - [Publishing the CDK and switching to a pinned CDK reference](#publishing-the-cdk-and-switching-to-a-pinned-cdk-reference)
    - [Troubleshooting CDK Dependency Caches](#troubleshooting-cdk-dependency-caches)
    - [Developing a connector against a pinned CDK version](#developing-a-connector-against-a-pinned-cdk-version)
  - [Changelog](#changelog)
    - [Java CDK](#java-cdk)

## Intro to the Java CDK

### What is included in the Java CDK?

The java CDK is comprised of separate modules, among which:

- `dependencies` and `core` - Shared classes for building connectors of all types.
- `db-sources` - Shared classes for building DB sources.
- `db-destinations` - Shared classes for building DB destinations.

Each CDK submodule may contain these elements:

- `src/main` - (Required.) The classes that will ship with the connector, providing capabilities to
  the connectors.
- `src/test` - (Required.) These are unit tests that run as part of every build of the CDK. They
  help ensure that CDK `main` code is in a healthy state.
- `src/testFixtures` - (Optional.) These shared classes are exported for connectors for use in the
  connectors' own test implementations. Connectors will have access to these classes within their
  unit and integration tests, but the classes will not be shipped with connectors when they are
  published.

### How is the CDK published?

The CDK is published as a set of jar files sharing a version number. Every submodule generates one
runtime jar for the main classes. If the submodule contains test fixtures, a second jar will be
published with the test fixtures classes.

Note: Connectors do not have to manage which jars they should depend on, as this is handled
automatically by the `airbyte-java-connector` plugin. See example below.

## Using the Java CDK

### Building the CDK

To build and test the Java CDK, execute the following:

```sh
./gradlew :airbyte-cdk:java:airbyte-cdk:build
```

### Bumping the CDK version

You will need to bump this version manually whenever you are making changes to code inside the CDK.

While under development, the next version number for the CDK is tracked in the file:
`airbyte-cdk/java/airbyte-cdk/core/src/main/resources/version.properties`.

If the CDK is not being modified, this file will contain the most recently published version number.

### Publishing the CDK

_⚠️ These steps should only be performed after all testing and approvals are in place on the PR. ⚠️_

The CDK can be published with a GitHub Workflow and a slash command which can be run by Airbyte
personnel.

To invoke via slash command (recommended), use the following syntax in a comment on the PR that
contains your changes:

```bash
/publish-java-cdk                # Run with the defaults (dry-run=false, force=false)
/publish-java-cdk dry-run=true   # Run in dry-run mode (no-op)
/publish-java-cdk force=true     # Force-publish if needing to replace an already published version
```

Note:

- Remember to **document your changes** in the Changelog section below.
- After you publish the CDK, remember to toggle `useLocalCdk` back to `false` in all connectors.
- Unless you specify `force=true`, the pipeline should fail if the version you are trying to publish
  already exists.
- By running the publish with `dry-run=true`, you can confirm the process is working as expected,
  without actually publishing the changes.
- In dry-run mode, you can also view and download the jars that are generated. To do so, navigate to
  the job status in GitHub Actions and navigate to the 'artifacts' section.
- You can also invoke manually in the GitHub Web UI. To do so: go to `Actions` tab, select the
  `Publish Java CDK` workflow, and click `Run workflow`.
- You can view and administer published CDK versions here:
  https://admin.cloudrepo.io/repository/airbyte-public-jars/io/airbyte/cdk
- The public endpoint for published CDK versions is here:
  https://airbyte.mycloudrepo.io/public/repositories/airbyte-public-jars/io/airbyte/cdk/

## Developing Connectors with the Java CDK

### Referencing the CDK from Java connectors

You can reference the CDK in your connector's `build.gradle` file:

```groovy
plugins {
    id 'airbyte-java-connector'
}

airbyteJavaConnector {
    cdkVersionRequired = '0.1.0'   // The CDK version to pin to.
    features = ['db-destinations'] // An array of CDK features to depend on.
    useLocalCdk = false            // Use 'true' to use a live reference to the
                                   // local cdk project.
}

```

Replace `0.1.0` with the CDK version you are working with. If you're actively developing the CDK and
want to use the latest version locally, use the `useLocalCdk` flag to use the live CDK code during
builds and tests.

### Developing a connector alongside the CDK

You can iterate on changes in the CDK local and test them in the connector without needing to
publish the CDK changes publicly.

When modifying the CDK and a connector in the same PR or branch, please use the following steps:

1. Set the version of the CDK in `version.properties` to the next appropriate version number and add
   a description in the `Changelog` at the bottom of this readme file.
2. Modify your connector's build.gradle file as follows:
   1. Set `useLocalCdk` to `true` in the connector you are working on. This will ensure the
      connector always uses the local CDK definitions instead of the published version.
   2. Set `cdkVersionRequired` to use the new _to-be-published_ CDK version.

After the above, you can build and test your connector as usual. Gradle will automatically use the
local CDK code files while you are working on the connector.

### Publishing the CDK and switching to a pinned CDK reference

Once you are done developing and testing your CDK changes:

1. Publish the CDK using the instructions here in this readme.
2. After publishing the CDK, update the `useLocalCdk` setting to `false`.

### Troubleshooting CDK Dependency Caches

Note: after switching between a local and a pinned CDK reference, you may need to refresh dependency
caches in Gradle and/or your IDE.

In Gradle, you can use the CLI arg `--refresh-dependencies` the next time you build or test your
connector, which will ensure that the correct version of the CDK is used after toggling the
`useLocalCdk` value.

### Developing a connector against a pinned CDK version

You can always pin your connector to a prior stable version of the CDK, which may not match what is
the latest version in the `airbyte` repo. For instance, your connector can be pinned to `0.1.1`
while the latest version may be `0.2.0`.

Maven and Gradle will automatically reference the correct (pinned) version of the CDK for your
connector, and you can use your local IDE to browse the prior version of the codebase that
corresponds to that version.

## Changelog

### Java CDK

| Version    | Date       | Pull Request                                                | Subject                                                                                                                                                        |
|:-----------|:-----------|:------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.48.7     | 2025-01-26 | [\#51596](https://github.com/airbytehq/airbyte/pull/51596)  | Make efficient table discovery during read                                                                                                                     |
| 0.48.6     | 2025-01-26 | [\#51596](https://github.com/airbytehq/airbyte/pull/51596)  | Fix flaky source mssql tests                                                                                                                                   |
| 0.48.5     | 2025-01-16 | [\#51583](https://github.com/airbytehq/airbyte/pull/51583)  | Also save SSL key to /tmp in destination-postgres                                                                                                              |
| 0.48.4     | 2024-12-24 | [\#50410](https://github.com/airbytehq/airbyte/pull/50410)  | Save SSL key to /tmp                                                                                                                                           |
| 0.48.3     | 2024-12-23 | [\#49858](https://github.com/airbytehq/airbyte/pull/49858)  | Relax various Destination CDK methods visibility.                                                                                                              |
| 0.48.1     | 2024-11-13 | [\#48482](https://github.com/airbytehq/airbyte/pull/48482)  | Adding support converting very large numbers via BigInteger                                                                                                    |
| 0.48.0     | 2024-10-23 | [\#46302](https://github.com/airbytehq/airbyte/pull/46302)  | Add support for file transfer                                                                                                                                  |
| 0.47.3     | 2024-10-23 | [\#46689](https://github.com/airbytehq/airbyte/pull/46689)  | Split DestinationAcceptanceTest                                                                                                                                |
| 0.47.2     | 2024-10-21 | [\#47216](https://github.com/airbytehq/airbyte/pull/47216)  | improve java compatibiilty                                                                                                                                     |
| 0.47.1     | 2024-09-27 | [\#45397](https://github.com/airbytehq/airbyte/pull/45397)  | Allow logical replication from Postgres 16 read-replicas                                                                                                       |
| 0.47.0     | 2024-09-26 | [\#42030](https://github.com/airbytehq/airbyte/pull/42030)  | minor refactor                                                                                                                                                 |
| 0.46.1     | 2024-09-20 | [\#45700](https://github.com/airbytehq/airbyte/pull/45700)  | Destinations: Fix bug in parsing jsonschema                                                                                                                    |
| 0.46.0     | 2024-09-18 | [\#45432](https://github.com/airbytehq/airbyte/pull/45432)  | upgrade all libraries to latest version                                                                                                                        |
| 0.45.1     | 2024-09-17 | [\#45638](https://github.com/airbytehq/airbyte/pull/45638)  | upgrade apache mina sshd to 2.13.2 to handle openssh tcpkeepalive requests                                                                                     |
| 0.45.0     | 2024-09-16 | [\#45469](https://github.com/airbytehq/airbyte/pull/45469)  | Fix some race conditions, improve thread filtering, improve test logging                                                                                       |
| 0.44.22    | 2024-09-10 | [\#45368](https://github.com/airbytehq/airbyte/pull/45368)  | Remove excessive debezium logging                                                                                                                              |
| 0.44.21    | 2024-09-04 | [\#45143](https://github.com/airbytehq/airbyte/pull/45143)  | S3-destination: don't overwrite existing files, skip those file indexes instead                                                                                |
| 0.44.20    | 2024-08-30 | [\#44933](https://github.com/airbytehq/airbyte/pull/44933)  | Avro/Parquet destinations: handle `{}` schemas inside objects/arrays                                                                                           |
| 0.44.19    | 2024-08-20 | [\#44476](https://github.com/airbytehq/airbyte/pull/44476)  | Increase Jackson message length limit to 100mb                                                                                                                 |
| 0.44.18    | 2024-08-22 | [\#44759](https://github.com/airbytehq/airbyte/pull/44759)  | Improve handling of incoming debezium change events                                                                                                            |
| 0.44.17    | 2024-08-27 | [\#44832](https://github.com/airbytehq/airbyte/pull/44832)  | Fix issues where some error messages with upper cases do not get matched by the error translation framework.                                                   |
| 0.44.16    | 2024-08-22 | [\#44505](https://github.com/airbytehq/airbyte/pull/44505)  | Destinations: add sqlgenerator testing for mixed-case stream name                                                                                              |
| 0.44.15    | ?????????? | [\#?????](https://github.com/airbytehq/airbyte/pull/?????)  | ?????                                                                                                                                                          |
| 0.44.14    | 2024-08-19 | [\#42503](https://github.com/airbytehq/airbyte/pull/42503)  | Destinations (refreshes) - correctly detect existing raw/final table of the correct generation during truncate sync                                            |
| 0.44.13    | 2024-08-14 | [\#42579](https://github.com/airbytehq/airbyte/pull/42579)  | S3 destination - OVERWRITE: keep files until successful sync of same generationId                                                                              |
| 0.44.5     | 2024-08-09 | [\#43374](https://github.com/airbytehq/airbyte/pull/43374)  | S3 destination V2 fields, conversion improvements, bugfixes                                                                                                    |
| 0.44.4     | 2024-08-08 | [\#43410](https://github.com/airbytehq/airbyte/pull/43330)  | Better logs for counting info to state message.                                                                                                                |
| 0.44.3     | 2024-08-07 | [\#43330](https://github.com/airbytehq/airbyte/pull/43330)  | make TypingDedupingTest aware of column name renaming.                                                                                                         |
| 0.44.3     | 2024-08-07 | [\#43329](https://github.com/airbytehq/airbyte/pull/43329)  | move generationIdHandling to its own class.                                                                                                                    |
| 0.44.2     | 2024-08-06 | [\#42869](https://github.com/airbytehq/airbyte/pull/42869)  | Add logs about counting info to state message.                                                                                                                 |
| 0.44.1     | 2024-08-01 | [\#42550](https://github.com/airbytehq/airbyte/pull/42550)  | Fix error on reporting counts.                                                                                                                                 |
| 0.44.0     | 2024-08-01 | [\#42405](https://github.com/airbytehq/airbyte/pull/42405)  | s3-destinations: Use async framework, adapt to support refreshes                                                                                               |
| 0.43.6     | 2024-07-30 | [\#42540](https://github.com/airbytehq/airbyte/pull/42540)  | Fix generationId handling for destinations                                                                                                                     |
| 0.43.6     | 2024-07-30 | [\#42514](https://github.com/airbytehq/airbyte/pull/42514)  | Add tests around generationId handling for destinations.                                                                                                       |
| 0.43.4     | 2024-07-28 | [\#42839](https://github.com/airbytehq/airbyte/pull/42839)  | Fix error translation framework to not rethrow ConfigErrorException and TransientErrorException.                                                               |
| 0.43.3     | 2024-07-22 | [\#42417](https://github.com/airbytehq/airbyte/pull/42417)  | Handle null exception message in ConnectorExceptionHandler.                                                                                                    |
| 0.43.2     | 2024-07-22 | [\#42431](https://github.com/airbytehq/airbyte/pull/42431)  | Filter out debezium message change events                                                                                                                      |
| 0.43.1     | 2024-07-22 | [\#41622](https://github.com/airbytehq/airbyte/pull/41622)  | Fix null safety bug in debezium event processing                                                                                                               |
| 0.43.0     | 2024-07-17 | [\#41954](https://github.com/airbytehq/airbyte/pull/41954)  | fix refreshes for connectors using the old SqlOperations                                                                                                       |
| 0.43.0     | 2024-07-17 | [\#42017](https://github.com/airbytehq/airbyte/pull/42017)  | bump postgres-jdbc version                                                                                                                                     |
| 0.43.0     | 2024-07-17 | [\#42015](https://github.com/airbytehq/airbyte/pull/42015)  | wait until migration before creating the Writeconfig objects                                                                                                   |
| 0.43.0     | 2024-07-17 | [\#41953](https://github.com/airbytehq/airbyte/pull/41953)  | add generationId and syncId to SqlOperations functions                                                                                                         |
| 0.43.0     | 2024-07-17 | [\#41952](https://github.com/airbytehq/airbyte/pull/41952)  | rename and add fields in WriteConfig                                                                                                                           |
| 0.43.0     | 2024-07-17 | [\#41951](https://github.com/airbytehq/airbyte/pull/41951)  | remove nullables in JdbcBufferedConsumerFactory                                                                                                                |
| 0.43.0     | 2024-07-17 | [\#41950](https://github.com/airbytehq/airbyte/pull/41950)  | remove unused classes                                                                                                                                          |
| 0.42.2     | 2024-07-21 | [\#42122](https://github.com/airbytehq/airbyte/pull/42122)  | Support for Debezium resync and shutdown scenarios.                                                                                                            |
| 0.42.2     | 2024-07-04 | [\#40208](https://github.com/airbytehq/airbyte/pull/40208)  | Implement a new connector error handling and translation framework                                                                                             |
| 0.41.8     | 2024-07-18 | [\#42068](https://github.com/airbytehq/airbyte/pull/42068)  | Add analytics message for WASS occurrence.                                                                                                                     |
| 0.41.7     | 2024-07-17 | [\#42055](https://github.com/airbytehq/airbyte/pull/42055)  | Add debezium heartbeat timeout back to shutdown debezium.                                                                                                      |
| 0.41.6     | 2024-07-17 | [\#41996](https://github.com/airbytehq/airbyte/pull/41996)  | Fix java interop compilation issue in Config/TransientErrorException.                                                                                          |
| 0.41.5     | 2024-07-16 | [\#42011] (https://github.com/airbytehq/airbyte/pull/42011) | Async consumer accepts null default namespace                                                                                                                  |
| 0.41.4     | 2024-07-15 | [\#41959](https://github.com/airbytehq/airbyte/pull/41959)  | Allow setting `internal_message` in Config/TransientErrorException. Destinations: shorten error message for INCOMPLETE stream status.                          |
| 0.41.3     | 2024-07-15 | [\#41680](https://github.com/airbytehq/airbyte/pull/41680)  | Fix: CompletableFutures.allOf now handles empty list and `Throwable`                                                                                           |
| 0.41.2     | 2024-07-12 | [\#40567](https://github.com/airbytehq/airbyte/pull/40567)  | Fix BaseSqlGenerator test case (generation_id support); update minimum platform version for refreshes support.                                                 |
| 0.41.1     | 2024-07-11 | [\#41212](https://github.com/airbytehq/airbyte/pull/41212)  | Improve debezium logging.                                                                                                                                      |
| 0.41.0     | 2024-07-11 | [\#38240](https://github.com/airbytehq/airbyte/pull/38240)  | Sources : Changes in CDC interfaces to support WASS algorithm                                                                                                  |
| 0.40.11    | 2024-07-08 | [\#41041](https://github.com/airbytehq/airbyte/pull/41041)  | Destinations: Fix truncate refreshes incorrectly discarding data if successful attempt had 0 records                                                           |
| 0.40.10    | 2024-07-05 | [\#40719](https://github.com/airbytehq/airbyte/pull/40719)  | Update test to refrlect isResumable field in catalog                                                                                                           |
| 0.40.9     | 2024-07-01 | [\#39473](https://github.com/airbytehq/airbyte/pull/39473)  | minor changes around error logging and testing                                                                                                                 |
| 0.40.8     | 2024-07-01 | [\#40499](https://github.com/airbytehq/airbyte/pull/40499)  | Make JdbcDatabase SQL statement logging optional; add generation_id support to JdbcSqlGenerator                                                                |
| 0.40.7     | 2024-07-01 | [\#40516](https://github.com/airbytehq/airbyte/pull/40516)  | Remove dbz hearbeat.                                                                                                                                           |
| ~~0.40.6~~ |            |                                                             | (this version does not exist)                                                                                                                                  |
| 0.40.5     | 2024-06-26 | [\#40517](https://github.com/airbytehq/airbyte/pull/40517)  | JdbcDatabase.executeWithinTransaction allows disabling SQL statement logging                                                                                   |
| 0.40.4     | 2024-06-18 | [\#40254](https://github.com/airbytehq/airbyte/pull/40254)  | Destinations: Do not throw on unrecognized airbyte message type (ignore message instead)                                                                       |
| 0.40.3     | 2024-06-18 | [\#39526](https://github.com/airbytehq/airbyte/pull/39526)  | Destinations: INCOMPLETE stream status is a TRANSIENT error rather than SYSTEM                                                                                 |
| 0.40.2     | 2024-06-18 | [\#39552](https://github.com/airbytehq/airbyte/pull/39552)  | Destinations: Throw error if the ConfiguredCatalog has no streams                                                                                              |
| 0.40.1     | 2024-06-14 | [\#39349](https://github.com/airbytehq/airbyte/pull/39349)  | Source stats for full refresh streams                                                                                                                          |
| 0.40.0     | 2024-06-17 | [\#38622](https://github.com/airbytehq/airbyte/pull/38622)  | Destinations: Implement refreshes logic in AbstractStreamOperation                                                                                             |
| 0.39.0     | 2024-06-17 | [\#38067](https://github.com/airbytehq/airbyte/pull/38067)  | Destinations: Breaking changes for refreshes (fail on INCOMPLETE stream status; ignore OVERWRITE sync mode)                                                    |
| 0.38.3     | 2024-06-25 | [\#40499](https://github.com/airbytehq/airbyte/pull/40499)  | (backport) Make JdbcDatabase SQL statement logging optional; add generation_id support to JdbcSqlGenerator                                                     |
| 0.38.2     | 2024-06-14 | [\#39460](https://github.com/airbytehq/airbyte/pull/39460)  | Bump postgres JDBC driver version                                                                                                                              |
| 0.38.1     | 2024-06-13 | [\#39445](https://github.com/airbytehq/airbyte/pull/39445)  | Sources: More CDK changes to handle big initial snapshots.                                                                                                     |
| 0.38.0     | 2024-06-11 | [\#39405](https://github.com/airbytehq/airbyte/pull/39405)  | Sources: Debezium properties manager interface changed to accept a list of streams to scope to                                                                 |
| 0.37.1     | 2024-06-10 | [\#38075](https://github.com/airbytehq/airbyte/pull/38075)  | Destinations: Track stream statuses in async framework                                                                                                         |
| 0.37.0     | 2024-06-10 | [\#38121](https://github.com/airbytehq/airbyte/pull/38121)  | Destinations: Set default namespace via CatalogParser                                                                                                          |
| 0.36.8     | 2024-06-07 | [\#38763](https://github.com/airbytehq/airbyte/pull/38763)  | Increase Jackson message length limit                                                                                                                          |
| 0.36.7     | 2024-06-06 | [\#39220](https://github.com/airbytehq/airbyte/pull/39220)  | Handle null messages in ConnectorExceptionUtil                                                                                                                 |
| 0.36.6     | 2024-06-05 | [\#39106](https://github.com/airbytehq/airbyte/pull/39106)  | Skip write to storage with 0 byte file                                                                                                                         |
| 0.36.5     | 2024-06-01 | [\#38792](https://github.com/airbytehq/airbyte/pull/38792)  | Throw config exception if no selectable table exists in user provided schemas                                                                                  |
| 0.36.4     | 2024-05-31 | [\#38824](https://github.com/airbytehq/airbyte/pull/38824)  | Param marked as non-null to nullable in JdbcDestinationHandler for NPE fix                                                                                     |
| 0.36.2     | 2024-05-29 | [\#38538](https://github.com/airbytehq/airbyte/pull/38357)  | Exit connector when encountering a config error.                                                                                                               |
| 0.36.0     | 2024-05-29 | [\#38358](https://github.com/airbytehq/airbyte/pull/38358)  | Plumb generation_id / sync_id to destinations code                                                                                                             |
| 0.35.16    | 2024-06-25 | [\#40517](https://github.com/airbytehq/airbyte/pull/40517)  | (backport) JdbcDatabase.executeWithinTransaction allows disabling SQL statement logging                                                                        |
| 0.35.15    | 2024-05-31 | [\#38824](https://github.com/airbytehq/airbyte/pull/38824)  | Param marked as non-null to nullable in JdbcDestinationHandler for NPE fix                                                                                     |
| 0.35.14    | 2024-05-28 | [\#38738](https://github.com/airbytehq/airbyte/pull/38738)  | make ThreadCreationInfo cast as nullable                                                                                                                       |
| 0.35.13    | 2024-05-28 | [\#38632](https://github.com/airbytehq/airbyte/pull/38632)  | minor changes to allow conversion of snowflake tests to kotlin                                                                                                 |
| 0.35.12    | 2024-05-23 | [\#38638](https://github.com/airbytehq/airbyte/pull/38638)  | Minor change to support Snowflake conversion to Kotlin                                                                                                         |
| 0.35.11    | 2024-05-23 | [\#38357](https://github.com/airbytehq/airbyte/pull/38357)  | This release fixes an error on the previous release.                                                                                                           |
| 0.35.10    | 2024-05-23 | [\#38357](https://github.com/airbytehq/airbyte/pull/38357)  | Add shared code for db sources stream status trace messages and testing.                                                                                       |
| 0.35.9     | 2024-05-23 | [\#38586](https://github.com/airbytehq/airbyte/pull/38586)  | code cleanup                                                                                                                                                   |
| 0.35.9     | 2024-05-23 | [\#37583](https://github.com/airbytehq/airbyte/pull/37583)  | code cleanup                                                                                                                                                   |
| 0.35.9     | 2024-05-23 | [\#37555](https://github.com/airbytehq/airbyte/pull/37555)  | code cleanup                                                                                                                                                   |
| 0.35.9     | 2024-05-23 | [\#37540](https://github.com/airbytehq/airbyte/pull/37540)  | code cleanup                                                                                                                                                   |
| 0.35.9     | 2024-05-23 | [\#37539](https://github.com/airbytehq/airbyte/pull/37539)  | code cleanup                                                                                                                                                   |
| 0.35.9     | 2024-05-23 | [\#37538](https://github.com/airbytehq/airbyte/pull/37538)  | code cleanup                                                                                                                                                   |
| 0.35.9     | 2024-05-23 | [\#37537](https://github.com/airbytehq/airbyte/pull/37537)  | code cleanup                                                                                                                                                   |
| 0.35.9     | 2024-05-23 | [\#37518](https://github.com/airbytehq/airbyte/pull/37518)  | code cleanup                                                                                                                                                   |
| 0.35.8     | 2024-05-22 | [\#38572](https://github.com/airbytehq/airbyte/pull/38572)  | Add a temporary static method to decouple SnowflakeDestination from AbstractJdbcDestination                                                                    |
| 0.35.7     | 2024-05-20 | [\#38357](https://github.com/airbytehq/airbyte/pull/38357)  | Decouple create namespace from per stream operation interface.                                                                                                 |
| 0.35.6     | 2024-05-17 | [\#38107](https://github.com/airbytehq/airbyte/pull/38107)  | New interfaces for Destination connectors to plug into AsyncStreamConsumer                                                                                     |
| 0.35.5     | 2024-05-17 | [\#38204](https://github.com/airbytehq/airbyte/pull/38204)  | add assume-role authentication to s3                                                                                                                           |
| 0.35.2     | 2024-05-13 | [\#38104](https://github.com/airbytehq/airbyte/pull/38104)  | Handle transient error messages                                                                                                                                |
| 0.35.0     | 2024-05-13 | [\#38127](https://github.com/airbytehq/airbyte/pull/38127)  | Destinations: Populate generation/sync ID on StreamConfig                                                                                                      |
| 0.34.4     | 2024-05-10 | [\#37712](https://github.com/airbytehq/airbyte/pull/37712)  | make sure the exceptionHandler always terminates                                                                                                               |
| 0.34.3     | 2024-05-10 | [\#38095](https://github.com/airbytehq/airbyte/pull/38095)  | Minor changes for databricks connector                                                                                                                         |
| 0.34.1     | 2024-05-07 | [\#38030](https://github.com/airbytehq/airbyte/pull/38030)  | Add support for transient errors                                                                                                                               |
| 0.34.0     | 2024-05-01 | [\#37712](https://github.com/airbytehq/airbyte/pull/37712)  | Destinations: Remove incremental T+D                                                                                                                           |
| 0.33.2     | 2024-05-03 | [\#37824](https://github.com/airbytehq/airbyte/pull/37824)  | improve source acceptance tests                                                                                                                                |
| 0.33.1     | 2024-05-03 | [\#37824](https://github.com/airbytehq/airbyte/pull/37824)  | Add a unit test for cursor based sync                                                                                                                          |
| 0.33.0     | 2024-05-03 | [\#36935](https://github.com/airbytehq/airbyte/pull/36935)  | Destinations: Enable non-safe-casting DV2 tests                                                                                                                |
| 0.32.0     | 2024-05-03 | [\#36929](https://github.com/airbytehq/airbyte/pull/36929)  | Destinations: Assorted DV2 changes for mysql                                                                                                                   |
| 0.31.7     | 2024-05-02 | [\#36910](https://github.com/airbytehq/airbyte/pull/36910)  | changes for destination-snowflake                                                                                                                              |
| 0.31.6     | 2024-05-02 | [\#37746](https://github.com/airbytehq/airbyte/pull/37746)  | debuggability improvements.                                                                                                                                    |
| 0.31.5     | 2024-04-30 | [\#37758](https://github.com/airbytehq/airbyte/pull/37758)  | Set debezium max retries to zero                                                                                                                               |
| 0.31.4     | 2024-04-30 | [\#37754](https://github.com/airbytehq/airbyte/pull/37754)  | Add DebeziumEngine notification log                                                                                                                            |
| 0.31.3     | 2024-04-30 | [\#37726](https://github.com/airbytehq/airbyte/pull/37726)  | Remove debezium retries                                                                                                                                        |
| 0.31.2     | 2024-04-30 | [\#37507](https://github.com/airbytehq/airbyte/pull/37507)  | Better error messages when switching between global/per-stream modes.                                                                                          |
| 0.31.0     | 2024-04-26 | [\#37584](https://github.com/airbytehq/airbyte/pull/37584)  | Update S3 destination deps to exclude zookeeper and hadoop-yarn-common                                                                                         |
| 0.30.11    | 2024-04-25 | [\#36899](https://github.com/airbytehq/airbyte/pull/36899)  | changes for bigQuery destination.                                                                                                                              |
| 0.30.10    | 2024-04-24 | [\#37541](https://github.com/airbytehq/airbyte/pull/37541)  | remove excessive logging                                                                                                                                       |
| 0.30.9     | 2024-04-24 | [\#37477](https://github.com/airbytehq/airbyte/pull/37477)  | remove unnecessary logs                                                                                                                                        |
| 0.30.7     | 2024-04-23 | [\#37477](https://github.com/airbytehq/airbyte/pull/37477)  | fix kotlin warnings in core CDK submodule                                                                                                                      |
| 0.30.7     | 2024-04-23 | [\#37484](https://github.com/airbytehq/airbyte/pull/37484)  | fix kotlin warnings in dependencies CDK submodule                                                                                                              |
| 0.30.7     | 2024-04-23 | [\#37479](https://github.com/airbytehq/airbyte/pull/37479)  | fix kotlin warnings in azure-destination, datastore-{bigquery,mongo,postgres} CDK submodules                                                                   |
| 0.30.7     | 2024-04-23 | [\#37481](https://github.com/airbytehq/airbyte/pull/37481)  | fix kotlin warnings in destination CDK submodules                                                                                                              |
| 0.30.7     | 2024-04-23 | [\#37482](https://github.com/airbytehq/airbyte/pull/37482)  | fix kotlin warnings in db-sources CDK submodule                                                                                                                |
| 0.30.6     | 2024-04-19 | [\#37442](https://github.com/airbytehq/airbyte/pull/37442)  | Destinations: Rename File format related classes to be agnostic of S3                                                                                          |
| 0.30.3     | 2024-04-12 | [\#37106](https://github.com/airbytehq/airbyte/pull/37106)  | Destinations: Simplify constructors in `AsyncStreamConsumer`                                                                                                   |
| 0.30.2     | 2024-04-12 | [\#36926](https://github.com/airbytehq/airbyte/pull/36926)  | Destinations: Remove `JdbcSqlOperations#formatData`; misc changes for java interop                                                                             |
| 0.30.1     | 2024-04-11 | [\#36919](https://github.com/airbytehq/airbyte/pull/36919)  | Fix regression in sources conversion of null values                                                                                                            |
| 0.30.0     | 2024-04-11 | [\#36974](https://github.com/airbytehq/airbyte/pull/36974)  | Destinations: Pass config to jdbc sqlgenerator; allow cascade drop                                                                                             |
| 0.29.13    | 2024-04-10 | [\#36981](https://github.com/airbytehq/airbyte/pull/36981)  | DB sources : Emit analytics for data type serialization errors.                                                                                                |
| 0.29.12    | 2024-04-10 | [\#36973](https://github.com/airbytehq/airbyte/pull/36973)  | Destinations: Make flush batch size configurable for JdbcInsertFlush                                                                                           |
| 0.29.11    | 2024-04-10 | [\#36865](https://github.com/airbytehq/airbyte/pull/36865)  | Sources : Remove noisy log line.                                                                                                                               |
| 0.29.10    | 2024-04-10 | [\#36805](https://github.com/airbytehq/airbyte/pull/36805)  | Destinations: Enhance CatalogParser name collision handling; add DV2 tests for long identifiers                                                                |
| 0.29.9     | 2024-04-09 | [\#36047](https://github.com/airbytehq/airbyte/pull/36047)  | Destinations: CDK updates for raw-only destinations                                                                                                            |
| 0.29.8     | 2024-04-08 | [\#36868](https://github.com/airbytehq/airbyte/pull/36868)  | Destinations: s3-destinations Compilation fixes for connector                                                                                                  |
| 0.29.7     | 2024-04-08 | [\#36768](https://github.com/airbytehq/airbyte/pull/36768)  | Destinations: Make destination state fetch/commit logic more resilient to errors                                                                               |
| 0.29.6     | 2024-04-05 | [\#36577](https://github.com/airbytehq/airbyte/pull/36577)  | Do not send system_error trace message for config exceptions.                                                                                                  |
| 0.29.5     | 2024-04-05 | [\#36620](https://github.com/airbytehq/airbyte/pull/36620)  | Missed changes - open for extension for destination-postgres                                                                                                   |
| 0.29.3     | 2024-04-04 | [\#36759](https://github.com/airbytehq/airbyte/pull/36759)  | Minor fixes.                                                                                                                                                   |
| 0.29.3     | 2024-04-04 | [\#36706](https://github.com/airbytehq/airbyte/pull/36706)  | Enabling spotbugs for s3-destination.                                                                                                                          |
| 0.29.3     | 2024-04-03 | [\#36705](https://github.com/airbytehq/airbyte/pull/36705)  | Enabling spotbugs for db-sources.                                                                                                                              |
| 0.29.3     | 2024-04-03 | [\#36704](https://github.com/airbytehq/airbyte/pull/36704)  | Enabling spotbugs for datastore-postgres.                                                                                                                      |
| 0.29.3     | 2024-04-03 | [\#36703](https://github.com/airbytehq/airbyte/pull/36703)  | Enabling spotbugs for gcs-destination.                                                                                                                         |
| 0.29.3     | 2024-04-03 | [\#36702](https://github.com/airbytehq/airbyte/pull/36702)  | Enabling spotbugs for db-destinations.                                                                                                                         |
| 0.29.3     | 2024-04-03 | [\#36701](https://github.com/airbytehq/airbyte/pull/36701)  | Enabling spotbugs for typing_and_deduping.                                                                                                                     |
| 0.29.3     | 2024-04-03 | [\#36612](https://github.com/airbytehq/airbyte/pull/36612)  | Enabling spotbugs for dependencies.                                                                                                                            |
| 0.29.5     | 2024-04-05 | [\#36577](https://github.com/airbytehq/airbyte/pull/36577)  | Do not send system_error trace message for config exceptions.                                                                                                  |
| 0.29.3     | 2024-04-04 | [\#36759](https://github.com/airbytehq/airbyte/pull/36759)  | Minor fixes.                                                                                                                                                   |
| 0.29.3     | 2024-04-04 | [\#36706](https://github.com/airbytehq/airbyte/pull/36706)  | Enabling spotbugs for s3-destination.                                                                                                                          |
| 0.29.3     | 2024-04-03 | [\#36705](https://github.com/airbytehq/airbyte/pull/36705)  | Enabling spotbugs for db-sources.                                                                                                                              |
| 0.29.3     | 2024-04-03 | [\#36704](https://github.com/airbytehq/airbyte/pull/36704)  | Enabling spotbugs for datastore-postgres.                                                                                                                      |
| 0.29.3     | 2024-04-03 | [\#36703](https://github.com/airbytehq/airbyte/pull/36703)  | Enabling spotbugs for gcs-destination.                                                                                                                         |
| 0.29.3     | 2024-04-03 | [\#36702](https://github.com/airbytehq/airbyte/pull/36702)  | Enabling spotbugs for db-destinations.                                                                                                                         |
| 0.29.3     | 2024-04-03 | [\#36701](https://github.com/airbytehq/airbyte/pull/36701)  | Enabling spotbugs for typing_and_deduping.                                                                                                                     |
| 0.29.3     | 2024-04-03 | [\#36612](https://github.com/airbytehq/airbyte/pull/36612)  | Enabling spotbugs for dependencies.                                                                                                                            |
| 0.29.2     | 2024-04-04 | [\#36845](https://github.com/airbytehq/airbyte/pull/36772)  | Changes to make source-mongo compileable                                                                                                                       |
| 0.29.1     | 2024-04-03 | [\#36772](https://github.com/airbytehq/airbyte/pull/36772)  | Changes to make source-mssql compileable                                                                                                                       |
| 0.29.0     | 2024-04-02 | [\#36759](https://github.com/airbytehq/airbyte/pull/36759)  | Build artifact publication changes and fixes.                                                                                                                  |
| 0.28.21    | 2024-04-02 | [\#36673](https://github.com/airbytehq/airbyte/pull/36673)  | Change the destination message parsing to use standard java/kotlin classes. Adds logging to catch empty lines.                                                 |
| 0.28.20    | 2024-04-01 | [\#36584](https://github.com/airbytehq/airbyte/pull/36584)  | Changes to make source-postgres compileable                                                                                                                    |
| 0.28.19    | 2024-03-29 | [\#36619](https://github.com/airbytehq/airbyte/pull/36619)  | Changes to make destination-postgres compileable                                                                                                               |
| 0.28.19    | 2024-03-29 | [\#36588](https://github.com/airbytehq/airbyte/pull/36588)  | Changes to make destination-redshift compileable                                                                                                               |
| 0.28.19    | 2024-03-29 | [\#36610](https://github.com/airbytehq/airbyte/pull/36610)  | remove airbyte-api generation, pull depdendency jars instead                                                                                                   |
| 0.28.19    | 2024-03-29 | [\#36611](https://github.com/airbytehq/airbyte/pull/36611)  | disable spotbugs for CDK tes and testFixtures tasks                                                                                                            |
| 0.28.18    | 2024-03-28 | [\#36606](https://github.com/airbytehq/airbyte/pull/36574)  | disable spotbugs for CDK tes and testFixtures tasks                                                                                                            |
| 0.28.18    | 2024-03-28 | [\#36574](https://github.com/airbytehq/airbyte/pull/36574)  | Fix ContainerFactory                                                                                                                                           |
| 0.28.18    | 2024-03-27 | [\#36570](https://github.com/airbytehq/airbyte/pull/36570)  | Convert missing s3-destinations tests to Kotlin                                                                                                                |
| 0.28.18    | 2024-03-27 | [\#36446](https://github.com/airbytehq/airbyte/pull/36446)  | Convert dependencies submodule to Kotlin                                                                                                                       |
| 0.28.18    | 2024-03-27 | [\#36445](https://github.com/airbytehq/airbyte/pull/36445)  | Convert functional out Checked interfaces to kotlin                                                                                                            |
| 0.28.18    | 2024-03-27 | [\#36444](https://github.com/airbytehq/airbyte/pull/36444)  | Use apache-commons classes in our Checked functional interfaces                                                                                                |
| 0.28.18    | 2024-03-27 | [\#36467](https://github.com/airbytehq/airbyte/pull/36467)  | Convert #36465 to Kotlin                                                                                                                                       |
| 0.28.18    | 2024-03-27 | [\#36473](https://github.com/airbytehq/airbyte/pull/36473)  | Convert convert #36396 to Kotlin                                                                                                                               |
| 0.28.18    | 2024-03-27 | [\#36439](https://github.com/airbytehq/airbyte/pull/36439)  | Convert db-destinations submodule to Kotlin                                                                                                                    |
| 0.28.18    | 2024-03-27 | [\#36438](https://github.com/airbytehq/airbyte/pull/36438)  | Convert db-sources submodule to Kotlin                                                                                                                         |
| 0.28.18    | 2024-03-26 | [\#36437](https://github.com/airbytehq/airbyte/pull/36437)  | Convert gsc submodule to Kotlin                                                                                                                                |
| 0.28.18    | 2024-03-26 | [\#36421](https://github.com/airbytehq/airbyte/pull/36421)  | Convert typing-deduping submodule to Kotlin                                                                                                                    |
| 0.28.18    | 2024-03-26 | [\#36420](https://github.com/airbytehq/airbyte/pull/36420)  | Convert s3-destinations submodule to Kotlin                                                                                                                    |
| 0.28.18    | 2024-03-26 | [\#36419](https://github.com/airbytehq/airbyte/pull/36419)  | Convert azure submodule to Kotlin                                                                                                                              |
| 0.28.18    | 2024-03-26 | [\#36413](https://github.com/airbytehq/airbyte/pull/36413)  | Convert postgres submodule to Kotlin                                                                                                                           |
| 0.28.18    | 2024-03-26 | [\#36412](https://github.com/airbytehq/airbyte/pull/36412)  | Convert mongodb submodule to Kotlin                                                                                                                            |
| 0.28.18    | 2024-03-26 | [\#36411](https://github.com/airbytehq/airbyte/pull/36411)  | Convert datastore-bigquery submodule to Kotlin                                                                                                                 |
| 0.28.18    | 2024-03-26 | [\#36205](https://github.com/airbytehq/airbyte/pull/36205)  | Convert core/main to Kotlin                                                                                                                                    |
| 0.28.18    | 2024-03-26 | [\#36204](https://github.com/airbytehq/airbyte/pull/36204)  | Convert core/test to Kotlin                                                                                                                                    |
| 0.28.18    | 2024-03-26 | [\#36190](https://github.com/airbytehq/airbyte/pull/36190)  | Convert core/testFixtures to Kotlin                                                                                                                            |
| 0.28.0     | 2024-03-26 | [\#36514](https://github.com/airbytehq/airbyte/pull/36514)  | Bump CDK version to 0.28.0                                                                                                                                     |
| 0.27.7     | 2024-03-26 | [\#36466](https://github.com/airbytehq/airbyte/pull/36466)  | Destinations: fix support for case-sensitive fields in destination state.                                                                                      |
| 0.27.6     | 2024-03-26 | [\#36432](https://github.com/airbytehq/airbyte/pull/36432)  | Sources support for AirbyteRecordMessageMeta during reading source data types.                                                                                 |
| 0.27.5     | 2024-03-25 | [\#36461](https://github.com/airbytehq/airbyte/pull/36461)  | Destinations: Handle case-sensitive columns in destination state handling.                                                                                     |
| 0.27.4     | 2024-03-25 | [\#36333](https://github.com/airbytehq/airbyte/pull/36333)  | Sunset DebeziumSourceDecoratingIterator.                                                                                                                       |
| 0.27.1     | 2024-03-22 | [\#36296](https://github.com/airbytehq/airbyte/pull/36296)  | Destinations: (async framework) Do not log invalid message data.                                                                                               |
| 0.27.0     | 2024-03-21 | [\#36364](https://github.com/airbytehq/airbyte/pull/36364)  | Sources: Increase debezium initial record wait time to 40 minute.                                                                                              |
| 0.26.1     | 2024-03-19 | [\#35599](https://github.com/airbytehq/airbyte/pull/35599)  | Sunset SourceDecoratingIterator.                                                                                                                               |
| 0.26.0     | 2024-03-19 | [\#36263](https://github.com/airbytehq/airbyte/pull/36263)  | Improve conversion of debezium Date type for some edge case in mssql.                                                                                          |
| 0.25.0     | 2024-03-18 | [\#36203](https://github.com/airbytehq/airbyte/pull/36203)  | Wiring of Transformer to StagingConsumerFactory and JdbcBufferedConsumerFactory; import changes for Kotlin conversion; State message logs to debug             |
| 0.24.1     | 2024-03-13 | [\#36022](https://github.com/airbytehq/airbyte/pull/36022)  | Move log4j2-test.xml to test fixtures, away from runtime classpath.                                                                                            |
| 0.24.0     | 2024-03-13 | [\#35944](https://github.com/airbytehq/airbyte/pull/35944)  | Add `_airbyte_meta` in raw table and test fixture updates                                                                                                      |
| 0.23.20    | 2024-03-12 | [\#36011](https://github.com/airbytehq/airbyte/pull/36011)  | Debezium configuration for conversion of null value on a column with default value.                                                                            |
| 0.23.19    | 2024-03-11 | [\#35904](https://github.com/airbytehq/airbyte/pull/35904)  | Add retries to the debezium engine.                                                                                                                            |
| 0.23.18    | 2024-03-07 | [\#35899](https://github.com/airbytehq/airbyte/pull/35899)  | Null check when retrieving destination state                                                                                                                   |
| 0.23.16    | 2024-03-06 | [\#35842](https://github.com/airbytehq/airbyte/pull/35842)  | Improve logging in debezium processing.                                                                                                                        |
| 0.23.15    | 2024-03-05 | [\#35827](https://github.com/airbytehq/airbyte/pull/35827)  | improving the Junit interceptor.                                                                                                                               |
| 0.23.14    | 2024-03-05 | [\#35739](https://github.com/airbytehq/airbyte/pull/35739)  | Add logging to the CDC queue size. Fix the ContainerFactory.                                                                                                   |
| 0.23.13    | 2024-03-04 | [\#35774](https://github.com/airbytehq/airbyte/pull/35774)  | minor changes to the CDK test fixtures.                                                                                                                        |
| 0.23.12    | 2024-03-01 | [\#35767](https://github.com/airbytehq/airbyte/pull/35767)  | introducing a timeout for java tests.                                                                                                                          |
| 0.23.11    | 2024-03-01 | [\#35313](https://github.com/airbytehq/airbyte/pull/35313)  | Preserve timezone offset in CSV writer for destinations                                                                                                        |
| 0.23.10    | 2024-03-01 | [\#35303](https://github.com/airbytehq/airbyte/pull/35303)  | Migration framework with DestinationState for softReset                                                                                                        |
| 0.23.9     | 2024-02-29 | [\#35720](https://github.com/airbytehq/airbyte/pull/35720)  | various improvements for tests TestDataHolder                                                                                                                  |
| 0.23.8     | 2024-02-28 | [\#35529](https://github.com/airbytehq/airbyte/pull/35529)  | Refactor on state iterators                                                                                                                                    |
| 0.23.7     | 2024-02-28 | [\#35376](https://github.com/airbytehq/airbyte/pull/35376)  | Extract typereduper migrations to separte method                                                                                                               |
| 0.23.6     | 2024-02-26 | [\#35647](https://github.com/airbytehq/airbyte/pull/35647)  | Add a getNamespace into TestDataHolder                                                                                                                         |
| 0.23.5     | 2024-02-26 | [\#35512](https://github.com/airbytehq/airbyte/pull/35512)  | Remove @DisplayName from all CDK tests.                                                                                                                        |
| 0.23.4     | 2024-02-26 | [\#35507](https://github.com/airbytehq/airbyte/pull/35507)  | Add more logs into TestDatabase.                                                                                                                               |
| 0.23.3     | 2024-02-26 | [\#35495](https://github.com/airbytehq/airbyte/pull/35495)  | Fix Junit Interceptor to print better stacktraces                                                                                                              |
| 0.23.2     | 2024-02-22 | [\#35385](https://github.com/airbytehq/airbyte/pull/35342)  | Bugfix: inverted logic of disableTypeDedupe flag                                                                                                               |
| 0.23.1     | 2024-02-22 | [\#35527](https://github.com/airbytehq/airbyte/pull/35527)  | reduce shutdow timeouts                                                                                                                                        |
| 0.23.0     | 2024-02-22 | [\#35342](https://github.com/airbytehq/airbyte/pull/35342)  | Consolidate and perform upfront gathering of DB metadata state                                                                                                 |
| 0.21.4     | 2024-02-21 | [\#35511](https://github.com/airbytehq/airbyte/pull/35511)  | Reduce CDC state compression limit to 1MB                                                                                                                      |
| 0.21.3     | 2024-02-20 | [\#35394](https://github.com/airbytehq/airbyte/pull/35394)  | Add Junit progress information to the test logs                                                                                                                |
| 0.21.2     | 2024-02-20 | [\#34978](https://github.com/airbytehq/airbyte/pull/34978)  | Reduce log noise in NormalizationLogParser.                                                                                                                    |
| 0.21.1     | 2024-02-20 | [\#35199](https://github.com/airbytehq/airbyte/pull/35199)  | Add thread names to the logs.                                                                                                                                  |
| 0.21.0     | 2024-02-16 | [\#35314](https://github.com/airbytehq/airbyte/pull/35314)  | Delete S3StreamCopier classes. These have been superseded by the async destinations framework.                                                                 |
| 0.20.9     | 2024-02-15 | [\#35240](https://github.com/airbytehq/airbyte/pull/35240)  | Make state emission to platform inside state manager itself.                                                                                                   |
| 0.20.8     | 2024-02-15 | [\#35285](https://github.com/airbytehq/airbyte/pull/35285)  | Improve blobstore module structure.                                                                                                                            |
| 0.20.7     | 2024-02-13 | [\#35236](https://github.com/airbytehq/airbyte/pull/35236)  | output logs to files in addition to stdout when running tests                                                                                                  |
| 0.20.6     | 2024-02-12 | [\#35036](https://github.com/airbytehq/airbyte/pull/35036)  | Add trace utility to emit analytics messages.                                                                                                                  |
| 0.20.5     | 2024-02-13 | [\#34869](https://github.com/airbytehq/airbyte/pull/34869)  | Don't emit final state in SourceStateIterator there is an underlying stream failure.                                                                           |
| 0.20.4     | 2024-02-12 | [\#35042](https://github.com/airbytehq/airbyte/pull/35042)  | Use delegate's isDestinationV2 invocation in SshWrappedDestination.                                                                                            |
| 0.20.3     | 2024-02-09 | [\#34580](https://github.com/airbytehq/airbyte/pull/34580)  | Support special chars in mysql/mssql database name.                                                                                                            |
| 0.20.2     | 2024-02-12 | [\#35111](https://github.com/airbytehq/airbyte/pull/35144)  | Make state emission from async framework synchronized.                                                                                                         |
| 0.20.1     | 2024-02-11 | [\#35111](https://github.com/airbytehq/airbyte/pull/35111)  | Fix GlobalAsyncStateManager stats counting logic.                                                                                                              |
| 0.20.0     | 2024-02-09 | [\#34562](https://github.com/airbytehq/airbyte/pull/34562)  | Add new test cases to BaseTypingDedupingTest to exercise special characters.                                                                                   |
| 0.19.0     | 2024-02-01 | [\#34745](https://github.com/airbytehq/airbyte/pull/34745)  | Reorganize CDK module structure.                                                                                                                               |
| 0.18.0     | 2024-02-08 | [\#33606](https://github.com/airbytehq/airbyte/pull/33606)  | Add updated Initial and Incremental Stream State definitions for DB Sources.                                                                                   |
| 0.17.1     | 2024-02-08 | [\#35027](https://github.com/airbytehq/airbyte/pull/35027)  | Make state handling thread safe in async destination framework.                                                                                                |
| 0.17.0     | 2024-02-08 | [\#34502](https://github.com/airbytehq/airbyte/pull/34502)  | Enable configuring async destination batch size.                                                                                                               |
| 0.16.6     | 2024-02-07 | [\#34892](https://github.com/airbytehq/airbyte/pull/34892)  | Improved testcontainers logging and support for unshared containers.                                                                                           |
| 0.16.5     | 2024-02-07 | [\#34948](https://github.com/airbytehq/airbyte/pull/34948)  | Fix source state stats counting logic                                                                                                                          |
| 0.16.4     | 2024-02-01 | [\#34727](https://github.com/airbytehq/airbyte/pull/34727)  | Add future based stdout consumer in BaseTypingDedupingTest                                                                                                     |
| 0.16.3     | 2024-01-30 | [\#34669](https://github.com/airbytehq/airbyte/pull/34669)  | Fix org.apache.logging.log4j:log4j-slf4j-impl version conflicts.                                                                                               |
| 0.16.2     | 2024-01-29 | [\#34630](https://github.com/airbytehq/airbyte/pull/34630)  | expose NamingTransformer to sub-classes in destinations JdbcSqlGenerator.                                                                                      |
| 0.16.1     | 2024-01-29 | [\#34533](https://github.com/airbytehq/airbyte/pull/34533)  | Add a safe method to execute DatabaseMetadata's Resultset returning queries.                                                                                   |
| 0.16.0     | 2024-01-26 | [\#34573](https://github.com/airbytehq/airbyte/pull/34573)  | Untangle Debezium harness dependencies.                                                                                                                        |
| 0.15.2     | 2024-01-25 | [\#34441](https://github.com/airbytehq/airbyte/pull/34441)  | Improve airbyte-api build performance.                                                                                                                         |
| 0.15.1     | 2024-01-25 | [\#34451](https://github.com/airbytehq/airbyte/pull/34451)  | Async destinations: Better logging when we fail to parse an AirbyteMessage                                                                                     |
| 0.15.0     | 2024-01-23 | [\#34441](https://github.com/airbytehq/airbyte/pull/34441)  | Removed connector registry and micronaut dependencies.                                                                                                         |
| 0.14.2     | 2024-01-24 | [\#34458](https://github.com/airbytehq/airbyte/pull/34458)  | Handle case-sensitivity in sentry error grouping                                                                                                               |
| 0.14.1     | 2024-01-24 | [\#34468](https://github.com/airbytehq/airbyte/pull/34468)  | Add wait for process to be done before ending sync in destination BaseTDTest                                                                                   |
| 0.14.0     | 2024-01-23 | [\#34461](https://github.com/airbytehq/airbyte/pull/34461)  | Revert non backward compatible signature changes from 0.13.1                                                                                                   |
| 0.13.3     | 2024-01-23 | [\#34077](https://github.com/airbytehq/airbyte/pull/34077)  | Denote if destinations fully support Destinations V2                                                                                                           |
| 0.13.2     | 2024-01-18 | [\#34364](https://github.com/airbytehq/airbyte/pull/34364)  | Better logging in mongo db source connector                                                                                                                    |
| 0.13.1     | 2024-01-18 | [\#34236](https://github.com/airbytehq/airbyte/pull/34236)  | Add postCreateTable hook in destination JdbcSqlGenerator                                                                                                       |
| 0.13.0     | 2024-01-16 | [\#34177](https://github.com/airbytehq/airbyte/pull/34177)  | Add `useExpensiveSafeCasting` param in JdbcSqlGenerator methods; add JdbcTypingDedupingTest fixture; other DV2-related changes                                 |
| 0.12.1     | 2024-01-11 | [\#34186](https://github.com/airbytehq/airbyte/pull/34186)  | Add hook for additional destination specific checks to JDBC destination check method                                                                           |
| 0.12.0     | 2024-01-10 | [\#33875](https://github.com/airbytehq/airbyte/pull/33875)  | Upgrade sshd-mina to 2.11.1                                                                                                                                    |
| 0.11.5     | 2024-01-10 | [\#34119](https://github.com/airbytehq/airbyte/pull/34119)  | Remove wal2json support for postgres+debezium.                                                                                                                 |
| 0.11.4     | 2024-01-09 | [\#33305](https://github.com/airbytehq/airbyte/pull/33305)  | Source stats in incremental syncs                                                                                                                              |
| 0.11.3     | 2023-01-09 | [\#33658](https://github.com/airbytehq/airbyte/pull/33658)  | Always fail when debezium fails, even if it happened during the setup phase.                                                                                   |
| 0.11.2     | 2024-01-09 | [\#33969](https://github.com/airbytehq/airbyte/pull/33969)  | Destination state stats implementation                                                                                                                         |
| 0.11.1     | 2024-01-04 | [\#33727](https://github.com/airbytehq/airbyte/pull/33727)  | SSH bastion heartbeats for Destinations                                                                                                                        |
| 0.11.0     | 2024-01-04 | [\#33730](https://github.com/airbytehq/airbyte/pull/33730)  | DV2 T+D uses Sql struct to represent transactions; other T+D-related changes                                                                                   |
| 0.10.4     | 2023-12-20 | [\#33071](https://github.com/airbytehq/airbyte/pull/33071)  | Add the ability to parse JDBC parameters with another delimiter than '&'                                                                                       |
| 0.10.3     | 2024-01-03 | [\#33312](https://github.com/airbytehq/airbyte/pull/33312)  | Send out count in AirbyteStateMessage                                                                                                                          |
| 0.10.1     | 2023-12-21 | [\#33723](https://github.com/airbytehq/airbyte/pull/33723)  | Make memory-manager log message less scary                                                                                                                     |
| 0.10.0     | 2023-12-20 | [\#33704](https://github.com/airbytehq/airbyte/pull/33704)  | JdbcDestinationHandler now properly implements `getInitialRawTableState`; reenable SqlGenerator test                                                           |
| 0.9.0      | 2023-12-18 | [\#33124](https://github.com/airbytehq/airbyte/pull/33124)  | Make Schema Creation Separate from Table Creation, exclude the T&D module from the CDK                                                                         |
| 0.8.0      | 2023-12-18 | [\#33506](https://github.com/airbytehq/airbyte/pull/33506)  | Improve async destination shutdown logic; more JDBC async migration work; improve DAT test schema handling                                                     |
| 0.7.9      | 2023-12-18 | [\#33549](https://github.com/airbytehq/airbyte/pull/33549)  | Improve MongoDB logging.                                                                                                                                       |
| 0.7.8      | 2023-12-18 | [\#33365](https://github.com/airbytehq/airbyte/pull/33365)  | Emit stream statuses more consistently                                                                                                                         |
| 0.7.7      | 2023-12-18 | [\#33434](https://github.com/airbytehq/airbyte/pull/33307)  | Remove LEGACY state                                                                                                                                            |
| 0.7.6      | 2023-12-14 | [\#32328](https://github.com/airbytehq/airbyte/pull/33307)  | Add schema less mode for mongodb CDC. Fixes for non standard mongodb id type.                                                                                  |
| 0.7.4      | 2023-12-13 | [\#33232](https://github.com/airbytehq/airbyte/pull/33232)  | Track stream record count during sync; only run T+D if a stream had nonzero records or the previous sync left unprocessed records.                             |
| 0.7.3      | 2023-12-13 | [\#33369](https://github.com/airbytehq/airbyte/pull/33369)  | Extract shared JDBC T+D code.                                                                                                                                  |
| 0.7.2      | 2023-12-11 | [\#33307](https://github.com/airbytehq/airbyte/pull/33307)  | Fix DV2 JDBC type mappings (code changes in [\#33307](https://github.com/airbytehq/airbyte/pull/33307)).                                                       |
| 0.7.1      | 2023-12-01 | [\#33027](https://github.com/airbytehq/airbyte/pull/33027)  | Add the abstract DB source debugger.                                                                                                                           |
| 0.7.0      | 2023-12-07 | [\#32326](https://github.com/airbytehq/airbyte/pull/32326)  | Destinations V2 changes for JDBC destinations                                                                                                                  |
| 0.6.4      | 2023-12-06 | [\#33082](https://github.com/airbytehq/airbyte/pull/33082)  | Improvements to schema snapshot error handling + schema snapshot history scope (scoped to configured DB).                                                      |
| 0.6.2      | 2023-11-30 | [\#32573](https://github.com/airbytehq/airbyte/pull/32573)  | Update MSSQLConverter to enforce 6-digit microsecond precision for timestamp fields                                                                            |
| 0.6.1      | 2023-11-30 | [\#32610](https://github.com/airbytehq/airbyte/pull/32610)  | Support DB initial sync using binary as primary key.                                                                                                           |
| 0.6.0      | 2023-11-30 | [\#32888](https://github.com/airbytehq/airbyte/pull/32888)  | JDBC destinations now use the async framework                                                                                                                  |
| 0.5.3      | 2023-11-28 | [\#32686](https://github.com/airbytehq/airbyte/pull/32686)  | Better attribution of debezium engine shutdown due to heartbeat.                                                                                               |
| 0.5.1      | 2023-11-27 | [\#32662](https://github.com/airbytehq/airbyte/pull/32662)  | Debezium initialization wait time will now read from initial setup time.                                                                                       |
| 0.5.0      | 2023-11-22 | [\#32656](https://github.com/airbytehq/airbyte/pull/32656)  | Introduce TestDatabase test fixture, refactor database source test base classes.                                                                               |
| 0.4.11     | 2023-11-14 | [\#32526](https://github.com/airbytehq/airbyte/pull/32526)  | Clean up memory manager logs.                                                                                                                                  |
| 0.4.10     | 2023-11-13 | [\#32285](https://github.com/airbytehq/airbyte/pull/32285)  | Fix UUID codec ordering for MongoDB connector                                                                                                                  |
| 0.4.9      | 2023-11-13 | [\#32468](https://github.com/airbytehq/airbyte/pull/32468)  | Further error grouping improvements for DV2 connectors                                                                                                         |
| 0.4.8      | 2023-11-09 | [\#32377](https://github.com/airbytehq/airbyte/pull/32377)  | source-postgres tests: skip dropping database                                                                                                                  |
| 0.4.7      | 2023-11-08 | [\#31856](https://github.com/airbytehq/airbyte/pull/31856)  | source-postgres: support for infinity date and timestamps                                                                                                      |
| 0.4.5      | 2023-11-07 | [\#32112](https://github.com/airbytehq/airbyte/pull/32112)  | Async destinations framework: Allow configuring the queue flush threshold                                                                                      |
| 0.4.4      | 2023-11-06 | [\#32119](https://github.com/airbytehq/airbyte/pull/32119)  | Add STANDARD UUID codec to MongoDB debezium handler                                                                                                            |
| 0.4.2      | 2023-11-06 | [\#32190](https://github.com/airbytehq/airbyte/pull/32190)  | Improve error deinterpolation                                                                                                                                  |
| 0.4.1      | 2023-11-02 | [\#32192](https://github.com/airbytehq/airbyte/pull/32192)  | Add 's3-destinations' CDK module.                                                                                                                              |
| 0.4.0      | 2023-11-02 | [\#32050](https://github.com/airbytehq/airbyte/pull/32050)  | Fix compiler warnings.                                                                                                                                         |
| 0.3.0      | 2023-11-02 | [\#31983](https://github.com/airbytehq/airbyte/pull/31983)  | Add deinterpolation feature to AirbyteExceptionHandler.                                                                                                        |
| 0.2.4      | 2023-10-31 | [\#31807](https://github.com/airbytehq/airbyte/pull/31807)  | Handle case of debezium update and delete of records in mongodb.                                                                                               |
| 0.2.3      | 2023-10-31 | [\#32022](https://github.com/airbytehq/airbyte/pull/32022)  | Update Debezium version from 2.20 -> 2.4.0.                                                                                                                    |
| 0.2.2      | 2023-10-31 | [\#31976](https://github.com/airbytehq/airbyte/pull/31976)  | Debezium tweaks to make tests run faster.                                                                                                                      |
| 0.2.0      | 2023-10-30 | [\#31960](https://github.com/airbytehq/airbyte/pull/31960)  | Hoist top-level gradle subprojects into CDK.                                                                                                                   |
| 0.1.12     | 2023-10-24 | [\#31674](https://github.com/airbytehq/airbyte/pull/31674)  | Fail sync when Debezium does not shut down properly.                                                                                                           |
| 0.1.11     | 2023-10-18 | [\#31486](https://github.com/airbytehq/airbyte/pull/31486)  | Update constants in AdaptiveSourceRunner.                                                                                                                      |
| 0.1.9      | 2023-10-12 | [\#31309](https://github.com/airbytehq/airbyte/pull/31309)  | Use toPlainString() when handling BigDecimals in PostgresConverter                                                                                             |
| 0.1.8      | 2023-10-11 | [\#31322](https://github.com/airbytehq/airbyte/pull/31322)  | Cap log line length to 32KB to prevent loss of records                                                                                                         |
| 0.1.7      | 2023-10-10 | [\#31194](https://github.com/airbytehq/airbyte/pull/31194)  | Deallocate unused per stream buffer memory when empty                                                                                                          |
| 0.1.6      | 2023-10-10 | [\#31083](https://github.com/airbytehq/airbyte/pull/31083)  | Fix precision of numeric values in async destinations                                                                                                          |
| 0.1.5      | 2023-10-09 | [\#31196](https://github.com/airbytehq/airbyte/pull/31196)  | Update typo in CDK (CDN_LSN -> CDC_LSN)                                                                                                                        |
| 0.1.4      | 2023-10-06 | [\#31139](https://github.com/airbytehq/airbyte/pull/31139)  | Reduce async buffer                                                                                                                                            |
| 0.1.1      | 2023-09-28 | [\#30835](https://github.com/airbytehq/airbyte/pull/30835)  | JDBC destinations now avoid staging area name collisions by using the raw table name as the stage name. (previously we used the stream name as the stage name) |
| 0.1.0      | 2023-09-27 | [\#30445](https://github.com/airbytehq/airbyte/pull/30445)  | First launch, including shared classes for all connectors.                                                                                                     |
| 0.0.2      | 2023-08-21 | [\#28687](https://github.com/airbytehq/airbyte/pull/28687)  | Version bump only (no other changes).                                                                                                                          |
| 0.0.1      | 2023-08-08 | [\#28687](https://github.com/airbytehq/airbyte/pull/28687)  | Initial release for testing.                                                                                                                                   |
