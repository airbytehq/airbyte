# Pokeapi
This is a connector for Pokeapi contributed directly from the Connector Builder

This is just a test
## Local Development
### Environment Setup
You will need `airbyte-ci` installed. You can find the documentation [here](airbyte-ci).

### Build
This will create a dev image (`source-pokeapi-contribution-test:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-pokeapi-contribution-test build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-pokeapi-contribution-test test
```
