# Airbyte Secrets Migration

This is the repository for the Secrets Migration helper pod.  It enables migrating
secrets from a DatabaseConfigPersistence to a GoogleSecretsManagerConfigPersistence 
as a one-time bulk.

## Local development

#### Building via Gradle
From the Airbyte repository root, run:
```
./gradlew :airbyte-secrets-migrationsbuild
```

#### Build
Build the connector image via Gradle:
```
./gradlew :airbyte-secrets-migration:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run

## Testing
We use `JUnit` for Java tests.

### Unit and Integration Tests
Place unit tests under `src/test/...`
Place integration tests in `src/test-integration/...` 

