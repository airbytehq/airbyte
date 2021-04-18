# Standard tests
This package uses pytest to discover, configure and execute the tests.
It implemented as a pytest plugin.

It adds new configuration option `--standard_test_config` - path to configuration file (by default is current folder). 
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
      validate_output_from_all_streams: true
  incremental:
    - config_path: "secrets/config.json"
      configured_catalog_path: "sample_files/configured_catalog.json"
      state_path: "sample_files/abnormal_state.json"
      cursor_paths:
        subscription_changes: ["timestamp"]
        email_events: ["timestamp"]
  full_refresh:
    - config_path: "secrets/config.json"
      configured_catalog_path: "sample_files/configured_catalog.json"
```
# Running
```bash
python -m pytest standard_test/tests --standard_test_config=<path_to_your_connector> -vvv
```
_Note: this will assume that docker image for connector is already built_

Using Gradle
```bash
./gradlew :airbyte-integrations:connectors:source-<name>:standardTest
```
_Note: this will also build docker image for connector_
