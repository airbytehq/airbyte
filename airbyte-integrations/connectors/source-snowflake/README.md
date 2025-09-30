# Snowflake Source

This is the repository for the Snowflake source connector, written in Kotlin.


### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**


#### Build
To build the connector:
```
./gradlew :airbyte-integrations:connectors:source-snowflake:build
```

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-snowflake:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-snowflake:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-snowflake:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-snowflake:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing
### Unit Tests
To run unit tests:
```
./gradlew :airbyte-integrations:connectors:source-snowflake:test
```

### Integration Tests
To run integration tests:
```
./gradlew :airbyte-integrations:connectors:source-snowflake:integrationTest
```