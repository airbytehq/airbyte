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
    - [Developing a connector against a pinned CDK version](#developing-a-connector-against-a-pinned-cdk-version)
  - [Common Debugging Tips](#common-debugging-tips)
  - [Changelog](#changelog)
    - [Java CDK](#java-cdk)

## Intro to the Java CDK

### What is included in the Java CDK?

The java CDK is comprised of separate modules:

- `core` - Shared classes for building connectors of all types.
- `db-sources-feature` - Shared classes for building DB sources.
- `db-destinations-feature` - Shared classes for building DB destinations.

Each CDK submodule contains these elements:

- `src/main` code and resources - The part of the module that will ship with the connector, providing base capabilities.
- `src/test` - These are unit tests that run as part of every build of the CDK. They help ensure that CDK `main` code is in a healthy state.
- `src/test-integration` - Integration tests which provide a more extensive test of the code in `src/main`. These are not by the `build` command but are executed as part of the `integrationTest` or `integrationTestJava` Gradle tasks.
- `src/testFixtures` - These shared classes are exported for connectors for use in the connectors' own test implementations. Connectors will have access to these classes within their unit and integration tests, but the classes will not be shipped with connectors when they are published.

### How is the CDK published?

The CDK is published as a set of jar files sharing a version number. Every submodule generates one runtime jar for the main classes. If the submodule contains test fixtures, a second jar will be published with the test fixtures classes.

Note: Connectors do not have to manage which jars they should depend on, as this is handled automatically by the `airbyte-java-connector` plugin. See example below.

## Using the Java CDK

### Building the CDK

To build and test the Java CDK, execute the following:

```sh
./gradlew :airbyte-cdk:java:airbyte-cdk:build
```

### Bumping the CDK version

You will need to bump this version manually whenever you are making changes to code inside the CDK.

While under development, the next version number for the CDK is tracked in the file: `airbyte-cdk/java/airbyte-cdk/core/src/main/resources/version.properties`.

If the CDK is not being modified, this file will contain the most recently published version number.

<!-- TODO: Remove or update this section. Snapshots are no longer required or preferred.

## Publishing the CDK to Local Maven

If your connector pins to a work-in-progress `-SNAPSHOT` version of the CDK (e.g. `0.0.1-SNAPSHOT` or `0.2.0-SNAPSHOT`), Gradle can notice this and automatically run the task to build and publish it to your MavenLocal repository before running the connector's own build and test tasks. -->

### Publishing the CDK

_⚠️ These steps should only be performed after all testing and approvals are in place on the PR. ⚠️_

The CDK can be published with a GitHub Workflow and a slash command which can be run by Airbyte personnel.

To invoke via slash command (recommended), use the following syntax in a comment on the PR that contains your changes:

```bash
/publish-java-cdk                # Run with the defaults (dry-run=false, force=false)
/publish-java-cdk dry-run=true   # Run in dry-run mode (no-op)
/publish-java-cdk force=true     # Force-publish if needing to replace an already published version
```

Note:

- Remember to **document your changes** in the Changelog section below.
- After you publish the CDK, remember to toggle `useLocalCdk` back to `false` in all connectors.
- Unless you specify `force=true`, the pipeline should fail if the version you are trying to publish already exists.
- By running the publish with `dry-run=true`, you can confirm the process is working as expected, without actually publishing the changes.
- In dry-run mode, you can also view and download the jars that are generated. To do so, navigate to the job status in GitHub Actions and navigate to the 'artifacts' section.
- You can also invoke manually in the GitHub Web UI. To do so: go to `Actions` tab, select the `Publish Java CDK` workflow, and click `Run workflow`.
- You can view and administer published CDK versions here: https://admin.cloudrepo.io/repository/airbyte-public-jars/io/airbyte/airbyte-cdk
- The public endpoint for published CDK versions is here: https://airbyte.mycloudrepo.io/public/repositories/airbyte-public-jars/io/airbyte/airbyte-cdk/

## Developing Connectors with the Java CDK

### Referencing the CDK from Java connectors

You can reference the CDK in your connector's `build.gradle` file:

```groovy
plugins {
    id 'application'
    id 'airbyte-docker'
    id 'airbyte-java-connector'
}

airbyteJavaConnector {
    cdkVersionRequired = '0.1.0'   // The CDK version to pin to.
    features = ['db-destinations'] // An array of CDK features to depend on.
    useLocalCdk = true             // Use 'true' to use a live reference to the 
                                   // local cdk project.
}

airbyteJavaConnector.addCdkDependencies()
```

Replace `0.1.0` with the CDK version you are working with. If you're actively developing the CDK and want to use the latest version locally, use the `useLocalCdk` flag to use the live CDK code during builds and tests.

### Developing a connector alongside the CDK

You can iterate on changes in the CDK local and test them in the connector without needing to publish the CDK changes publicly.

When modifying the CDK and a connector in the same PR or branch, please use the following steps:

1. Set the version of the CDK in `version.properties` to the next appropriate version number, along with a `-SNAPSHOT` suffix, as explained above.
1. In your connector project, modify the `build.gradle` to use the _new_ local CDK version with the `-SNAPSHOT` suffix, as explained above.
1. Build and test your connector as usual. Gradle will automatically build the snapshot version of the CDK, and it will use this version when building and testing your connector.
1. As you make additional changes to the CDK, Gradle will automatically rebuild and republish the CDK locally in order to incorporate the latest changes.

### Developing a connector against a pinned CDK version

You can always pin your connector to a prior stable version of the CDK, which may not match what is the latest version in the `airbyte` repo. For instance, your connector can be pinned to `0.1.1` while the latest version may be `0.2.0`.

Maven and Gradle will automatically reference the correct (pinned) version of the CDK for your connector, and you can use your local IDE to browse the prior version of the codebase that corresponds to that version.

## Common Debugging Tips

MavenLocal debugging steps:

1. Confirm local publish status by running:
   `ls -la ~/.m2/repository/io/airbyte/airbyte-cdk/*`
2. Confirm jar contents by running:
   `jar tf ~/.m2/repository/io/airbyte/airbyte-cdk/0.0.2-SNAPSHOT/airbyte-cdk-0.0.2-SNAPSHOT.jar`
3. Remove CDK artifacts from MavenLocal by running:
   `rm -rf ~/.m2/repository/io/airbyte/airbyte-cdk/*`
4. Rebuid CDK artifacts by running:
   `./gradlew :airbyte-cdk:java:airbyte-cdk:build`
   or
   `./gradlew :airbyte-cdk:java:airbyte-cdk:publishToMavenLocal`

## Changelog

### Java CDK

| Version | Date       | Pull Request                                               | Subject                               |
| :------ | :--------- | :--------------------------------------------------------- | :------------------------------------ |
| 0.1.0   | 2023-08-21 | [\#30445](https://github.com/airbytehq/airbyte/pull/30445) | First launch, including share code for all connectors. |
| 0.0.2   | 2023-08-21 | [\#28687](https://github.com/airbytehq/airbyte/pull/28687) | Version bump only (no other changes). |
| 0.0.1   | 2023-08-08 | [\#28687](https://github.com/airbytehq/airbyte/pull/28687) | Initial release for testing.          |
