# Databricks Source

This is the repository for the Databricks source connector, written in Kotlin.


### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**


#### Build
To build the connector:
```
./gradlew :airbyte-integrations:connectors:source-databricks:build
```

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-databricks:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-databricks:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-databricks:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-databricks:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing
### Unit Tests
To run unit tests:
```
./gradlew :airbyte-integrations:connectors:source-databricks:test
```

### Integration Tests
To run integration tests:
```
./gradlew :airbyte-integrations:connectors:source-databricks:integrationTest
```