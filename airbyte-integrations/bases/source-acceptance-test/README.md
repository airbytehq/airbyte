# Source Acceptance Tests
This package uses pytest to discover, configure and execute the tests.
It implemented as a pytest plugin.

It adds new configuration option `--acceptance-test-config` - path to configuration file (by default is current folder). 
Configuration stored in YaML format and validated by pydantic.

Example configuration can be found in `sample_files/` folder:
```yaml
connector_image: <your_image>
tests:
  spec:
    - spec_path: "<connector_folder>/spec.json"
  connection:
    - config_path: "secrets/config.json"
      status: "succeed"
    - config_path: "sample_files/invalid_config.json"
      status: "exception"
  discovery:
    - config_path: "secrets/config.json"
  basic_read:
    - config_path: "secrets/config.json"
      configured_catalog_path: "sample_files/configured_catalog.json"
      empty_streams: []
  incremental:
    - config_path: "secrets/config.json"
      configured_catalog_path: "sample_files/configured_catalog.json"
      future_state_path: "sample_files/abnormal_state.json"
      cursor_paths:
        subscription_changes: ["timestamp"]
        email_events: ["timestamp"]
  full_refresh:
    - config_path: "secrets/config.json"
      configured_catalog_path: "sample_files/configured_catalog.json"
```
Required steps to test connector are the following:
* Build docker image for connector
* Create `acceptance-test-config.yml` file with test settings, Note: all paths in this files are relative to its location
* Use one of the following ways to run tests:

## Running
Using python
```bash
cd ../../base/source-acceptance-test
python -m pytest source_acceptance_test/tests --acceptance-test-config=<path_to_your_connector> -vvv
```
_Note: this will assume that docker image for connector is already built_

Using Gradle
```bash
./gradlew :airbyte-integrations:connectors:source-<name>:sourceAcceptanceTest
```
_Note: this way will also build docker image for the connector_

Using Bash
```bash
./source-acceptance-test.sh -vv
```
_Note: you can append any arguments to this command, they will be forwarded to pytest


## Developing Locally

To run the tests within this dir:
* Ensure you have `venv` set up with `python3 -m venv .venv` & source it `source ./.venv/bin/activate`
* Run tests with `python -m pytest -s unit_tests`