# Airbyte Secrets Migration

This is the repository for the Secrets Migration helper pod.  It enables migrating
secrets from a DatabaseConfigPersistence to a GoogleSecretsManagerConfigPersistence 
as a one-time bulk.

## Local development

#### Building via Gradle
From the Airbyte repository root, run:
```
SUB_BUILD=PLATFORM ./gradlew :airbyte-secrets-migration:build -x test
```

#### Build
Build the image via Gradle:
```
SUB_BUILD=PLATFORM ./gradlew :airbyte-secrets-migration:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

### Publish
Publish the image to Docker hub:
```
docker login
docker tag airbyte/secrets-migration:dev airbyte/secrets-migration:dev-27
docker push airbyte/secrets-migration:dev-27
```

#### Run

## Testing
We use `JUnit` for Java tests.

### Unit and Integration Tests
Place unit tests under `src/test/...`
Place integration tests in `src/test-integration/...` 

