#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import logging
from collections import Counter, defaultdict
from functools import reduce
from logging import Logger
from typing import Any, Dict, List, Mapping, MutableMapping

import dpath.util
import pytest
from airbyte_cdk.models import AirbyteMessage, ConnectorSpecification, Status, Type
from docker.errors import ContainerError
from jsonschema import validate
from source_acceptance_test.base import BaseTest
from source_acceptance_test.config import BasicReadTestConfig, ConnectionTestConfig
from source_acceptance_test.utils import ConnectorRunner, SecretDict, filter_output, serialize, verify_records_schema
from source_acceptance_test.utils.json_schema_helper import JsonSchemaHelper


@pytest.mark.default_timeout(10)
class TestSpec(BaseTest):
    def test_match_expected(self, connector_spec: ConnectorSpecification, connector_config: SecretDict, docker_runner: ConnectorRunner):
        output = docker_runner.call_spec()
        spec_messages = filter_output(output, Type.SPEC)

        assert len(spec_messages) == 1, "Spec message should be emitted exactly once"
        if connector_spec:
            assert spec_messages[0].spec == connector_spec, "Spec should be equal to the one in spec.json file"

        assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT"), "AIRBYTE_ENTRYPOINT must be set in dockerfile"
        assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT") == " ".join(
            docker_runner.entry_point
        ), "env should be equal to space-joined entrypoint"

        # Getting rid of technical variables that start with an underscore
        config = {key: value for key, value in connector_config.data.items() if not key.startswith("_")}

        spec_message_schema = spec_messages[0].spec.connectionSpecification
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
            assert "Traceback" in err.value.stderr.decode("utf-8"), "Connector should print exception"


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
    def _validate_schema(records, configured_catalog):
        """
        Check if data type and structure in records matches the one in json_schema of the stream in catalog
        """
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
        records = filter_output(output, Type.RECORD)

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
