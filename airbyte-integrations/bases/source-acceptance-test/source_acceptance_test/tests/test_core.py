#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
from collections import Counter, defaultdict
from functools import reduce
from logging import Logger
from typing import Any, Dict, List, Mapping, MutableMapping, Set

import dpath.util
import pytest
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConnectorSpecification, Status, Type
from docker.errors import ContainerError
from jsonschema import validate
from source_acceptance_test.base import BaseTest
from source_acceptance_test.config import BasicReadTestConfig, ConnectionTestConfig
from source_acceptance_test.utils import ConnectorRunner, SecretDict, filter_output, serialize, verify_records_schema
from source_acceptance_test.utils.json_schema_helper import JsonSchemaHelper, get_expected_schema_structure, get_object_structure


@pytest.mark.default_timeout(10)
class TestSpec(BaseTest):

    spec_cache: ConnectorSpecification = None

    @pytest.fixture(name="actual_connector_spec")
    def actual_connector_spec_fixture(request: BaseTest, docker_runner):
        if not request.spec_cache:
            output = docker_runner.call_spec()
            spec_messages = filter_output(output, Type.SPEC)
            assert len(spec_messages) == 1, "Spec message should be emitted exactly once"
            assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT"), "AIRBYTE_ENTRYPOINT must be set in dockerfile"
            assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT") == " ".join(
                docker_runner.entry_point
            ), "env should be equal to space-joined entrypoint"
            spec = spec_messages[0].spec
            request.spec_cache = spec
        return request.spec_cache

    def test_match_expected(
        self, connector_spec: ConnectorSpecification, actual_connector_spec: ConnectorSpecification, connector_config: SecretDict
    ):

        if connector_spec:
            assert actual_connector_spec == connector_spec, "Spec should be equal to the one in spec.json file"
        # Getting rid of technical variables that start with an underscore
        config = {key: value for key, value in connector_config.data.items() if not key.startswith("_")}

        spec_message_schema = actual_connector_spec.connectionSpecification
        validate(instance=config, schema=spec_message_schema)

        js_helper = JsonSchemaHelper(spec_message_schema)
        variants = js_helper.find_variant_paths()
        js_helper.validate_variant_paths(variants)

    def test_required(self):
        """Check that connector will fail if any required field is missing"""

    def test_optional(self):
        """Check that connector can work without any optional field"""

    def test_has_secret(self):
        """Check that spec has a secret. Not sure if this should be always the case"""

    def test_secret_never_in_the_output(self):
        """This test should be injected into any docker command it needs to know current config and spec"""

    def test_oauth_flow_parameters(self, actual_connector_spec: ConnectorSpecification):
        """
        Check if connector has correct oauth flow parameters according to https://docs.airbyte.io/connector-development/connector-specification-reference
        """
        self._validate_authflow_parameters(actual_connector_spec)

    @staticmethod
    def _validate_authflow_parameters(connector_spec: ConnectorSpecification):
        if not connector_spec.authSpecification:
            return
        spec_schema = connector_spec.connectionSpecification
        oauth_spec = connector_spec.authSpecification.oauth2Specification
        parameters: List[List[str]] = oauth_spec.oauthFlowInitParameters + oauth_spec.oauthFlowOutputParameters
        root_object = oauth_spec.rootObject
        if len(root_object) == 0:
            params = {"/" + "/".join(p) for p in parameters}
            schema_path = set(get_expected_schema_structure(spec_schema))
        elif len(root_object) == 1:
            params = {"/" + "/".join([root_object[0], *p]) for p in parameters}
            schema_path = set(get_expected_schema_structure(spec_schema))
        elif len(root_object) == 2:
            params = {"/" + "/".join([f"{root_object[0]}({root_object[1]})", *p]) for p in parameters}
            schema_path = set(get_expected_schema_structure(spec_schema, annotate_one_of=True))
        else:
            assert "rootObject cannot have more than 2 elements"

        diff = params - schema_path
        assert diff == set(), f"Specified oauth fields are missed from spec schema: {diff}"


@pytest.mark.default_timeout(30)
class TestConnection(BaseTest):
    def test_check(self, connector_config, inputs: ConnectionTestConfig, docker_runner: ConnectorRunner):
        if inputs.status == ConnectionTestConfig.Status.Succeed:
            output = docker_runner.call_check(config=connector_config)
            con_messages = filter_output(output, Type.CONNECTION_STATUS)

            assert len(con_messages) == 1, "Connection status message should be emitted exactly once"
            assert con_messages[0].connectionStatus.status == Status.SUCCEEDED
        elif inputs.status == ConnectionTestConfig.Status.Failed:
            output = docker_runner.call_check(config=connector_config)
            con_messages = filter_output(output, Type.CONNECTION_STATUS)

            assert len(con_messages) == 1, "Connection status message should be emitted exactly once"
            assert con_messages[0].connectionStatus.status == Status.FAILED
        elif inputs.status == ConnectionTestConfig.Status.Exception:
            with pytest.raises(ContainerError) as err:
                docker_runner.call_check(config=connector_config)

            assert err.value.exit_status != 0, "Connector should exit with error code"
            assert "Traceback" in err.value.stderr, "Connector should print exception"


@pytest.mark.default_timeout(30)
class TestDiscovery(BaseTest):
    def test_discover(self, connector_config, docker_runner: ConnectorRunner):
        output = docker_runner.call_discover(config=connector_config)
        catalog_messages = filter_output(output, Type.CATALOG)

        assert len(catalog_messages) == 1, "Catalog message should be emitted exactly once"
        # TODO(sherifnada) return this once an input bug is fixed (test suite currently fails if this file is not provided)
        # if catalog:
        #     for stream1, stream2 in zip(catalog_messages[0].catalog.streams, catalog.streams):
        #         assert stream1.json_schema == stream2.json_schema, f"Streams: {stream1.name} vs {stream2.name}, stream schemas should match"
        #         stream1.json_schema = None
        #         stream2.json_schema = None
        #         assert stream1.dict() == stream2.dict(), f"Streams {stream1.name} and {stream2.name}, stream configs should match"

    def test_defined_cursors_exist_in_schema(self, connector_config, discovered_catalog):
        """
        Check if all of the source defined cursor fields are exists on stream's json schema.
        """
        for stream_name, stream in discovered_catalog.items():
            if stream.default_cursor_field:
                schema = stream.json_schema
                assert "properties" in schema, "Top level item should have an 'object' type for {stream_name} stream schema"
                properties = schema["properties"]
                cursor_path = "/properties/".join(stream.default_cursor_field)
                assert dpath.util.search(
                    properties, cursor_path
                ), f"Some of defined cursor fields {stream.default_cursor_field} are not specified in discover schema properties for {stream_name} stream"


def primary_keys_for_records(streams, records):
    streams_with_primary_key = [stream for stream in streams if stream.stream.source_defined_primary_key]
    for stream in streams_with_primary_key:
        stream_records = [r for r in records if r.stream == stream.stream.name]
        for stream_record in stream_records:
            pk_values = {}
            for pk_path in stream.stream.source_defined_primary_key:
                pk_value = reduce(lambda data, key: data.get(key) if isinstance(data, dict) else None, pk_path, stream_record.data)
                pk_values[tuple(pk_path)] = pk_value

            yield pk_values, stream_record


@pytest.mark.default_timeout(5 * 60)
class TestBasicRead(BaseTest):
    @staticmethod
    def _validate_records_structure(records: List[AirbyteRecordMessage], configured_catalog: ConfiguredAirbyteCatalog):
        """
        Check object structure simmilar to one expected by schema. Sometimes
        just running schema validation is not enough case schema could have
        additionalProperties parameter set to true and no required fields
        therefore any arbitrary object would pass schema validation.
        This method is here to catch those cases by extracting all the pathes
        from the object and compare it to pathes expected from jsonschema. If
        there no common pathes then raise an alert.

        :param records: List of airbyte record messages gathered from connector instances.
        :param configured_catalog: SAT testcase parameters parsed from yaml file
        """
        schemas: Dict[str, Set] = {}
        for stream in configured_catalog.streams:
            schemas[stream.stream.name] = set(get_expected_schema_structure(stream.stream.json_schema))

        for record in records:
            schema_pathes = schemas.get(record.stream)
            if not schema_pathes:
                continue
            record_fields = set(get_object_structure(record.data))
            common_fields = set.intersection(record_fields, schema_pathes)
            assert common_fields, f" Record from {record.stream} stream should have some fields mentioned by json schema, {schema_pathes}"

    @staticmethod
    def _validate_schema(records: List[AirbyteRecordMessage], configured_catalog: ConfiguredAirbyteCatalog):
        """
        Check if data type and structure in records matches the one in json_schema of the stream in catalog
        """
        TestBasicRead._validate_records_structure(records, configured_catalog)
        bar = "-" * 80
        streams_errors = verify_records_schema(records, configured_catalog)
        for stream_name, errors in streams_errors.items():
            errors = map(str, errors.values())
            str_errors = f"\n{bar}\n".join(errors)
            logging.error(f"The {stream_name} stream has the following schema errors:\n{str_errors}")

        if streams_errors:
            pytest.fail(f"Please check your json_schema in selected streams {tuple(streams_errors.keys())}.")

    def _validate_empty_streams(self, records, configured_catalog, allowed_empty_streams):
        """
        Only certain streams allowed to be empty
        """
        counter = Counter(record.stream for record in records)

        all_streams = set(stream.stream.name for stream in configured_catalog.streams)
        streams_with_records = set(counter.keys())
        streams_without_records = all_streams - streams_with_records

        streams_without_records = streams_without_records - allowed_empty_streams
        assert not streams_without_records, f"All streams should return some records, streams without records: {streams_without_records}"

    def _validate_expected_records(
        self, records: List[AirbyteMessage], expected_records: List[AirbyteMessage], flags, detailed_logger: Logger
    ):
        """
        We expect some records from stream to match expected_records, partially or fully, in exact or any order.
        """
        actual_by_stream = self.group_by_stream(records)
        expected_by_stream = self.group_by_stream(expected_records)
        for stream_name, expected in expected_by_stream.items():
            actual = actual_by_stream.get(stream_name, [])
            detailed_logger.info(f"Actual records for stream {stream_name}:")
            detailed_logger.log_json_list(actual)
            detailed_logger.info(f"Expected records for stream {stream_name}:")
            detailed_logger.log_json_list(expected)

            self.compare_records(
                stream_name=stream_name,
                actual=actual,
                expected=expected,
                extra_fields=flags.extra_fields,
                exact_order=flags.exact_order,
                extra_records=flags.extra_records,
                detailed_logger=detailed_logger,
            )

    def test_read(
        self,
        connector_config,
        configured_catalog,
        inputs: BasicReadTestConfig,
        expected_records: List[AirbyteMessage],
        docker_runner: ConnectorRunner,
        detailed_logger,
    ):
        output = docker_runner.call_read(connector_config, configured_catalog)
        records = [message.record for message in filter_output(output, Type.RECORD)]

        assert records, "At least one record should be read using provided catalog"

        if inputs.validate_schema:
            self._validate_schema(records=records, configured_catalog=configured_catalog)

        self._validate_empty_streams(records=records, configured_catalog=configured_catalog, allowed_empty_streams=inputs.empty_streams)
        for pks, record in primary_keys_for_records(streams=configured_catalog.streams, records=records):
            for pk_path, pk_value in pks.items():
                assert pk_value is not None, (
                    f"Primary key subkeys {repr(pk_path)} " f"have null values or not present in {record.stream} stream records."
                )

        if expected_records:
            self._validate_expected_records(
                records=records, expected_records=expected_records, flags=inputs.expect_records, detailed_logger=detailed_logger
            )

    @staticmethod
    def remove_extra_fields(record: Any, spec: Any) -> Any:
        """Remove keys from record that spec doesn't have, works recursively"""
        if not isinstance(spec, Mapping):
            return record

        assert isinstance(record, Mapping), "Record or part of it is not a dictionary, but expected record is."
        result = {}

        for k, v in spec.items():
            assert k in record, "Record or part of it doesn't have attribute that has expected record."
            result[k] = TestBasicRead.remove_extra_fields(record[k], v)

        return result

    @staticmethod
    def compare_records(
        stream_name: str,
        actual: List[Dict[str, Any]],
        expected: List[Dict[str, Any]],
        extra_fields: bool,
        exact_order: bool,
        extra_records: bool,
        detailed_logger: Logger,
    ):
        """Compare records using combination of restrictions"""
        if exact_order:
            for r1, r2 in zip(expected, actual):
                if r1 is None:
                    assert extra_records, f"Stream {stream_name}: There are more records than expected, but extra_records is off"
                    break
                if extra_fields:
                    r2 = TestBasicRead.remove_extra_fields(r2, r1)
                assert r1 == r2, f"Stream {stream_name}: Mismatch of record order or values"
        else:
            expected = set(map(serialize, expected))
            actual = set(map(serialize, actual))
            missing_expected = set(expected) - set(actual)

            if missing_expected:
                msg = f"Stream {stream_name}: All expected records must be produced"
                detailed_logger.info(msg)
                detailed_logger.log_json_list(missing_expected)
                pytest.fail(msg)

            if not extra_records:
                extra_actual = set(actual) - set(expected)
                if extra_actual:
                    msg = f"Stream {stream_name}: There are more records than expected, but extra_records is off"
                    detailed_logger.info(msg)
                    detailed_logger.log_json_list(extra_actual)
                    pytest.fail(msg)

    @staticmethod
    def group_by_stream(records) -> MutableMapping[str, List[MutableMapping]]:
        """Group records by a source stream"""
        result = defaultdict(list)
        for record in records:
            result[record.stream].append(record.data)

        return result
