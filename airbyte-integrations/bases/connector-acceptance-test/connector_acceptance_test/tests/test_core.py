#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import functools
import json
import logging
import re
from collections import Counter, defaultdict
from functools import reduce
from logging import Logger
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Set, Tuple
from xmlrpc.client import Boolean

import dpath.util
import jsonschema
import pytest
from airbyte_cdk.models import (
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    Status,
    SyncMode,
    TraceType,
    Type,
)
from connector_acceptance_test.base import BaseTest
from connector_acceptance_test.config import (
    BasicReadTestConfig,
    Config,
    ConnectionTestConfig,
    DiscoveryTestConfig,
    EmptyStreamConfiguration,
    ExpectedRecordsConfig,
    IgnoredFieldsConfiguration,
    SpecTestConfig,
)
from connector_acceptance_test.utils import ConnectorRunner, SecretDict, delete_fields, filter_output, make_hashable, verify_records_schema
from connector_acceptance_test.utils.backward_compatibility import CatalogDiffChecker, SpecDiffChecker, validate_previous_configs
from connector_acceptance_test.utils.common import (
    build_configured_catalog_from_custom_catalog,
    build_configured_catalog_from_discovered_catalog_and_empty_streams,
    find_all_values_for_key_in_schema,
    find_keyword_schema,
)
from connector_acceptance_test.utils.json_schema_helper import JsonSchemaHelper, get_expected_schema_structure, get_object_structure
from jsonschema._utils import flatten


@pytest.fixture(name="connector_spec_dict")
def connector_spec_dict_fixture(actual_connector_spec):
    return json.loads(actual_connector_spec.json())


@pytest.fixture(name="secret_property_names")
def secret_property_names_fixture():
    return (
        "client_token",
        "access_token",
        "api_token",
        "token",
        "secret",
        "client_secret",
        "password",
        "key",
        "service_account_info",
        "service_account",
        "tenant_id",
        "certificate",
        "jwt",
        "credentials",
        "app_id",
        "appid",
        "refresh_token",
    )


DATE_PATTERN = "^[0-9]{2}-[0-9]{2}-[0-9]{4}$"
DATETIME_PATTERN = "^[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}:[0-9]{2})?$"


@pytest.mark.default_timeout(10)
class TestSpec(BaseTest):

    spec_cache: ConnectorSpecification = None
    previous_spec_cache: ConnectorSpecification = None

    @pytest.fixture(name="skip_backward_compatibility_tests")
    def skip_backward_compatibility_tests_fixture(
        self,
        inputs: SpecTestConfig,
        previous_connector_docker_runner: ConnectorRunner,
        previous_connector_spec: ConnectorSpecification,
        actual_connector_spec: ConnectorSpecification,
    ) -> bool:
        if actual_connector_spec == previous_connector_spec:
            pytest.skip("The previous and actual specifications are identical.")

        if previous_connector_docker_runner is None:
            pytest.skip("The previous connector image could not be retrieved.")

        # Get the real connector version in case 'latest' is used in the config:
        previous_connector_version = previous_connector_docker_runner._image.labels.get("io.airbyte.version")

        if previous_connector_version == inputs.backward_compatibility_tests_config.disable_for_version:
            pytest.skip(f"Backward compatibility tests are disabled for version {previous_connector_version}.")
        return False

    def test_config_match_spec(self, actual_connector_spec: ConnectorSpecification, connector_config: SecretDict):
        """Check that config matches the actual schema from the spec call"""
        # Getting rid of technical variables that start with an underscore
        config = {key: value for key, value in connector_config.data.items() if not key.startswith("_")}

        try:
            jsonschema.validate(instance=config, schema=actual_connector_spec.connectionSpecification)
        except jsonschema.exceptions.ValidationError as err:
            pytest.fail(f"Config invalid: {err}")
        except jsonschema.exceptions.SchemaError as err:
            pytest.fail(f"Spec is invalid: {err}")

    def test_match_expected(self, connector_spec: ConnectorSpecification, actual_connector_spec: ConnectorSpecification):
        """Check that spec call returns a spec equals to expected one"""
        if connector_spec:
            assert actual_connector_spec == connector_spec, "Spec should be equal to the one in spec.yaml or spec.json file"

    def test_docker_env(self, actual_connector_spec: ConnectorSpecification, docker_runner: ConnectorRunner):
        """Check that connector's docker image has required envs"""
        assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT"), "AIRBYTE_ENTRYPOINT must be set in dockerfile"
        assert docker_runner.env_variables.get("AIRBYTE_ENTRYPOINT") == " ".join(
            docker_runner.entry_point
        ), "env should be equal to space-joined entrypoint"

    def test_enum_usage(self, actual_connector_spec: ConnectorSpecification):
        """Check that enum lists in specs contain distinct values."""
        docs_url = "https://docs.airbyte.io/connector-development/connector-specification-reference"
        docs_msg = f"See specification reference at {docs_url}."

        schema_helper = JsonSchemaHelper(actual_connector_spec.connectionSpecification)
        enum_paths = schema_helper.find_nodes(keys=["enum"])

        for path in enum_paths:
            enum_list = schema_helper.get_node(path)
            assert len(set(enum_list)) == len(
                enum_list
            ), f"Enum lists should not contain duplicate values. Misconfigured enum array: {enum_list}. {docs_msg}"

    def test_oneof_usage(self, actual_connector_spec: ConnectorSpecification):
        """Check that if spec contains oneOf it follows the rules according to reference
        https://docs.airbyte.io/connector-development/connector-specification-reference
        """
        docs_url = "https://docs.airbyte.io/connector-development/connector-specification-reference"
        docs_msg = f"See specification reference at {docs_url}."

        schema_helper = JsonSchemaHelper(actual_connector_spec.connectionSpecification)
        variant_paths = schema_helper.find_nodes(keys=["oneOf", "anyOf"])

        for variant_path in variant_paths:
            top_level_obj = schema_helper.get_node(variant_path[:-1])
            assert (
                top_level_obj.get("type") == "object"
            ), f"The top-level definition in a `oneOf` block should have type: object. misconfigured object: {top_level_obj}. {docs_msg}"

            variants = schema_helper.get_node(variant_path)
            for variant in variants:
                assert "properties" in variant, f"Each item in the oneOf array should be a property with type object. {docs_msg}"

            oneof_path = ".".join(map(str, variant_path))
            variant_props = [set(v["properties"].keys()) for v in variants]
            common_props = set.intersection(*variant_props)
            assert common_props, f"There should be at least one common property for {oneof_path} subobjects. {docs_msg}"

            const_common_props = set()
            for common_prop in common_props:
                if all(["const" in variant["properties"][common_prop] for variant in variants]):
                    const_common_props.add(common_prop)
            assert (
                len(const_common_props) == 1
            ), f"There should be exactly one common property with 'const' keyword for {oneof_path} subobjects. {docs_msg}"

            const_common_prop = const_common_props.pop()
            for n, variant in enumerate(variants):
                prop_obj = variant["properties"][const_common_prop]
                assert (
                    "default" not in prop_obj
                ), f"There should not be 'default' keyword in common property {oneof_path}[{n}].{const_common_prop}. Use `const` instead. {docs_msg}"
                assert (
                    "enum" not in prop_obj
                ), f"There should not be 'enum' keyword in common property {oneof_path}[{n}].{const_common_prop}. Use `const` instead. {docs_msg}"

    def test_required(self):
        """Check that connector will fail if any required field is missing"""

    def test_optional(self):
        """Check that connector can work without any optional field"""

    def test_has_secret(self):
        """Check that spec has a secret. Not sure if this should be always the case"""

    def test_secret_never_in_the_output(self):
        """This test should be injected into any docker command it needs to know current config and spec"""

    @staticmethod
    def _is_spec_property_name_secret(path: str, secret_property_names) -> Tuple[Optional[str], bool]:
        """
        Given a path to a type field, extract a field name and decide whether it is a name of secret or not
        based on a provided list of secret names.
        Split the path by `/`, drop the last item and make list reversed.
        Then iterate over it and find the first item that's not a reserved keyword or an index.
        Example:
        properties/credentials/oneOf/1/properties/api_key/type -> [api_key, properties, 1, oneOf, credentials, properties] -> api_key
        """
        reserved_keywords = ("anyOf", "oneOf", "allOf", "not", "properties", "items", "type", "prefixItems")
        for part in reversed(path.split("/")[:-1]):
            if part.isdigit() or part in reserved_keywords:
                continue
            return part, part.lower() in secret_property_names
        return None, False

    @staticmethod
    def _property_can_store_secret(prop: dict) -> bool:
        """
        Some fields can not hold a secret by design, others can.
        Null type as well as boolean can not hold a secret value.
        A string, a number or an integer type can always store secrets.
        Secret objects and arrays can not be rendered correctly in the UI:
        A field with a constant value can not hold a secret as well.
        """
        unsecure_types = {"string", "integer", "number"}
        type_ = prop["type"]
        is_property_constant_value = bool(prop.get("const"))
        can_store_secret = any(
            [
                isinstance(type_, str) and type_ in unsecure_types,
                isinstance(type_, list) and (set(type_) & unsecure_types),
            ]
        )
        if not can_store_secret:
            return False
        # if a property can store a secret, additional check should be done if it's a constant value
        return not is_property_constant_value

    def test_secret_is_properly_marked(self, connector_spec_dict: dict, detailed_logger, secret_property_names):
        """
        Each field has a type, therefore we can make a flat list of fields from the returned specification.
        Iterate over the list, check if a field name is a secret name, can potentially hold a secret value
        and make sure it is marked as `airbyte_secret`.
        """
        secrets_exposed = []
        non_secrets_hidden = []
        spec_properties = connector_spec_dict["connectionSpecification"]["properties"]
        for type_path, type_value in dpath.util.search(spec_properties, "**/type", yielded=True):
            _, is_property_name_secret = self._is_spec_property_name_secret(type_path, secret_property_names)
            if not is_property_name_secret:
                continue
            absolute_path = f"/{type_path}"
            property_path, _ = absolute_path.rsplit(sep="/", maxsplit=1)
            property_definition = dpath.util.get(spec_properties, property_path)
            marked_as_secret = property_definition.get("airbyte_secret", False)
            possibly_a_secret = self._property_can_store_secret(property_definition)
            if marked_as_secret and not possibly_a_secret:
                non_secrets_hidden.append(property_path)
            if not marked_as_secret and possibly_a_secret:
                secrets_exposed.append(property_path)

        if non_secrets_hidden:
            properties = "\n".join(non_secrets_hidden)
            pytest.fail(
                f"""Some properties are marked with `airbyte_secret` although they probably should not be.
                Please double check them. If they're okay, please fix this test.
                {properties}"""
            )
        if secrets_exposed:
            properties = "\n".join(secrets_exposed)
            pytest.fail(
                f"""The following properties should be marked with `airbyte_secret!`
                    {properties}"""
            )

    def _fail_on_errors(self, errors: List[str]):
        if len(errors) > 0:
            pytest.fail("\n".join(errors))

    def test_property_type_is_not_array(self, connector_spec: ConnectorSpecification):
        """
        Each field has one or multiple types, but the UI only supports a single type and optionally "null" as a second type.
        """
        errors = []
        for type_path, type_value in dpath.util.search(connector_spec.connectionSpecification, "**/properties/*/type", yielded=True):
            if isinstance(type_value, List):
                number_of_types = len(type_value)
                if number_of_types != 2 and number_of_types != 1:
                    errors.append(
                        f"{type_path} is not either a simple type or an array of a simple type plus null: {type_value} (for example: type: [string, null])"
                    )
                if number_of_types == 2 and type_value[1] != "null":
                    errors.append(
                        f"Second type of {type_path} is not null: {type_value}. Type can either be a simple type or an array of a simple type plus null (for example: type: [string, null])"
                    )
        self._fail_on_errors(errors)

    def test_object_not_empty(self, connector_spec: ConnectorSpecification):
        """
        Each object field needs to have at least one property as the UI won't be able to show them otherwise.
        If the whole spec is empty, it's allowed to have a single empty object at the top level
        """
        schema_helper = JsonSchemaHelper(connector_spec.connectionSpecification)
        errors = []
        for type_path, type_value in dpath.util.search(connector_spec.connectionSpecification, "**/type", yielded=True):
            if type_path == "type":
                # allow empty root object
                continue
            if type_value == "object":
                property = schema_helper.get_parent(type_path)
                if "oneOf" not in property and ("properties" not in property or len(property["properties"]) == 0):
                    errors.append(
                        f"{type_path} is an empty object which will not be represented correctly in the UI. Either remove or add specific properties"
                    )
        self._fail_on_errors(errors)

    def test_array_type(self, connector_spec: ConnectorSpecification):
        """
        Each array has one or multiple types for its items, but the UI only supports a single type which can either be object, string or an enum
        """
        schema_helper = JsonSchemaHelper(connector_spec.connectionSpecification)
        errors = []
        for type_path, type_type in dpath.util.search(connector_spec.connectionSpecification, "**/type", yielded=True):
            property_definition = schema_helper.get_parent(type_path)
            if type_type != "array":
                # unrelated "items", not an array definition
                continue
            items_value = property_definition.get("items", None)
            if items_value is None:
                continue
            elif isinstance(items_value, List):
                errors.append(f"{type_path} is not just a single item type: {items_value}")
            elif items_value.get("type") not in ["object", "string", "number", "integer"] and "enum" not in items_value:
                errors.append(f"Items of {type_path} has to be either object or string or define an enum")
        self._fail_on_errors(errors)

    def test_forbidden_complex_types(self, connector_spec: ConnectorSpecification):
        """
        not, anyOf, patternProperties, prefixItems, allOf, if, then, else, dependentSchemas and dependentRequired are not allowed
        """
        forbidden_keys = [
            "not",
            "anyOf",
            "patternProperties",
            "prefixItems",
            "allOf",
            "if",
            "then",
            "else",
            "dependentSchemas",
            "dependentRequired",
        ]
        found_keys = set()
        for forbidden_key in forbidden_keys:
            for path, value in dpath.util.search(connector_spec.connectionSpecification, f"**/{forbidden_key}", yielded=True):
                found_keys.add(path)

        for forbidden_key in forbidden_keys:
            # remove forbidden keys if they are used as properties directly
            for path, _value in dpath.util.search(connector_spec.connectionSpecification, f"**/properties/{forbidden_key}", yielded=True):
                found_keys.remove(path)

        if len(found_keys) > 0:
            key_list = ", ".join(found_keys)
            pytest.fail(f"Found the following disallowed JSON schema features: {key_list}")

    def test_date_pattern(self, connector_spec: ConnectorSpecification, detailed_logger):
        """
        Properties with format date or date-time should always have a pattern defined how the date/date-time should be formatted
        that corresponds with the format the datepicker component is creating.
        """
        schema_helper = JsonSchemaHelper(connector_spec.connectionSpecification)
        for format_path, format in dpath.util.search(connector_spec.connectionSpecification, "**/format", yielded=True):
            if not isinstance(format, str):
                # format is not a format definition here but a property named format
                continue
            property_definition = schema_helper.get_parent(format_path)
            pattern = property_definition.get("pattern")
            if format == "date" and not pattern == DATE_PATTERN:
                detailed_logger.warning(
                    f"{format_path} is defining a date format without the corresponding pattern. Consider setting the pattern to {DATE_PATTERN} to make it easier for users to edit this field in the UI."
                )
            if format == "date-time" and not pattern == DATETIME_PATTERN:
                detailed_logger.warning(
                    f"{format_path} is defining a date-time format without the corresponding pattern Consider setting the pattern to {DATETIME_PATTERN} to make it easier for users to edit this field in the UI."
                )

    def test_date_format(self, connector_spec: ConnectorSpecification, detailed_logger):
        """
        Properties with a pattern that looks like a date should have their format set to date or date-time.
        """
        schema_helper = JsonSchemaHelper(connector_spec.connectionSpecification)
        for pattern_path, pattern in dpath.util.search(connector_spec.connectionSpecification, "**/pattern", yielded=True):
            if not isinstance(pattern, str):
                # pattern is not a pattern definition here but a property named pattern
                continue
            if pattern == DATE_PATTERN or pattern == DATETIME_PATTERN:
                property_definition = schema_helper.get_parent(pattern_path)
                format = property_definition.get("format")
                if not format == "date" and pattern == DATE_PATTERN:
                    detailed_logger.warning(
                        f"{pattern_path} is defining a pattern that looks like a date without setting the format to `date`. Consider specifying the format to make it easier for users to edit this field in the UI."
                    )
                if not format == "date-time" and pattern == DATETIME_PATTERN:
                    detailed_logger.warning(
                        f"{pattern_path} is defining a pattern that looks like a date-time without setting the format to `date-time`. Consider specifying the format to make it easier for users to edit this field in the UI."
                    )

    def test_duplicate_order(self, connector_spec: ConnectorSpecification):
        """
        Custom ordering of field (via the "order" property defined in the field) is not allowed to have duplicates within the same group.
        `{ "a": { "order": 1 }, "b": { "order": 1 } }` is invalid because there are two fields with order 1
        `{ "a": { "order": 1 }, "b": { "order": 1, "group": "x" } }` is valid because the fields with the same order are in different groups
        """
        schema_helper = JsonSchemaHelper(connector_spec.connectionSpecification)
        errors = []
        for properties_path, properties in dpath.util.search(connector_spec.connectionSpecification, "**/properties", yielded=True):
            definition = schema_helper.get_parent(properties_path)
            if definition.get("type") != "object":
                # unrelated "properties", not an actual object definition
                continue
            used_orders: Dict[str, Set[int]] = {}
            for property in properties.values():
                if "order" not in property:
                    continue
                order = property.get("order")
                group = property.get("group", "")
                if group not in used_orders:
                    used_orders[group] = set()
                orders_for_group = used_orders[group]
                if order in orders_for_group:
                    errors.append(f"{properties_path} has duplicate order: {order}")
                orders_for_group.add(order)
        self._fail_on_errors(errors)

    def test_nested_group(self, connector_spec: ConnectorSpecification):
        """
        Groups can only be defined on the top level properties
        `{ "a": { "group": "x" }}` is valid because field "a" is a top level field
        `{ "a": { "oneOf": [{ "type": "object", "properties": { "b": { "group": "x" } } }] }}` is invalid because field "b" is nested in a oneOf
        """
        errors = []
        schema_helper = JsonSchemaHelper(connector_spec.connectionSpecification)
        for result in dpath.util.search(connector_spec.connectionSpecification, "/properties/**/group", yielded=True):
            group_path = result[0]
            parent_path = schema_helper.get_parent_path(group_path)
            is_property_named_group = parent_path.endswith("properties")
            grandparent_path = schema_helper.get_parent_path(parent_path)
            if grandparent_path != "/properties" and not is_property_named_group:
                errors.append(f"Groups can only be defined on top level, is defined at {group_path}")
        self._fail_on_errors(errors)

    def test_required_always_show(self, connector_spec: ConnectorSpecification):
        """
        Fields with always_show are not allowed to be required fields because only optional fields can be hidden in the form in the first place.
        """
        errors = []
        schema_helper = JsonSchemaHelper(connector_spec.connectionSpecification)
        for result in dpath.util.search(connector_spec.connectionSpecification, "/properties/**/always_show", yielded=True):
            always_show_path = result[0]
            parent_path = schema_helper.get_parent_path(always_show_path)
            is_property_named_always_show = parent_path.endswith("properties")
            if is_property_named_always_show:
                continue
            property_name = parent_path.rsplit(sep="/", maxsplit=1)[1]
            properties_path = schema_helper.get_parent_path(parent_path)
            parent_object = schema_helper.get_parent(properties_path)
            if (
                "required" in parent_object
                and isinstance(parent_object.get("required"), List)
                and property_name in parent_object.get("required")
            ):
                errors.append(f"always_show is only allowed on optional properties, but is set on {always_show_path}")
        self._fail_on_errors(errors)

    def test_defined_refs_exist_in_json_spec_file(self, connector_spec_dict: dict):
        """Checking for the presence of unresolved `$ref`s values within each json spec file"""
        check_result = list(find_all_values_for_key_in_schema(connector_spec_dict, "$ref"))
        assert not check_result, "Found unresolved `$refs` value in spec.json file"

    def test_oauth_flow_parameters(self, actual_connector_spec: ConnectorSpecification):
        """Check if connector has correct oauth flow parameters according to
        https://docs.airbyte.io/connector-development/connector-specification-reference
        """
        if not actual_connector_spec.authSpecification:
            return
        spec_schema = actual_connector_spec.connectionSpecification
        oauth_spec = actual_connector_spec.authSpecification.oauth2Specification
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
            pytest.fail("rootObject cannot have more than 2 elements")

        diff = params - schema_path
        assert diff == set(), f"Specified oauth fields are missed from spec schema: {diff}"

    @pytest.mark.default_timeout(60)
    @pytest.mark.backward_compatibility
    def test_backward_compatibility(
        self,
        skip_backward_compatibility_tests: bool,
        actual_connector_spec: ConnectorSpecification,
        previous_connector_spec: ConnectorSpecification,
        number_of_configs_to_generate: int = 100,
    ):
        """Check if the current spec is backward_compatible with the previous one"""
        assert isinstance(actual_connector_spec, ConnectorSpecification) and isinstance(previous_connector_spec, ConnectorSpecification)
        checker = SpecDiffChecker(previous=previous_connector_spec.dict(), current=actual_connector_spec.dict())
        checker.assert_is_backward_compatible()
        validate_previous_configs(previous_connector_spec, actual_connector_spec, number_of_configs_to_generate)

    def test_additional_properties_is_true(self, actual_connector_spec: ConnectorSpecification):
        """Check that value of the "additionalProperties" field is always true.
        A spec declaring "additionalProperties": false introduces the risk of accidental breaking changes.
        Specifically, when removing a property from the spec, existing connector configs will no longer be valid.
        False value introduces the risk of accidental breaking changes.
        Read https://github.com/airbytehq/airbyte/issues/14196 for more details"""
        additional_properties_values = find_all_values_for_key_in_schema(
            actual_connector_spec.connectionSpecification, "additionalProperties"
        )
        if additional_properties_values:
            assert all(
                [additional_properties_value is True for additional_properties_value in additional_properties_values]
            ), "When set, additionalProperties field value must be true for backward compatibility."


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
            output = docker_runner.call_check(config=connector_config, raise_container_error=False)
            trace_messages = filter_output(output, Type.TRACE)
            assert len(trace_messages) == 1, "A trace message should be emitted in case of unexpected errors"
            trace = trace_messages[0].trace
            assert isinstance(trace, AirbyteTraceMessage)
            assert trace.error is not None
            assert trace.error.message is not None


@pytest.mark.default_timeout(30)
class TestDiscovery(BaseTest):

    VALID_TYPES = {"null", "string", "number", "integer", "boolean", "object", "array"}
    VALID_AIRBYTE_TYPES = {"timestamp_with_timezone", "timestamp_without_timezone", "integer"}
    VALID_FORMATS = {"date-time", "date"}
    VALID_TYPE_FORMAT_COMBINATIONS = [
        ({"string"}, "date"),
        ({"string"}, "date-time"),
        ({"string", "null"}, "date"),
        ({"string", "null"}, "date-time"),
    ]
    VALID_TYPE_AIRBYTE_TYPE_COMBINATIONS = [
        ({"string"}, "timestamp_with_timezone"),
        ({"string"}, "timestamp_without_timezone"),
        ({"string", "null"}, "timestamp_with_timezone"),
        ({"integer"}, "integer"),
        ({"integer", "null"}, "integer"),
        ({"number"}, "integer"),
        ({"number", "null"}, "integer"),
    ]

    @pytest.fixture(name="skip_backward_compatibility_tests")
    def skip_backward_compatibility_tests_fixture(
        self,
        inputs: DiscoveryTestConfig,
        previous_connector_docker_runner: ConnectorRunner,
        discovered_catalog: MutableMapping[str, AirbyteStream],
        previous_discovered_catalog: MutableMapping[str, AirbyteStream],
    ) -> bool:
        if discovered_catalog == previous_discovered_catalog:
            pytest.skip("The previous and actual discovered catalogs are identical.")

        if previous_connector_docker_runner is None:
            pytest.skip("The previous connector image could not be retrieved.")

        # Get the real connector version in case 'latest' is used in the config:
        previous_connector_version = previous_connector_docker_runner._image.labels.get("io.airbyte.version")

        if previous_connector_version == inputs.backward_compatibility_tests_config.disable_for_version:
            pytest.skip(f"Backward compatibility tests are disabled for version {previous_connector_version}.")
        return False

    def test_discover(self, connector_config, docker_runner: ConnectorRunner):
        """Verify that discover produce correct schema."""
        output = docker_runner.call_discover(config=connector_config)
        catalog_messages = filter_output(output, Type.CATALOG)

        assert len(catalog_messages) == 1, "Catalog message should be emitted exactly once"
        assert catalog_messages[0].catalog, "Message should have catalog"
        assert catalog_messages[0].catalog.streams, "Catalog should contain streams"

    def test_defined_cursors_exist_in_schema(self, discovered_catalog: Mapping[str, Any]):
        """Check if all of the source defined cursor fields are exists on stream's json schema."""
        for stream_name, stream in discovered_catalog.items():
            if not stream.default_cursor_field:
                continue
            schema = stream.json_schema
            assert "properties" in schema, f"Top level item should have an 'object' type for {stream_name} stream schema"
            cursor_path = "/properties/".join(stream.default_cursor_field)
            cursor_field_location = dpath.util.search(schema["properties"], cursor_path)
            assert cursor_field_location, (
                f"Some of defined cursor fields {stream.default_cursor_field} are not specified in discover schema "
                f"properties for {stream_name} stream"
            )

    def test_defined_refs_exist_in_schema(self, discovered_catalog: Mapping[str, Any]):
        """Check the presence of unresolved `$ref`s values within each json schema."""
        schemas_errors = []
        for stream_name, stream in discovered_catalog.items():
            check_result = list(find_all_values_for_key_in_schema(stream.json_schema, "$ref"))
            if check_result:
                schemas_errors.append({stream_name: check_result})

        assert not schemas_errors, f"Found unresolved `$refs` values for selected streams: {tuple(schemas_errors)}."

    @pytest.mark.parametrize("keyword", ["allOf", "not"])
    def test_defined_keyword_exist_in_schema(self, keyword, discovered_catalog):
        """Checking for the presence of not allowed keywords within each json schema"""
        schemas_errors = []
        for stream_name, stream in discovered_catalog.items():
            check_result = find_keyword_schema(stream.json_schema, key=keyword)
            if check_result:
                schemas_errors.append(stream_name)

        assert not schemas_errors, f"Found not allowed `{keyword}` keyword for selected streams: {schemas_errors}."

    def test_primary_keys_exist_in_schema(self, discovered_catalog: Mapping[str, Any]):
        """Check that all primary keys are present in catalog."""
        for stream_name, stream in discovered_catalog.items():
            for pk in stream.source_defined_primary_key or []:
                schema = stream.json_schema
                pk_path = "/properties/".join(pk)
                pk_field_location = dpath.util.search(schema["properties"], pk_path)
                assert pk_field_location, f"One of the PKs ({pk}) is not specified in discover schema for {stream_name} stream"

    def test_streams_has_sync_modes(self, discovered_catalog: Mapping[str, Any]):
        """Checking that the supported_sync_modes is a not empty field in streams of the catalog."""
        for _, stream in discovered_catalog.items():
            assert stream.supported_sync_modes is not None, f"The stream {stream.name} is missing supported_sync_modes field declaration."
            assert len(stream.supported_sync_modes) > 0, f"supported_sync_modes list on stream {stream.name} should not be empty."

    def test_additional_properties_is_true(self, discovered_catalog: Mapping[str, Any]):
        """Check that value of the "additionalProperties" field is always true.
        A stream schema declaring "additionalProperties": false introduces the risk of accidental breaking changes.
        Specifically, when removing a property from the stream schema, existing connector catalog will no longer be valid.
        False value introduces the risk of accidental breaking changes.
        Read https://github.com/airbytehq/airbyte/issues/14196 for more details"""
        for stream in discovered_catalog.values():
            additional_properties_values = list(find_all_values_for_key_in_schema(stream.json_schema, "additionalProperties"))
            if additional_properties_values:
                assert all(
                    [additional_properties_value is True for additional_properties_value in additional_properties_values]
                ), "When set, additionalProperties field value must be true for backward compatibility."

    @pytest.mark.default_timeout(60)
    @pytest.mark.backward_compatibility
    def test_backward_compatibility(
        self,
        skip_backward_compatibility_tests: bool,
        discovered_catalog: MutableMapping[str, AirbyteStream],
        previous_discovered_catalog: MutableMapping[str, AirbyteStream],
    ):
        """Check if the current catalog is backward_compatible with the previous one."""
        assert isinstance(discovered_catalog, MutableMapping) and isinstance(previous_discovered_catalog, MutableMapping)
        checker = CatalogDiffChecker(previous_discovered_catalog, discovered_catalog)
        checker.assert_is_backward_compatible()

    @pytest.mark.skip("This tests currently leads to too much failures. We need to fix the connectors at scale first.")
    def test_catalog_has_supported_data_types(self, discovered_catalog: Mapping[str, Any]):
        """Check that all streams have supported data types, format and airbyte_types.
        Supported data types are listed there: https://docs.airbyte.com/understanding-airbyte/supported-data-types/
        """
        for stream_name, stream_data in discovered_catalog.items():
            schema_helper = JsonSchemaHelper(stream_data.json_schema)

            for type_path, type_value in dpath.util.search(stream_data.json_schema, "**^^type", yielded=True, separator="^^"):
                parent_path = schema_helper.get_parent_path(type_path)
                parent = schema_helper.get_parent(type_path, separator="^^")
                if not isinstance(type_value, list) and not isinstance(type_value, str):
                    # Skip when type is the name of a property.
                    continue
                type_values = set(type_value) if isinstance(type_value, list) else {type_value}

                # Check unsupported type
                has_unsupported_type = any(t not in self.VALID_TYPES for t in type_values)
                if has_unsupported_type:
                    raise AssertionError(f"Found unsupported type ({type_values}) in {stream_name} stream on property {parent_path}")

                # Check unsupported format
                property_format = parent.get("format")
                if property_format and property_format not in self.VALID_FORMATS:
                    raise AssertionError(f"Found unsupported format ({property_format}) in {stream_name} stream on property {parent_path}")

                # Check unsupported airbyte_type and type/airbyte_type combination
                airbyte_type = parent.get("airbyte_type")
                if airbyte_type and airbyte_type not in self.VALID_AIRBYTE_TYPES:
                    raise AssertionError(
                        f"Found unsupported airbyte_type ({airbyte_type}) in {stream_name} stream on property {parent_path}"
                    )
                if airbyte_type:
                    type_airbyte_type_combination = (type_values, airbyte_type)
                    if type_airbyte_type_combination not in self.VALID_TYPE_AIRBYTE_TYPE_COMBINATIONS:
                        raise AssertionError(
                            f"Found unsupported type/airbyte_type combination {type_airbyte_type_combination} in {stream_name} stream on property {parent_path}"
                        )
                # Check unsupported type/format combination
                if property_format:
                    type_format_combination = (type_values, property_format)
                    if type_format_combination not in self.VALID_TYPE_FORMAT_COMBINATIONS:
                        raise AssertionError(
                            f"Found unsupported type/format combination {type_format_combination} in {stream_name} stream on property {parent_path}"
                        )


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
        Check object structure similar to one expected by schema. Sometimes
        just running schema validation is not enough case schema could have
        additionalProperties parameter set to true and no required fields
        therefore any arbitrary object would pass schema validation.
        This method is here to catch those cases by extracting all the paths
        from the object and compare it to paths expected from jsonschema. If
        there no common pathes then raise an alert.

        :param records: List of airbyte record messages gathered from connector instances.
        :param configured_catalog: Testcase parameters parsed from yaml file
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

            assert (
                common_fields
            ), f" Record {record} from {record.stream} stream with fields {record_fields} should have some fields mentioned by json schema: {schema_pathes}"

    @staticmethod
    def _validate_schema(records: List[AirbyteRecordMessage], configured_catalog: ConfiguredAirbyteCatalog, fail_on_extra_columns: Boolean):
        """
        Check if data type and structure in records matches the one in json_schema of the stream in catalog
        """
        TestBasicRead._validate_records_structure(records, configured_catalog)
        bar = "-" * 80
        streams_errors = verify_records_schema(records, configured_catalog, fail_on_extra_columns)
        for stream_name, errors in streams_errors.items():
            errors = map(str, errors.values())
            str_errors = f"\n{bar}\n".join(errors)
            logging.error(f"\nThe {stream_name} stream has the following schema errors:\n{str_errors}")

        if streams_errors:
            pytest.fail(f"Please check your json_schema in selected streams {tuple(streams_errors.keys())}.")

    def _validate_empty_streams(self, records, configured_catalog, allowed_empty_streams):
        """
        Only certain streams allowed to be empty
        """
        allowed_empty_stream_names = set([allowed_empty_stream.name for allowed_empty_stream in allowed_empty_streams])
        counter = Counter(record.stream for record in records)

        all_streams = set(stream.stream.name for stream in configured_catalog.streams)
        streams_with_records = set(counter.keys())
        streams_without_records = all_streams - streams_with_records

        streams_without_records = streams_without_records - allowed_empty_stream_names
        assert not streams_without_records, f"All streams should return some records, streams without records: {streams_without_records}"

    def _validate_field_appears_at_least_once_in_stream(self, records: List, schema: Dict):
        """
        Get all possible schema paths, then diff with existing record paths.
        In case of `oneOf` or `anyOf` schema props, compare only choice which is present in records.
        """
        expected_paths = get_expected_schema_structure(schema, annotate_one_of=True)
        expected_paths = set(flatten(tuple(expected_paths)))

        for record in records:
            record_paths = set(get_object_structure(record))
            paths_to_remove = {path for path in expected_paths if re.sub(r"\([0-9]*\)", "", path) in record_paths}
            for path in paths_to_remove:
                path_parts = re.split(r"\([0-9]*\)", path)
                if len(path_parts) > 1:
                    expected_paths -= {path for path in expected_paths if path_parts[0] in path}
            expected_paths -= paths_to_remove

        return sorted(list(expected_paths))

    def _validate_field_appears_at_least_once(self, records: List[AirbyteRecordMessage], configured_catalog: ConfiguredAirbyteCatalog):
        """
        Validate if each field in a stream has appeared at least once in some record.
        """

        stream_name_to_empty_fields_mapping = {}
        for stream in configured_catalog.streams:
            stream_records = [record.data for record in records if record.stream == stream.stream.name]

            empty_field_paths = self._validate_field_appears_at_least_once_in_stream(
                records=stream_records, schema=stream.stream.json_schema
            )
            if empty_field_paths:
                stream_name_to_empty_fields_mapping[stream.stream.name] = empty_field_paths

        msg = "Following streams has records with fields, that are either null or not present in each output record:\n"
        for stream_name, fields in stream_name_to_empty_fields_mapping.items():
            msg += f"`{stream_name}` stream has `{fields}` empty fields\n"
        assert not stream_name_to_empty_fields_mapping, msg

    def _validate_expected_records(
        self,
        records: List[AirbyteRecordMessage],
        expected_records_by_stream: MutableMapping[str, List[MutableMapping]],
        flags,
        ignored_fields: Optional[Mapping[str, List[IgnoredFieldsConfiguration]]],
        detailed_logger: Logger,
    ):
        """
        We expect some records from stream to match expected_records, partially or fully, in exact or any order.
        """
        actual_by_stream = self.group_by_stream(records)
        for stream_name, expected in expected_records_by_stream.items():
            actual = actual_by_stream.get(stream_name, [])
            detailed_logger.info(f"Actual records for stream {stream_name}:")
            detailed_logger.log_json_list(actual)
            detailed_logger.info(f"Expected records for stream {stream_name}:")
            detailed_logger.log_json_list(expected)

            ignored_field_names = [field.name for field in ignored_fields.get(stream_name, [])]
            detailed_logger.info(f"Ignored fields for stream {stream_name}:")
            detailed_logger.log_json_list(ignored_field_names)

            self.compare_records(
                stream_name=stream_name,
                actual=actual,
                expected=expected,
                extra_fields=flags.extra_fields,
                exact_order=flags.exact_order,
                extra_records=flags.extra_records,
                ignored_fields=ignored_field_names,
                detailed_logger=detailed_logger,
            )

    @pytest.fixture(name="should_validate_schema")
    def should_validate_schema_fixture(self, inputs: BasicReadTestConfig, test_strictness_level: Config.TestStrictnessLevel):
        if not inputs.validate_schema and test_strictness_level is Config.TestStrictnessLevel.high:
            pytest.fail("High strictness level error: validate_schema must be set to true in the basic read test configuration.")
        else:
            return inputs.validate_schema

    @pytest.fixture(name="should_fail_on_extra_columns")
    def should_fail_on_extra_columns_fixture(self, inputs: BasicReadTestConfig):
        # TODO (Ella): enforce this param once all connectors are passing
        return inputs.fail_on_extra_columns

    @pytest.fixture(name="should_validate_data_points")
    def should_validate_data_points_fixture(self, inputs: BasicReadTestConfig) -> Boolean:
        # TODO: we might want to enforce this when Config.TestStrictnessLevel.high
        return inputs.validate_data_points

    @pytest.fixture(name="configured_catalog")
    def configured_catalog_fixture(
        self,
        test_strictness_level: Config.TestStrictnessLevel,
        configured_catalog_path: Optional[str],
        discovered_catalog: MutableMapping[str, AirbyteStream],
        empty_streams: Set[EmptyStreamConfiguration],
    ) -> ConfiguredAirbyteCatalog:
        """Build a configured catalog for basic read only.
        We discard the use of custom configured catalog if:
        - No custom configured catalog is declared with configured_catalog_path.
        - We are in high test strictness level.
        When a custom configured catalog is discarded we use the discovered catalog from which we remove the declared empty streams.
        We use a custom configured catalog if a configured_catalog_path is declared and we are not in high test strictness level.
        Args:
            test_strictness_level (Config.TestStrictnessLevel): The current test strictness level according to the global test configuration.
            configured_catalog_path (Optional[str]): Path to a JSON file containing a custom configured catalog.
            discovered_catalog (MutableMapping[str, AirbyteStream]): The discovered catalog.
            empty_streams (Set[EmptyStreamConfiguration]): The empty streams declared in the test configuration.

        Returns:
            ConfiguredAirbyteCatalog: the configured Airbyte catalog.
        """
        if test_strictness_level is Config.TestStrictnessLevel.high or not configured_catalog_path:
            if configured_catalog_path:
                pytest.fail(
                    "High strictness level error: you can't set a custom configured catalog on the basic read test when strictness level is high."
                )
            return build_configured_catalog_from_discovered_catalog_and_empty_streams(discovered_catalog, empty_streams)
        else:
            return build_configured_catalog_from_custom_catalog(configured_catalog_path, discovered_catalog)

    def test_read(
        self,
        connector_config,
        configured_catalog,
        expect_records_config: ExpectedRecordsConfig,
        should_validate_schema: Boolean,
        should_validate_data_points: Boolean,
        should_fail_on_extra_columns: Boolean,
        empty_streams: Set[EmptyStreamConfiguration],
        ignored_fields: Optional[Mapping[str, List[IgnoredFieldsConfiguration]]],
        expected_records_by_stream: MutableMapping[str, List[MutableMapping]],
        docker_runner: ConnectorRunner,
        detailed_logger,
    ):
        output = docker_runner.call_read(connector_config, configured_catalog)
        records = [message.record for message in filter_output(output, Type.RECORD)]

        assert records, "At least one record should be read using provided catalog"

        if should_validate_schema:
            self._validate_schema(
                records=records, configured_catalog=configured_catalog, fail_on_extra_columns=should_fail_on_extra_columns
            )

        self._validate_empty_streams(records=records, configured_catalog=configured_catalog, allowed_empty_streams=empty_streams)
        for pks, record in primary_keys_for_records(streams=configured_catalog.streams, records=records):
            for pk_path, pk_value in pks.items():
                assert (
                    pk_value is not None
                ), f"Primary key subkeys {repr(pk_path)} have null values or not present in {record.stream} stream records."

        # TODO: remove this condition after https://github.com/airbytehq/airbyte/issues/8312 is done
        if should_validate_data_points:
            self._validate_field_appears_at_least_once(records=records, configured_catalog=configured_catalog)

        if expected_records_by_stream:
            self._validate_expected_records(
                records=records,
                expected_records_by_stream=expected_records_by_stream,
                flags=expect_records_config,
                ignored_fields=ignored_fields,
                detailed_logger=detailed_logger,
            )

    def test_airbyte_trace_message_on_failure(self, connector_config, inputs: BasicReadTestConfig, docker_runner: ConnectorRunner):
        if not inputs.expect_trace_message_on_failure:
            pytest.skip("Skipping `test_airbyte_trace_message_on_failure` because `inputs.expect_trace_message_on_failure=False`")
            return

        invalid_configured_catalog = ConfiguredAirbyteCatalog(
            streams=[
                # create ConfiguredAirbyteStream without validation
                ConfiguredAirbyteStream.construct(
                    stream=AirbyteStream(
                        name="__AIRBYTE__stream_that_does_not_exist",
                        json_schema={"type": "object", "properties": {"f1": {"type": "string"}}},
                        supported_sync_modes=[SyncMode.full_refresh],
                    ),
                    sync_mode="INVALID",
                    destination_sync_mode="INVALID",
                )
            ]
        )

        output = docker_runner.call_read(connector_config, invalid_configured_catalog, raise_container_error=False)
        trace_messages = filter_output(output, Type.TRACE)
        error_trace_messages = list(filter(lambda m: m.trace.type == TraceType.ERROR, trace_messages))

        assert len(error_trace_messages) >= 1, "Connector should emit at least one error trace message"

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
        actual: List[Mapping[str, Any]],
        expected: List[Mapping[str, Any]],
        extra_fields: bool,
        exact_order: bool,
        extra_records: bool,
        ignored_fields: List[str],
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
                if ignored_fields:
                    delete_fields(r1, ignored_fields)
                    delete_fields(r2, ignored_fields)
                assert r1 == r2, f"Stream {stream_name}: Mismatch of record order or values"
        else:
            _make_hashable = functools.partial(make_hashable, exclude_fields=ignored_fields) if ignored_fields else make_hashable
            expected = set(map(_make_hashable, expected))
            actual = set(map(_make_hashable, actual))
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
    def group_by_stream(records: List[AirbyteRecordMessage]) -> MutableMapping[str, List[MutableMapping]]:
        """Group records by a source stream"""
        result = defaultdict(list)
        for record in records:
            result[record.stream].append(record.data)

        return result
