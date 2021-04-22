# Source Acceptance Test Suite

Tests configurable via `acceptance-test-config.yml`. Each test has a number of inputs, 
you can provide multiple sets of inputs which will cause the same to run multiple times - one for each set of inputs.

Example of `acceptance-test-config.yml`:
```yaml
connector_image: string  # Docker image to test, for example 'airbyte/source-hubspot:0.1.0'
base_path: string  # Base path for all relative paths, optional, default - ./
tests:  # Tests configuration 
  spec: # list of the test inputs
  connection: # list of the test inputs
    - config_path: string  # set #1 of inputs
      status: string
    - config_path: string  # set #2 of inputs
      status: string
  # discovery:  # skip this test
  incremental: []  # skip this test as well
```
Ideally the connector should pass all acceptance tests. If test or its inputs omitted this test will be skipped. 
 
## Test Spec
Verify that a spec operation issued to the connector returns a valid spec.
| Input |  Type| Default | Note |
|--|--|--|--|
| `spec_path` | string | `secrets/spec.json` |Path to a JSON object representing the spec expected to be output by this connector |

## Test Connection
Verify that a check operation issued to the connector with the input config file returns a success response.
| Input |  Type| Default | Note |
|--|--|--|--|
| `config_path` | string | `secrets/config.json` |Path to a JSON object representing a valid connector configuration|
| `status` | `succeed` `failed` `exception`| |Indicate if connection check should succeed with provided config|

## Test Discovery

Verifies when a discover operation is run on the connector using the given config file, a valid catalog is output by the connector.
| Input |  Type| Default | Note |
|--|--|--|--|
| `config_path` | string | `secrets/config.json` |Path to a JSON object representing a valid connector configuration|
| `configured_catalog_path` | string| `integration_tests/configured_catalog.json` |Path to configured catalog|

## Test Basic Read

Configuring all streams in the input catalog to full refresh mode, verifies that a read operation produces some RECORD messages.
| Input |  Type| Default | Note |
|--|--|--|--|
| `config_path` | string | `secrets/config.json` |Path to a JSON object representing a valid connector configuration|
| `configured_catalog_path` | string| `integration_tests/configured_catalog.json` |Path to configured catalog|
| `validate_output_from_all_streams` | boolean | False | Verify that **all** streams have records|

## Test Full Refresh sync
### TestSequentialReads

This test performs two read operations on all streams which support full refresh syncs. It then verifies that the RECORD messages output from both were identical or the former is a strict subset of the latter.
| Input |  Type| Default | Note |
|--|--|--|--|
| `config_path` | string | `secrets/config.json` |Path to a JSON object representing a valid connector configuration|
| `configured_catalog_path` | string | `integration_tests/configured_catalog.json` |Path to configured catalog|

## Test Incremental sync
### TestTwoSequentialReads
This test verifies that all streams in the input catalog which support incremental sync can do so correctly. It does this by running two read operations: the first takes the configured catalog and config provided to this test as input. It then verifies that the sync produced a non-zero number of `RECORD` and `STATE` messages. The second read takes the same catalog and config used in the first test, plus the last `STATE` message output by the first read operation as the input state file. It verifies that either no records are produced \(since we read all records in the first sync\) or all records that produced have cursor value greather or equal to cursor value from `STATE` message. This test is performed only for streams which support incremental. Streams which do not support incremental sync are ignored. If no streams in the input catalog support incremental sync, this test is skipped.
| Input |  Type| Default | Note |
|--|--|--|--|
| `config_path` | string | `secrets/config.json` |Path to a JSON object representing a valid connector configuration|
| `configured_catalog_path` | string | `integration_tests/configured_catalog.json` |Path to configured catalog|
| `cursor_paths` | dict | {} | For each stream, the path of its cursor field in the output state messages. If omitted the test will be skipped|

### TestStateWithAbnormallyLargeValues

This tests verifies that sync produces no records when run with the STATE with abnormally large values
| Input |  Type| Default | Note |
|--|--|--|--|
| `config_path` | string | `secrets/config.json` |Path to a JSON object representing a valid connector configuration|
| `configured_catalog_path` | string | `integration_tests/configured_catalog.json` |Path to configured catalog|
| `state_path` | string | None |Path to the state file with abnormaly large cursor values|
