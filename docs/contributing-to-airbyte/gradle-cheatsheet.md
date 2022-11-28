# Gradle Cheatsheet

## Overview

We have 3 ways of slicing our builds:

1. **Build Everything**: Including every single connectors.
2. **Build Platform**: Build only modules related to the core platform.
3. **Build Connectors Base**: Build only modules related to code infrastructure for connectors.

**Build Everything** is really not particularly functional as building every single connector at once is really prone to transient errors. As there are more connectors the chance that there is a transient issue while downloading any single dependency starts to get really high.

In our CI we run **Build Platform** and **Build Connectors Base**. Then separately, on a regular cadence, we build each connector and run its integration tests.

We split Build Platform and Build Connectors Base from each other for a few reasons:

1. The tech stacks are very different. The Platform is almost entirely Java. Because of differing needs around separating environments, the Platform build can be optimized separately from the Connectors one.
2. We want to the iteration cycles of people working on connectors or the platform faster _and_ independent. e.g. Before this change someone working on a Platform feature needs to run formatting on the entire codebase \(including connectors\). This led to a lot of cosmetic build failures that obfuscated actually problems. Ideally a failure on the connectors side should not block progress on the platform side.
3. The lifecycles are different. One can safely release the Platform even if parts of Connectors Base is failing \(and vice versa\).

Future Work: The next step here is to figure out how to more formally split connectors and platform. Right now we exploit behavior in [settings.gradle](../../settings.gradle) to separate them. This is not a best practice. Ultimately, we want these two builds to be totally separate. We do not know what that will look like yet.

## Cheatsheet

Here is a cheatsheet for common gradle commands.

### Basic Build Syntax

Here is the syntax for running gradle commands on the different parts of the code base that we called out above.

#### Build Everything

```text
./gradlew <gradle command>
```

#### Build Platform

```text
SUB_BUILD=PLATFORM ./gradlew <gradle command>
```

#### Build Connectors Base

```text
SUB_BUILD=CONNECTORS_BASE ./gradlew <gradle command>
```

### Build

In order to "build" the project. This task includes producing all artifacts and running unit tests \(anything called in the `:test` task\). It does _not_ include integration tests \(anything called in the `:integrationTest` task\).

For example all the following are valid.

```shell
./gradlew build # builds the entire Airbyte project including every single connector supported
SUB_BUILD=PLATFORM ./gradlew build -x test # builds Airbyte Platform without running tests
SUB_BUILD=CONNECTORS_BASE ./gradlew build # builds all Airbyte connectors and runs unit tests
```

### Formatting

The build system has a custom task called `format`. It is not called as part of `build`. If the command is called on a subset of the project, it will \(mostly\) target just the included modules. The exception is that `spotless` \(a gradle formatter\) will always format any file types that it is configured to manage regardless of which sub build is run. `spotless` is relatively fast, so this should not be too much of an annoyance. It can lead to formatting changes in unexpected parts of the code base.

For example all the following are valid.

```shell
./gradlew format
SUB_BUILD=PLATFORM ./gradlew format
SUB_BUILD=CONNECTORS_BASE ./gradlew format
```

### Platform-Specific Commands

#### Build Artifacts

This command just builds the docker images that are used as artifacts in the platform. It bypasses running tests.

```shell
SUB_BUILD=PLATFORM ./gradlew build
```

#### Running Tests

The Platform has 3 different levels of tests: Unit Tests, Acceptance Tests, Frontend Acceptance Tests.

| Test        | Used | Description                                                                                   |
|:------------|:----:|:----------------------------------------------------------------------------------------------|
| Unit        |  X   | Aims to test each component (e.g. a method function)                                          |
| Integration |      | Checks the data flow from one module to other modules                                         |
| System      |      | Tests overall interaction of components, includes load, performance, reliability and security |
| Acceptance  |  X   | Assess whether the Product is working for the user's viewpoint                                |

**Unit Tests**

Unit Tests can be run using the `:test` task on any submodule. These test class-level behavior. They should avoid using external resources \(e.g. calling staging services or pulling resources from the internet\). We do allow these tests to spin up local resources \(usually in docker containers\). For example, we use test containers frequently to spin up test postgres databases.

**Acceptance Tests**

We split Acceptance Tests into 2 different test suites:

* Platform Acceptance Tests: These tests are a coarse test to sanity check that each major feature in the platform. They are run with the following command: `SUB_BUILD=PLATFORM ./gradlew :airbyte-tests:acceptanceTests`. These tests expect to find a local version of Airbyte running. For testing the docker version start Airbyte locally. For an example, see the [acceptance_test script](../../tools/bin/acceptance_test.sh) that is used by the CI. For Kubernetes, see the [accetance_test_kube script](../../tools/bin/acceptance_test_kube.sh) that is used by the CI.
* Migration Acceptance Tests: These tests make sure the end-to-end process of migrating from one version of Airbyte to the next works. These tests are run with the following command: `SUB_BUILD=PLATFORM ./gradlew :airbyte-tests:automaticMigrationAcceptanceTest --scan`. These tests do not expect there to be a separate deployment of Airbyte running.

These tests currently all live in [airbyte-tests](https://github.com/airbytehq/airbyte/airbyte-tests)

**Frontend Acceptance Tests**

These are acceptance tests for the frontend. They are run with
```shell
SUB_BUILD=PLATFORM ./gradlew --no-daemon :airbyte-webapp-e2e-tests:e2etest
``` 

Like the Platform Acceptance Tests, they expect Airbyte to be running locally. See the [script](https://github.com/airbytehq/airbyte/blob/master/tools/bin/e2e_test.sh) that is used by the CI.

These tests currently all live in [airbyte-webapp-e2e-tests](https://github.com/airbytehq/airbyte/airbyte-webapp-e2e-tests)

**Future Work**

Our story around "integration testing" or "E2E testing" is a little ambiguous. Our Platform Acceptance Test Suite is getting somewhat unwieldy. It was meant to just be some coarse sanity checks, but over time we have found more need to test interactions between systems more granular. Whether we start supporting a separate class of tests \(e.g. integration tests\) or figure out how allow for more granular tests in the existing Acceptance Test framework is TBD.

### Connectors-Specific Commands \(Connector Development\)

#### Commands used in CI

All connectors, regardless of implementation language, implement the following interface to allow uniformity in the build system when run from CI:

**Build connector, run unit tests, and build Docker image**:
```shell
./gradlew :airbyte-integrations:connectors:<connector_name>:build
``` 

**Run integration tests**:
```shell
./gradlew :airbyte-integrations:connectors:<connector_name>:integrationTest
```

#### Python

The ideal end state for a Python connector developer is that they shouldn't have to know Gradle exists.

We're almost there, but today there is only one Gradle command that's needed when developing in Python, used for formatting code.

**Formatting python module**:
```shell
./gradlew :airbyte-integrations:connectors:<connector_name>:airbytePythonFormat
```

