# DataGen Source

## Documentation

This is the repository for the DataGen source connector.
For information about how to use this connector within Airbyte, see [User Documentation](https://docs.airbyte.com/integrations/sources/datagen)

## Local development

### Building via Gradle

From the Airbyte repository root, run:

```bash
./gradlew :airbyte-integrations:connectors:source-datagen:build
```

Once built, the docker image name and tag on your host will be `airbyte/source-datagen:dev`.
the Dockerfile.
