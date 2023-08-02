# Developing with the Java CDK

This page will walk through the process of developing with the Java CDK.

## Building the CDK

To build and test the Java CDK, execute the following:

```sh
./gradlew :airbyte-cdk:java:airbyte-cdk:build
```

## Bumping the declared CDK version

You will need to bump this version manually whenever you are making changes to code inside the CDK.

While under development, the next version number for the CDK is tracked in the file: `airbyte-cdk/java/airbyte-cdk/src/main/resources/version.properties`.

If the CDK is not being modified, this file will contain the most recently published version number.

## Publishing the CDK to Local Maven

If your connector pins to a work-in-progress `-SNAPSHOT` version of the CDK (e.g. `0.0.1-SNAPSHOT` or `0.2.0-SNAPSHOT`), Gradle will notice this and automatically run the task to build and publish it to your MavenLocal repository before running the connector's own build and test tasks.

## Referencing the CDK from Java connectors

You can reference the CDK in your connector's `build.gradle` file:

```groovy
dependencies {
    implementation 'io.airbyte:airbyte-cdk:0.0.1-SNAPSHOT'
}
```

Replace `0.0.1-SNAPSHOT` with the version you are working with. If you're actively developing the CDK and want to use the latest version locally, use the `-SNAPSHOT` suffix to reference a bumped version number. (See below for version bump instructions.)

## Developing a connector alongside the SDK

You can iterate on changes in the CDK local and test them in the connector without needing to publish the CDK changes publicly.

When modifying the CDK and a connector in the same PR or branch, please use the following steps:

1. Set the version of the SDK in `version.properties` to the next appropriate version number, along with a `-SNAPSHOT` suffix, as explained above.
1. In your connector project, modify the `build.gradle` to use the _new_ local CDK version with the `-SNAPSHOT` suffix, as explained above.
1. Build and test your connector as usual. Gradle will automatically build the snapshot version of the CDK, and it will use this version when building and testing your connector.
1. As you make additional changes to the CDK, Gradle will automatically rebuild and republish the CDK locally in order to incorporate the latest changes.

## Developing a connector against a pinned CDK version

You can always pin your connector to a prior stable version of the CDK, which may not match what is the latest version in the `airbyte` repo. For instance, your connector can be pinned to `0.1.1` while the latest version may be `0.2.0`.

Maven and Gradle will automatically reference the correct (pinned) version of the CDK for your connector, and you can use your local IDE to browse the prior version of the codebase that corresponds to that version.

<!--
TODO: More detailed instructions needed.

Add screenshots and additional details for IntelliJ IDEA and/or VS Code.
-->
