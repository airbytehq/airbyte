# Gradle Cheatsheet


## Connector Development

### Commands used in CI
All connectors, regardless of implementation language, implement the following interface to allow uniformity in the build system when run from CI: 

**Build connector, run unit tests, and build Docker image**: `./gradlew :airbyte-integrations:connectors:<name>:build`
**Run integration tests**: `./gradlew :airbyte-integrations:connectors:<name>:integrationTest`

### Python
The ideal end state for a Python connector developer is that they shouldn't have to know Gradle exists. 

We're almost there, but today there is only one Gradle command that's needed when developing in Python, used for formatting code.

**Formatting python module**: `./gradlew :airbyte-integrations:connectors:<name>:airbytePythonFormat`
