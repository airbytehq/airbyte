# MeiliSearch Destination

This is the repository for the MeiliSearch destination connector, written in Java.

## Local development

### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**

#### Build & Activate Virtual Environment
First, build the module by running the following from the `airbyte` project root directory: 
```
./gradlew :airbyte-integrations:connectors:destination-meilisearch:build
```

#### Create credentials
If you are running MeiliSearch locally you may not need an api key at all. If there is an API key set for MeiliSearch, you can find instruction on how to find it in the [MeiliSearch docs](https://docs.meilisearch.com/reference/features/authentication.html#master-key).

**If you are an Airbyte core member**, the integration tests do not require any external credentials. MeiliSearch is run from a test container.

### Locally running the connector docker image
```
# in airbyte root directory
./gradlew :airbyte-integrations:connectors:destination-meilisearch:airbyteDocker
docker run --rm airbyte/destination-meilisearch:dev spec
docker run --rm -v $(pwd)/airbyte-integrations/connectors/destination-meilisearch/secrets:/secrets airbyte/destination-meilisearch:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/destination-meilisearch/secrets:/secrets airbyte/destination-meilisearch:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/destination-meilisearch/secrets:/secrets -v $(pwd)/airbyte-integrations/connectors/destination-meilisearch/sample_files:/sample_files airbyte/destination-meilisearch:dev read --config /secrets/config.json --catalog /sample_files/configured_catalog.json
```

### Integration Tests
1. From the airbyte project root, run `./gradlew :airbyte-integrations:connectors:destination-meilisearch:integrationTest` to run the standard integration test suite.
