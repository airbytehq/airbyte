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

### List Gradle Tasks

To view all available tasks:
```text
./gradlew tasks
```

To view all tasks available for a given namespace:

```text
./gradlew <namespace>:tasks
```

for example:

```text
./gradlew :airbyte-integrations:connectors:source-bigquery:tasks
```

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

#### Build CDK

```text
SUB_BUILD=CDK ./gradlew <gradle command>
```

### Build

In order to "build" the project. This task includes producing all artifacts and running unit tests \(anything called in the `:test` task\). It does _not_ include integration tests \(anything called in the `:integrationTest` task\).

For example all the following are valid.

```shell
./gradlew build # builds the entire Airbyte project including every single connector supported
SUB_BUILD=PLATFORM ./gradlew build -x test # builds Airbyte Platform without running tests
SUB_BUILD=CONNECTORS_BASE ./gradlew build # builds all Airbyte connectors and runs unit tests
```

### Debugging

To debug a Gradle task, add `--scan` to the `./gradlew` command. After the task has completed, you should see a message like:

```text
Publishing build scan...
https://gradle.com/s/6y7ritpvzkwp4
```

Clicking the link opens a browser page which contains lots of information pertinent to debugging why a build failed, or understanding what sub-tasks were run during a task.

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

* Platform Acceptance Tests: These tests are a coarse test to sanity check that each major feature in the platform. They are run with the following command: `SUB_BUILD=PLATFORM ./gradlew :airbyte-tests:acceptanceTests`. These tests expect to find a local version of Airbyte running. For testing the docker version start Airbyte locally. For an example, see the [acceptance_test script](../../tools/bin/acceptance_test.sh) that is used by the CI. For Kubernetes, see the [acceptance_test_helm script](../../tools/bin/acceptance_test_kube_helm.sh) that is used by the CI.
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

# Updating Gradle Dependencies
We use [Gradle Catalogs](https://docs.gradle.org/current/userguide/platforms.html#sub:central-declaration-of-dependencies)
to keep dependencies synced up across different Java projects. This is particularly useful for Airbyte Cloud, and can be
used by any project seeking to build off Airbyte.

Catalogs allow dependencies to be represented as dependency coordinates. A user can reference preset dependencies/versions
when declaring dependencies in a build script.

> Version Catalog Example:
> ```gradle
> dependencies {
>    implementation(libs.groovy.core)
> }
> ```
> In this context, libs is a catalog and groovy represents a dependency available in this catalog. Instead of declaring a
> specific version, we reference the version in the Catalog.

This helps reduce the chances of dependency drift and dependency hell.

Thus, please use the Catalog when:
- declaring new common dependencies.
- specifying new common dependencies.

A common dependency is a foundational Java package e.g. Apache commons, Log4j etc that is often the basis on which libraries
are built upon.

This is a relatively new addition, so devs should keep this in mind and use the top-level Catalog on a best-effort basis.

### Setup Details
This section is for engineers wanting to understand Gradle Catalog details and how Airbyte has set this up.

#### The version catalog TOML file format
Gradle offers a conventional file to declare a catalog.
It’s a conventional location to declare dependencies that are both consumed and published.

The TOML file consists of 4 major sections:
- the [versions] section is used to declare versions which can be referenced by dependencies
- the [libraries] section is used to declare the aliases to coordinates
- the [bundles] section is used to declare dependency bundles
- the [plugins] section is used to declare plugins

> TOML file Example:
> ```gradle
> [versions]
> groovy = "3.0.5"
>
> [libraries]
> groovy-core = { module = "org.codehaus.groovy:groovy", version.ref = "groovy" }
>
> [bundles]
> groovy = ["groovy-core", "groovy-json", "groovy-nio"]
>
> [plugins]
> jmh = { id = "me.champeau.jmh", version = "0.6.5" }
> ```
> NOTE: for more information please follow [this](https://docs.gradle.org/current/userguide/platforms.html#:~:text=The%20version%20catalog%20TOML%20file%20format
) link.

As described above this project contains TOML file `deps.toml` which is fully fulfilled with respect to [official](https://docs.gradle.org/current/userguide/platforms.html#sub::toml-dependencies-format) documentation.
In case when new versions should be used please update `deps.toml` accordingly.

<details>
<summary>deps.toml</summary>

[versions]
fasterxml_version = "2.13.0"
glassfish_version = "2.31"
commons_io = "2.7"
log4j = "2.17.1"
slf4j = "1.7.30"
lombok = "1.18.22"
junit-jupiter = "5.8.2"

[libraries]
fasterxml = { module = "com.fasterxml.jackson:jackson-bom", version.ref = "fasterxml_version" }
glassfish = { module = "org.glassfish.jersey:jackson-bom", version.ref = "glassfish_version" }
jackson-databind = { module = "com.fasterxml.jackson.core:jackson-databind", version.ref = "fasterxml_version" }
jackson-annotations = { module = "com.fasterxml.jackson.core:jackson-annotations", version.ref = "fasterxml_version" }
jackson-dataformat = { module = "com.fasterxml.jackson.dataformat:jackson-dataformat-yaml", version.ref = "fasterxml_version" }
jackson-datatype = { module = "com.fasterxml.jackson.datatype:jackson-datatype-jsr310", version.ref = "fasterxml_version" }
guava = { module = "com.google.guava:guava", version = "30.1.1-jre" }
commons-io = { module = "commons-io:commons-io", version.ref = "commons_io" }
apache-commons = { module = "org.apache.commons:commons-compress", version = "1.20" }
apache-commons-lang = { module = "org.apache.commons:commons-lang3", version = "3.11" }
slf4j-api = { module = "org.slf4j:slf4j-api", version = "1.7.30" }
log4j-api = { module = "org.apache.logging.log4j:log4j-api", version.ref = "log4j" }
log4j-core = { module = "org.apache.logging.log4j:log4j-core", version.ref = "log4j" }
log4j-impl = { module = "org.apache.logging.log4j:log4j-slf4j-impl", version.ref = "log4j" }
log4j-web = { module = "org.apache.logging.log4j:log4j-web", version.ref = "log4j" }
jul-to-slf4j = { module = "org.slf4j:jul-to-slf4j", version.ref = "slf4j" }
jcl-over-slf4j = { module = "org.slf4j:jcl-over-slf4j", version.ref = "slf4j" }
log4j-over-slf4j = { module = "org.slf4j:log4j-over-slf4j", version.ref = "slf4j" }
appender-log4j2 = { module = "com.therealvan:appender-log4j2", version = "3.6.0" }
aws-java-sdk-s3 = { module = "com.amazonaws:aws-java-sdk-s3", version = "1.12.6" }
google-cloud-storage = { module = "com.google.cloud:google-cloud-storage", version = "2.2.2" }
s3 = { module = "software.amazon.awssdk:s3", version = "2.16.84" }
lombok = { module = "org.projectlombok:lombok", version.ref = "lombok" }
junit-jupiter-engine = { module = "org.junit.jupiter:junit-jupiter-engine", version.ref = "junit-jupiter" }
junit-jupiter-api = { module = "org.junit.jupiter:junit-jupiter-api", version.ref = "junit-jupiter" }
junit-jupiter-params = { module = "org.junit.jupiter:junit-jupiter-params", version.ref = "junit-jupiter" }
mockito-junit-jupiter = { module = "org.mockito:mockito-junit-jupiter", version = "4.0.0" }
assertj-core = { module = "org.assertj:assertj-core", version = "3.21.0" }
junit-pioneer = { module = "org.junit-pioneer:junit-pioneer", version = "1.6.2" }
findsecbugs-plugin = { module = "com.h3xstream.findsecbugs:findsecbugs-plugin", version = "1.11.0" }

[bundles]
jackson = ["jackson-databind", "jackson-annotations", "jackson-dataformat", "jackson-datatype"]
apache = ["apache-commons", "apache-commons-lang"]
log4j = ["log4j-api", "log4j-core", "log4j-impl", "log4j-web"]
slf4j = ["jul-to-slf4j", "jcl-over-slf4j", "log4j-over-slf4j"]
junit = ["junit-jupiter-api", "junit-jupiter-params", "mockito-junit-jupiter"]

</details>

#### Declaring a version catalog
Version catalogs can be declared in the settings.gradle file.
There should be specified section `dependencyResolutionManagement` which uses `deps.toml` file as a declared catalog.
> Example:
> ```gradle
> dependencyResolutionManagement {
>     repositories {
>         maven {
>             url 'https://airbyte.mycloudrepo.io/public/repositories/airbyte-public-jars/'
>        }
>     }
>     versionCatalogs {
>         libs {
>             from(files("deps.toml"))
>         }
>     }
> }
> ```

#### Sharing Catalogs
To share this catalog for further usage by other Projects, we do the following 2 steps:
- Define `version-catalog` plugin in `build.gradle` file (ignore if this record exists)
  ```gradle
  plugins {
      id '...'
      id 'version-catalog'
  ```
- Prepare Catalog for Publishing
  ```gradle
  catalog {
      versionCatalog {
          from(files("deps.toml")) < --- declere either dependencies or specify existing TOML file
      }
  }
  ```

#### Configure the Plugin Publishing Plugin
To **Publishing**, first define the `maven-publish` plugin in `build.gradle` file (ignore if this already exists):
```gradle
plugins {
    id '...'
    id 'maven-publish'
}
```
After that, describe the publishing section. Please use [this](https://docs.gradle.org/current/userguide/publishing_gradle_plugins.html) official documentation for more details.
> Example:
> ```gradle
> publishing {
>     publications {
>         maven(MavenPublication) {
>             groupId = 'io.airbyte'
>             artifactId = 'oss-catalog'
>
>                 from components.versionCatalog
>         }
>     }
>
>     repositories {
>         maven {
>             url 'https://airbyte.mycloudrepo.io/repositories/airbyte-public-jars'
>             credentials {
>                 name 'cloudrepo'
>                 username System.getenv('CLOUDREPO_USER')
>                 password System.getenv('CLOUDREPO_PASSWORD')
>             }
>         }
>
>         mavenLocal()
>     }
> }
> ```
