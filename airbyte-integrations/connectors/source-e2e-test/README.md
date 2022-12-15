# End-to-End Testing Source

This is the repository for the mock source connector in Java. For information about how to use this connector within Airbyte, see [the User Documentation](https://docs.airbyte.io/integrations/sources/e2e-test)

## Mock Json record generation
The [airbytehq/jsongenerator](https://github.com/airbytehq/jsongenerator) is used to generate random Json records based on the specified Json schema. This library is forked from [jimblackler/jsongenerator](https://github.com/jimblackler/jsongenerator) authored by [Jim Blackler](https://github.com/jimblackler) and licensed under Apache 2.0.

Although this library seems to be the best one available for Json generation in Java, it has two downsides.
  - It relies on JavaScript inside Java (through `org.mozilla:rhino-engine`), and fetches remote JavaScript snippets (in the [PatternReverser](https://github.com/jimblackler/jsongenerator/blob/master/src/main/java/net/jimblackler/jsongenerator/PatternReverser.java)).
  - It does not allow customization of individual field. The generated Json object can be seemingly garbled. We may use libraries such as [java-faker](https://github.com/DiUS/java-faker) in the future to argument it.

## Local development

#### Building via Gradle
From the Airbyte repository root, run:
```
./gradlew :airbyte-integrations:connectors:source-e2e-test:build
```

#### Create credentials
No credential is needed for this connector. 

### Locally running the connector docker image

#### Build
Build the connector image via Gradle:
```
./gradlew :airbyte-integrations:connectors:source-e2e-test:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-e2e-test:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-e2e-test:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-e2e-test:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-e2e-test:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

#### Cloud variant
The cloud version of this connector only allows the `CONTINUOUS FEED` mode. When this mode is changed, please make sure that the cloud variant is updated and published accordingly as well.

## Testing
We use `JUnit` for Java tests.

### Unit and Integration Tests
Place unit tests under `src/test/io/airbyte/integrations/sources/e2e-test`.

#### Acceptance Tests
Airbyte has a standard test suite that all destination connectors must pass. See example(s) in
`src/test-integration/java/io/airbyte/integrations/sources/e2e-test/`.

### Using gradle to run tests
All commands should be run from airbyte project root.
To run unit tests:
```
./gradlew :airbyte-integrations:connectors:sources-e2e-test:unitTest
```
To run acceptance and custom integration tests:
```
./gradlew :airbyte-integrations:connectors:sources-e2e-test:integrationTest
```

## Dependency Management

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing unit and integration tests.
2. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use [SemVer](https://semver.org/)).
3. Create a Pull Request.
4. Pat yourself on the back for being an awesome contributor.
5. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
