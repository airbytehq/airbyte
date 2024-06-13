# Changelog

## 3.8.0

Add `TestDiscovery.test_primary_keys_data_type`, which validates that primary keys are not of type `array` or `object` in discovered catalog.
Add `validate_primary_keys_data_type` to `TestBasicRead.test_read`, which validates that primary keys are not of type `array` or `object` in records
and ensures that at least one primary key is non-null when there is a composite primary key.

## 3.7.0

Add `validate_state_messages` to TestBasicRead.test_read:: Validate that all states contain neither legacy state emissions nor missing source stats in the state message.

## 3.6.0

Relaxing CATs validation when a stream has a primary key defined.

## 3.5.0

Add `validate_stream_statuses` to TestBasicRead.test_read:: Validate all statuses for all streams in the catalogs were emitted in correct order.

## 3.4.0

Add TestConnectorDocumentation suite for validating connectors documentation structure and content.

## 3.3.3

Аix `NoAdditionalPropertiesValidator` if no type found in `items`

## 3.3.2

Fix TestBasicRead.test_read.validate_schema: set `additionalProperties` to False recursively for objects.

## 3.3.1

Fix TestSpec.test_oauth_is_default_method to skip connectors that doesn't have predicate_key object.

## 3.3.0

Add `test_certified_connector_has_allowed_hosts` and `test_certified_connector_has_suggested_streams` tests to the `connector_attribute` test suite

## 3.2.0

Add `TestBasicRead.test_all_supported_file_types_present`, which validates that all supported file types are present in the sandbox account for certified file-based connectors.

## 3.1.0

Add TestSpec.test_oauth_is_default_method test with OAuth is default option validation.

## 3.0.1

Upgrade to Dagger 0.9.6

## 3.0.0

Upgrade to Dagger 0.9.5

## 2.2.0

Add connector_attribute test suite and stream primary key validation

## 2.1.4

Add check to ensure stream schemas are valid json schemas

## 2.1.3

Remove dockerfile and migrations tools. We are now running CAT with `airbyte-ci` and new migration operation will be done by the `airbyte-ci` tool.

## 2.1.2

Add check for duplicate stream names

## 2.1.1

Centralize timeout duration declaration and increase timeout for discover.

## 2.1.0

Make the container under test a sessions scoped fixture.
Support loading it from its Dagger container id for better performance.
Install pytest-xdist to support running tests in parallel.

## 2.0.2

Make `test_two_sequential_reads` handle namespace property in stream descriptor.

## 2.0.1

Changing `format` or `airbyte_type` in a field definition of a schema or specification is now a breaking change.

## 2.0.0

Update test_incremental.test_two_sequential_reads to be unaware of the contents of the state message. This is to support connectors that have a custom implementation of a cursor.

## 1.0.4

Fix edge case in skip_backward_compatibility_tests_fixture on discovery: if the current config structure is not compatible with the previous connector version, the discovery command failing and the previous connector version catalog could not be retrieved.

## 1.0.3

Add tests for display_type property

## 1.0.2

Fix bug in skip_backward_compatibility_tests_fixture, the previous connector version could not be retrieved.

## 1.0.1

Pin airbyte-protocol-model to <1.0.0.

## 1.0.0

Bump to Python 3.10, use dagger instead of docker-py in the ConnectorRunner.

## 0.11.5

Changing test output and adding diff to test_read

## 0.11.4

Relax checking of `oneOf` common property and allow optional `default` keyword additional to `const` keyword.

## 0.11.3

Refactor test_oauth_flow_parameters to validate advanced_auth instead of the deprecated authSpecification

## 0.11.2

Do not enforce spec.json/spec.yaml

## 0.11.1

Test connector image labels and make sure they are set correctly and match metadata.yaml.

## 0.11.0

Add backward_compatibility.check_if_field_removed test to check if a field has been removed from the catalog.

## 0.10.8

Increase the connection timeout to Docker client to 2 minutes ([context](https://github.com/airbytehq/airbyte/issues/27401))

## 0.10.7

Fix on supporting arrays in the state (ensure string are parsed as string and not int)

## 0.10.6

Supporting arrays in the state by allowing ints in cursor_paths

## 0.10.5

Skipping test_catalog_has_supported_data_types as it is failing on too many connectors. Will first address globally the type/format problems at scale and then re-enable it.

## 0.10.4

Fixing bug: test_catalog_has_supported_data_types should support stream properties having `/` in it.

## 0.10.3

Fixing bug: test_catalog_has_supported_data_types , integer is a supported airbyte type.

## 0.10.2

Fixing bug: test_catalog_has_supported_data_types was failing when a connector stream property is named 'type'.

## 0.10.1

Reverting to 0.9.0 as the latest version. 0.10.0 was released with a bug failing CAT on a couple of connectors.

## 0.10.0

Discovery test: add validation that fails if the declared types/format/airbyte_types in the connector's streams properties are not [supported data types](https://docs.airbyte.com/understanding-airbyte/supported-data-types/) or if their combination is invalid.

## 0.9.0

Basic read test: add validation that fails if undeclared columns are present in records. Add `fail_on_extra_fields` input parameter to ignore this failure if desired.

## 0.8.0

Spec tests: Make sure grouping and ordering properties are used in a consistent way.

## 0.7.2

TestConnection: assert that a check with `exception` status emits a trace message.

## 0.7.1

Discovery backward compatibility tests: handle errors on previous connectors catalog retrieval. Return None when the discovery failed. It should unblock the situation when tests fails even if you bypassed backward compatibility tests.

## 0.7.0

Basic read test: add `ignored_fields`, change configuration format by adding optional `bypass_reason` [#22996](https://github.com/airbytehq/airbyte/pull/22996)

## 0.6.1

Fix docker API - "Error" is optional. [#22987](https://github.com/airbytehq/airbyte/pull/22987)

## 0.6.0

Allow passing custom environment variables to the connector under test. [#22937](https://github.com/airbytehq/airbyte/pull/22937).

## 0.5.3

Spec tests: Make `oneOf` checks work for nested `oneOf`s. [#22395](https://github.com/airbytehq/airbyte/pull/22395)

## 0.5.2

Check that `emitted_at` increases during subsequent reads. [#22291](https://github.com/airbytehq/airbyte/pull/22291)

## 0.5.1

Fix discovered catalog caching for different configs. [#22301](https://github.com/airbytehq/airbyte/pull/22301)

## 0.5.0

Re-release of 0.3.0 [#21451](https://github.com/airbytehq/airbyte/pull/21451)

# Renamed image from `airbyte/source-acceptance-test` to `airbyte/connector-acceptance-test` - Older versions are only available under the old name

## 0.4.0

Revert 0.3.0

## 0.3.0

(Broken) Add various stricter checks for specs (see PR for details). [#21451](https://github.com/airbytehq/airbyte/pull/21451)

## 0.2.26

Check `future_state` only for incremental streams. [#21248](https://github.com/airbytehq/airbyte/pull/21248)

## 0.2.25

Enable bypass reason for future state test config.[#20549](https://github.com/airbytehq/airbyte/pull/20549)

## 0.2.24

Check for nullity of docker runner in `previous_discovered_catalog_fixture`.[#20899](https://github.com/airbytehq/airbyte/pull/20899)

## 0.2.23

Skip backward compatibility tests on specifications if actual and previous specifications and discovered catalogs are identical.[#20435](https://github.com/airbytehq/airbyte/pull/20435)

## 0.2.22

Capture control messages to store and use updated configurations. [#19979](https://github.com/airbytehq/airbyte/pull/19979).

## 0.2.21

Optionally disable discovered catalog caching. [#19806](https://github.com/airbytehq/airbyte/pull/19806).

## 0.2.20

Stricter integer field schema validation. [#19820](https://github.com/airbytehq/airbyte/pull/19820).

## 0.2.19

Test for exposed secrets: const values can not hold secrets. [#19465](https://github.com/airbytehq/airbyte/pull/19465).

## 0.2.18

Test connector specification against exposed secret fields. [#19124](https://github.com/airbytehq/airbyte/pull/19124).

## 0.2.17

Make `incremental.future_state` mandatory in `high` `test_strictness_level`. [#19085](https://github.com/airbytehq/airbyte/pull/19085/).

## 0.2.16

Run `basic_read` on the discovered catalog in `high` `test_strictness_level`. [#18937](https://github.com/airbytehq/airbyte/pull/18937).

## 0.2.15

Make `expect_records` mandatory in `high` `test_strictness_level`. [#18497](https://github.com/airbytehq/airbyte/pull/18497/).

## 0.2.14

Fail basic read in `high` `test_strictness_level` if no `bypass_reason` is set on empty_streams. [#18425](https://github.com/airbytehq/airbyte/pull/18425/).

## 0.2.13

Fail tests in `high` `test_strictness_level` if all tests are not configured. [#18414](https://github.com/airbytehq/airbyte/pull/18414/).

## 0.2.12

Declare `bypass_reason` field in test configuration. [#18364](https://github.com/airbytehq/airbyte/pull/18364).

## 0.2.11

Declare `test_strictness_level` field in test configuration. [#18218](https://github.com/airbytehq/airbyte/pull/18218).

## 0.2.10

Bump `airbyte-cdk~=0.2.0`

## 0.2.9

Update tests after protocol change making `supported_sync_modes` a required property of `AirbyteStream` [#15591](https://github.com/airbytehq/airbyte/pull/15591/)

## 0.2.8

Make full refresh tests tolerant to new records in a sequential read.[#17660](https://github.com/airbytehq/airbyte/pull/17660/)

## 0.2.7

Fix a bug when a state is evaluated once before used in a loop of `test_read_sequential_slices` [#17757](https://github.com/airbytehq/airbyte/pull/17757/)

## 0.2.6

Backward compatibility hypothesis testing: disable "filtering too much" health check. [#17871](https://github.com/airbytehq/airbyte/pull/17871)

## 0.2.5

Unit test `test_state_with_abnormally_large_values` to check state emission testing is working. [#17791](https://github.com/airbytehq/airbyte/pull/17791)

## 0.2.4

Make incremental tests compatible with per stream states.[#16686](https://github.com/airbytehq/airbyte/pull/16686/)

## 0.2.3

Backward compatibility tests: improve `check_if_type_of_type_field_changed` to make it less radical when validating specs and allow `'str' -> ['str', '<another_type>']` type changes.[#16429](https://github.com/airbytehq/airbyte/pull/16429/)

## 0.2.2

Backward compatibility tests: improve `check_if_cursor_field_was_changed` to make it less radical and allow stream addition to catalog.[#15835](https://github.com/airbytehq/airbyte/pull/15835/)

## 0.2.1

Don't fail on updating `additionalProperties`: fix IndexError [#15532](https://github.com/airbytehq/airbyte/pull/15532/)

## 0.2.0

Finish backward compatibility syntactic tests implementation: check that cursor fields were not changed. [#15520](https://github.com/airbytehq/airbyte/pull/15520/)

## 0.1.62

Backward compatibility tests: add syntactic validation of catalogs [#15486](https://github.com/airbytehq/airbyte/pull/15486/)

## 0.1.61

Add unit tests coverage computation [#15443](https://github.com/airbytehq/airbyte/pull/15443/).

## 0.1.60

Backward compatibility tests: validate fake previous config against current connector specification. [#15367](https://github.com/airbytehq/airbyte/pull/15367)

## 0.1.59

Backward compatibility tests: add syntactic validation of specs [#15194](https://github.com/airbytehq/airbyte/pull/15194/).

## 0.1.58

Bootstrap spec backward compatibility tests. Add fixtures to retrieve a previous connector version spec [#14954](https://github.com/airbytehq/airbyte/pull/14954/).

## 0.1.57

Run connector from its image `working_dir` instead of from `/data`.

## 0.1.56

Add test case in `TestDiscovery` and `TestConnection` to assert `additionalProperties` fields are set to true if they are declared [#14878](https://github.com/airbytehq/airbyte/pull/14878/).

## 0.1.55

Add test case in `TestDiscovery` to assert `supported_sync_modes` stream field in catalog is set and not empty.

## 0.1.54

Fixed `AirbyteTraceMessage` test case to make connectors fail more reliably.

## 0.1.53

Add more granular incremental testing that walks through syncs and verifies records according to cursor value.

## 0.1.52

Add test case for `AirbyteTraceMessage` emission on connector failure: [#12796](https://github.com/airbytehq/airbyte/pull/12796/).

## 0.1.51

- Add `threshold_days` option for lookback window support in incremental tests.
- Update CDK to prevent warnings when encountering new `AirbyteTraceMessage`s.

## 0.1.50

Added support for passing a `.yaml` file as `spec_path`.

## 0.1.49

Fixed schema parsing when a JSONschema `type` was not present - we now assume `object` if the `type` is not present.

## 0.1.48

Add checking that oneOf common property has only `const` keyword, no `default` and `enum` keywords: [#11704](https://github.com/airbytehq/airbyte/pull/11704)

## 0.1.47

Added local test success message containing git hash: [#11497](https://github.com/airbytehq/airbyte/pull/11497)

## 0.1.46

Fix `test_oneof_usage` test: [#9861](https://github.com/airbytehq/airbyte/pull/9861)

## 0.1.45

Check for not allowed keywords `allOf`, `not` in connectors schema: [#9851](https://github.com/airbytehq/airbyte/pull/9851)

## 0.1.44

Fix incorrect name of `primary_keys` attribute: [#9768](https://github.com/airbytehq/airbyte/pull/9768)

## 0.1.43

`TestFullRefresh` test can compare records using PKs: [#9768](https://github.com/airbytehq/airbyte/pull/9768)

## 0.1.36

Add assert that `spec.json` file does not have any `$ref` in it: [#8842](https://github.com/airbytehq/airbyte/pull/8842)

## 0.1.32

Add info about skipped failed tests in `/test` command message on GitHub: [#8691](https://github.com/airbytehq/airbyte/pull/8691)

## 0.1.31

Take `ConfiguredAirbyteCatalog` from discover command by default

## 0.1.30

Validate if each field in a stream has appeared at least once in some record.

## 0.1.29

Add assert that output catalog does not have any `$ref` in it

## 0.1.28

Print stream name when incremental sync tests fail

## 0.1.27

Add ignored fields for full refresh test (unit tests)

## 0.1.26

Add ignored fields for full refresh test

## 0.1.25

Fix incorrect nested structures compare.

## 0.1.24

Improve message about errors in the stream's schema: [#6934](https://github.com/airbytehq/airbyte/pull/6934)

## 0.1.23

Fix incorrect auth init flow check defect.

## 0.1.22

Fix checking schemas with root `$ref` keyword

## 0.1.21

Fix rootObject oauth init parameter check

## 0.1.20

Add oauth init flow parameter verification for spec.

## 0.1.19

Assert a non-empty overlap between the fields present in the record and the declared json schema.

## 0.1.18

Fix checking date-time format against nullable field.

## 0.1.17

Fix serialize function for acceptance-tests: [#5738](https://github.com/airbytehq/airbyte/pull/5738)

## 0.1.16

Fix for flake8-ckeck for acceptance-tests: [#5785](https://github.com/airbytehq/airbyte/pull/5785)

## 0.1.15

Add detailed logging for acceptance tests: [5392](https://github.com/airbytehq/airbyte/pull/5392)

## 0.1.14

Fix for NULL datetime in MySQL format (i.e. `0000-00-00`): [#4465](https://github.com/airbytehq/airbyte/pull/4465)

## 0.1.13

Replace `validate_output_from_all_streams` with `empty_streams` param: [#4897](https://github.com/airbytehq/airbyte/pull/4897)

## 0.1.12

Improve error message when data mismatches schema: [#4753](https://github.com/airbytehq/airbyte/pull/4753)

## 0.1.11

Fix error in the naming of method `test_match_expected` for class `TestSpec`.

## 0.1.10

Add validation of input config.json against spec.json.

## 0.1.9

Add configurable validation of schema for all records in BasicRead test: [#4345](https://github.com/airbytehq/airbyte/pull/4345)

The validation is ON by default.
To disable validation for the source you need to set `validate_schema: off` in the config file.

## 0.1.8

Fix cursor_path to support nested and absolute paths: [#4552](https://github.com/airbytehq/airbyte/pull/4552)

## 0.1.7

Add: `test_spec` additionally checks if Dockerfile has `ENV AIRBYTE_ENTRYPOINT` defined and equal to space_joined `ENTRYPOINT`

## 0.1.6

Add test whether PKs present and not None if `source_defined_primary_key` defined: [#4140](https://github.com/airbytehq/airbyte/pull/4140)

## 0.1.5

Add configurable timeout for the acceptance tests: [#4296](https://github.com/airbytehq/airbyte/pull/4296)
