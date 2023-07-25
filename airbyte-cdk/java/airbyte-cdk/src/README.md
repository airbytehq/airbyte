# Developing with the Java CDK

This page will walk through the process of developing with the Java CDK.

## Building the CDK

To build the CDK, navigate to the `airbyte-cdk` directory and run the build command using Gradle:

```console
cd airbyte-cdk/java/airbyte-cdk
./gradlew build
```

This command compiles the code, runs the tests, and creates a JAR file in the `build/libs` directory.

## Publishing the CDK to Local Maven

If you're working on the CDK and need your changes to be accessible by a connector project on the same machine, you can publish the CDK to your local Maven repository:

Navigate to the `airbyte-cdk` directory:

```console
cd airbyte-cdk/java/airbyte-cdk
```

Run the publish command:

```console
./gradlew publishToMavenLocal
```

## Referencing the CDK from Java connectors

You can reference the CDK in your connector's `build.gradle` file:

```groovy
dependencies {
    implementation 'io.airbyte:airbyte-cdk:0.0.1-SNAPSHOT'
}
```

Replace `0.0.1-SNAPSHOT` with the version you are working with. If you're actively developing the CDK and want to use the latest version locally, use the `-SNAPSHOT` suffix to reference a bumped version number. (See below for version bump instructions.)

## Bumping the declared CDK version

The following file stores the current or to-be-published version number of the CDK: `airbyte-cdk/java/airbyte-cdk/src/main/resources/version.properties`

You will need to bump this version manually if you are making changes to the CDK.

## Developing a connector alongside the SDK

You can iterate on changes in the CDK local and test them in the connector without needing to publish the CDK changes publicly.

When modifying the CDK and a connector in the same PR or branch, please use the following steps:

1. First, make your changes in the CDK.
2. Build the CDK as described above and publish to local Maven.
3. In your connector project, modify the `build.gradle` to use the local CDK version (with the `-SNAPSHOT` suffix).
4. Build your connector project. It will use the locally built version of the CDK.
5. As you make additional changes to the CDK, your can repeat the build and local republish steps to incorporate the latest changes.
