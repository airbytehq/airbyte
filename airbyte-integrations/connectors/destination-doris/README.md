# Destination Doris

This is the Airbyte destination connector for [Apache Doris](https://doris.apache.org/).

## Local development

### Prerequisites

- JDK 21
- Docker (for integration tests)

### Build

```bash
./gradlew :airbyte-integrations:connectors:destination-doris:build
```

### Unit tests

```bash
./gradlew :airbyte-integrations:connectors:destination-doris:test
```

### Integration tests

Integration tests use a Doris all-in-one Docker container (`apache/doris:doris-all-in-one-2.1.0`).

```bash
./gradlew :airbyte-integrations:connectors:destination-doris:integrationTestNonDocker
```

**Note:** The Doris container binds to fixed ports (8030, 9030, 8040, 9060). Ensure these ports are available before running tests.
