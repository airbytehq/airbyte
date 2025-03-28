# HubSpot Meeting Links API Source
This directory contains the manifest-only connector for `source-hubspot-meeting-links` (generated using the Airbyte Connector Builder).  

This connector reads data from the HubSpot API and defines below streams that are not supported by the official connector:
- [Meeting Links](https://developers.hubspot.com/docs/reference/api/library/meetings#get-%2Fscheduler%2Fv3%2Fmeetings%2Fmeeting-links): retrieves information about meetings created through a scheduling page


## Local development from Airbyte fork
### Prerequisites
Have `airbyte-ci` installed.
An available HubSpot API (Bearer) Token.

### Build
This will create a dev image (`source-hubspot-meeting-links:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-hubspot-meeting-links build
```
NB: possibly with complementary `--architecture=linux/amd64` flag if MacOS with M1 chip.

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-hubspot-meeting-links test
```

## Local usage
Some useful commands to test the connector locally:
1. Build the connector as described above from the Airbyte fork
2. Copy the `integration_tests/sample_config.json` file to a `secrets/prod_config.json` file
3. Fill the required credentials in the `secrets/prod_config.json` file (available in GCP Secret)
4. Run below commands to test the connector and ensure it reads data correctly
```bash
# `cd` to the source-hubspot-meeting-links connector repository
docker run --rm -i airbyte/source-hubspot-meeting-links:dev spec
docker run --rm -v $(pwd):/data -i airbyte/source-hubspot-meeting-links:dev check --config /data/secrets/prod_config.json
docker run --rm -v $(pwd):/data -i airbyte/source-hubspot-meeting-links:dev discover --config /data/secrets/prod_config.json
docker run --rm -v $(pwd):/data -i airbyte/source-hubspot-meeting-links:dev read --config /data/secrets/prod_config.json --catalog /data/integration_tests/configured_catalog.json > secrets/output.json
cat secrets/output.json
```
