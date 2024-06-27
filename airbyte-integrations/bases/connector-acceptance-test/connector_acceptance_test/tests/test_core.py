#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import re
from collections import Counter, defaultdict
from functools import reduce
from logging import Logger
from os.path import splitext
from pathlib import Path
from threading import Thread
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Set, Tuple
from xmlrpc.client import Boolean

import connector_acceptance_test.utils.docs as docs_utils
import dpath.util
import jsonschema
import pytest
import requests
from airbyte_protocol.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateStats,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
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
    ConnectorAttributesConfig,
    DiscoveryTestConfig,
    EmptyStreamConfiguration,
    ExpectedRecordsConfig,
    IgnoredFieldsConfiguration,
    NoPrimaryKeyConfiguration,
    SpecTestConfig,
    UnsupportedFileTypeConfig,
)
from connector_acceptance_test.utils import ConnectorRunner, SecretDict, filter_output, make_hashable, verify_records_schema
from connector_acceptance_test.utils.backward_compatibility import CatalogDiffChecker, SpecDiffChecker, validate_previous_configs
from connector_acceptance_test.utils.common import (
    build_configured_catalog_from_custom_catalog,
    build_configured_catalog_from_discovered_catalog_and_empty_streams,
    find_all_values_for_key_in_schema,
    find_keyword_schema,
)
from connector_acceptance_test.utils.json_schema_helper import (
    JsonSchemaHelper,
    flatten_tuples,
    get_expected_schema_structure,
    get_object_structure,
    get_paths_in_connector_config,
)
from connector_acceptance_test.utils.timeouts import FIVE_MINUTES, ONE_MINUTE, TEN_MINUTES

pytestmark = [
    pytest.mark.anyio,
]


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


# Running tests in parallel can sometime delay the execution of the tests if downstream services are not able to handle the load.
# This is why we set a timeout on tests that call command that should return quickly, like spec
@pytest.mark.default_timeout(ONE_MINUTE)
class TestSpec(BaseTest):
    @pytest.fixture(name="skip_backward_compatibility_tests")
    async def skip_backward_compatibility_tests_fixture(
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
        previous_connector_version = await previous_connector_docker_runner.get_container_label("io.airbyte.version")

        if previous_connector_version == inputs.backward_compatibility_tests_config.disable_for_version:
            pytest.skip(f"Backward compatibility tests are disabled for version {previous_connector_version}.")
        return False

    @pytest.fixture(name="skip_oauth_default_method_test")
    def skip_oauth_default_method_test_fixture(self, inputs: SpecTestConfig):
        if inputs.auth_default_method and not inputs.auth_default_method.oauth:
            pytest.skip(f"Skipping OAuth is default method test: {inputs.auth_default_method.bypass_reason}")
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
        else:
            pytest.skip("The spec.yaml or spec.json does not exist. Hence, comparison with the actual one can't be performed")

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
                    "default" not in prop_obj or prop_obj["default"] == prop_obj["const"]
                ), f"'default' needs to be identical to const in common property {oneof_path}[{n}].{const_common_prop}. It's recommended to just use `const`. {docs_msg}"
                assert "enum" not in prop_obj or (
                    len(prop_obj["enum"]) == 1 and prop_obj["enum"][0] == prop_obj["const"]
                ), f"'enum' needs to be an array with a single item identical to const in common property {oneof_path}[{n}].{const_common_prop}. It's recommended to just use `const`. {docs_msg}"

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

    def test_property_type_is_not_array(self, actual_connector_spec: ConnectorSpecification):
        """
        Each field has one or multiple types, but the UI only supports a single type and optionally "null" as a second type.
        """
        errors = []
        for type_path, type_value in dpath.util.search(actual_connector_spec.connectionSpecification, "**/properties/*/type", yielded=True):
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

    def test_object_not_empty(self, actual_connector_spec: ConnectorSpecification):
        """
        Each object field needs to have at least one property as the UI won't be able to show them otherwise.
        If the whole spec is empty, it's allowed to have a single empty object at the top level
        """
        schema_helper = JsonSchemaHelper(actual_connector_spec.connectionSpecification)
        errors = []
        for type_path, type_value in dpath.util.search(actual_connector_spec.connectionSpecification, "**/type", yielded=True):
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

    def test_array_type(self, actual_connector_spec: ConnectorSpecification):
        """
        Each array has one or multiple types for its items, but the UI only supports a single type which can either be object, string or an enum
        """
        schema_helper = JsonSchemaHelper(actual_connector_spec.connectionSpecification)
        errors = []
        for type_path, type_type in dpath.util.search(actual_connector_spec.connectionSpecification, "**/type", yielded=True):
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

    def test_forbidden_complex_types(self, actual_connector_spec: ConnectorSpecification):
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
            for path, value in dpath.util.search(actual_connector_spec.connectionSpecification, f"**/{forbidden_key}", yielded=True):
                found_keys.add(path)

        for forbidden_key in forbidden_keys:
            # remove forbidden keys if they are used as properties directly
            for path, _value in dpath.util.search(
                actual_connector_spec.connectionSpecification, f"**/properties/{forbidden_key}", yielded=True
            ):
                found_keys.remove(path)

        if len(found_keys) > 0:
            key_list = ", ".join(found_keys)
            pytest.fail(f"Found the following disallowed JSON schema features: {key_list}")

    def test_date_pattern(self, actual_connector_spec: ConnectorSpecification, detailed_logger):
        """
        Properties with format date or date-time should always have a pattern defined how the date/date-time should be formatted
        that corresponds with the format the datepicker component is creating.
        """
        schema_helper = JsonSchemaHelper(actual_connector_spec.connectionSpecification)
        for format_path, format in dpath.util.search(actual_connector_spec.connectionSpecification, "**/format", yielded=True):
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

    def test_date_format(self, actual_connector_spec: ConnectorSpecification, detailed_logger):
        """
        Properties with a pattern that looks like a date should have their format set to date or date-time.
        """
        schema_helper = JsonSchemaHelper(actual_connector_spec.connectionSpecification)
        for pattern_path, pattern in dpath.util.search(actual_connector_spec.connectionSpecification, "**/pattern", yielded=True):
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

    def test_duplicate_order(self, actual_connector_spec: ConnectorSpecification):
        """
        Custom ordering of field (via the "order" property defined in the field) is not allowed to have duplicates within the same group.
        `{ "a": { "order": 1 }, "b": { "order": 1 } }` is invalid because there are two fields with order 1
        `{ "a": { "order": 1 }, "b": { "order": 1, "group": "x" } }` is valid because the fields with the same order are in different groups
        """
        schema_helper = JsonSchemaHelper(actual_connector_spec.connectionSpecification)
        errors = []
        for properties_path, properties in dpath.util.search(actual_connector_spec.connectionSpecification, "**/properties", yielded=True):
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

    def test_nested_group(self, actual_connector_spec: ConnectorSpecification):
        """
        Groups can only be defined on the top level properties
        `{ "a": { "group": "x" }}` is valid because field "a" is a top level field
        `{ "a": { "oneOf": [{ "type": "object", "properties": { "b": { "group": "x" } } }] }}` is invalid because field "b" is nested in a oneOf
        """
        errors = []
        schema_helper = JsonSchemaHelper(actual_connector_spec.connectionSpecification)
        for result in dpath.util.search(actual_connector_spec.connectionSpecification, "/properties/**/group", yielded=True):
            group_path = result[0]
            parent_path = schema_helper.get_parent_path(group_path)
            is_property_named_group = parent_path.endswith("properties")
            grandparent_path = schema_helper.get_parent_path(parent_path)
            if grandparent_path != "/properties" and not is_property_named_group:
                errors.append(f"Groups can only be defined on top level, is defined at {group_path}")
        self._fail_on_errors(errors)

    def test_display_type(self, actual_connector_spec: ConnectorSpecification):
        """
        The display_type property can only be set on fields which have a oneOf property, and must be either "dropdown" or "radio"
        """
        errors = []
        schema_helper = JsonSchemaHelper(actual_connector_spec.connectionSpecification)
        for result in dpath.util.search(actual_connector_spec.connectionSpecification, "/properties/**/display_type", yielded=True):
            display_type_path = result[0]
            parent_path = schema_helper.get_parent_path(display_type_path)
            is_property_named_display_type = parent_path.endswith("properties")
            if is_property_named_display_type:
                continue
            parent_object = schema_helper.get_parent(display_type_path)
            if "oneOf" not in parent_object:
                errors.append(f"display_type is only allowed on fields which have a oneOf property, but is set on {parent_path}")
            display_type_value = parent_object.get("display_type")
            if display_type_value != "dropdown" and display_type_value != "radio":
                errors.append(
                    f"display_type must be either 'dropdown' or 'radio', but is set to '{display_type_value}' at {display_type_path}"
                )
        self._fail_on_errors(errors)

    def test_defined_refs_exist_in_json_spec_file(self, connector_spec_dict: dict):
        """Checking for the presence of unresolved `$ref`s values within each json spec file"""
        check_result = list(find_all_values_for_key_in_schema(connector_spec_dict, "$ref"))
        assert not check_result, "Found unresolved `$refs` value in spec.json file"

    def test_oauth_flow_parameters(self, actual_connector_spec: ConnectorSpecification):
        """Check if connector has correct oauth flow parameters according to
        https://docs.airbyte.io/connector-development/connector-specification-reference
        """
        advanced_auth = actual_connector_spec.advanced_auth
        if not advanced_auth:
            return
        spec_schema = actual_connector_spec.connectionSpecification
        paths_to_validate = set()
        if advanced_auth.predicate_key:
            paths_to_validate.add("/" + "/".join(advanced_auth.predicate_key))
        oauth_config_specification = advanced_auth.oauth_config_specification
        if oauth_config_specification:
            if oauth_config_specification.oauth_user_input_from_connector_config_specification:
                paths_to_validate.update(
                    get_paths_in_connector_config(
                        oauth_config_specification.oauth_user_input_from_connector_config_specification["properties"]
                    )
                )
            if oauth_config_specification.complete_oauth_output_specification:
                paths_to_validate.update(
                    get_paths_in_connector_config(oauth_config_specification.complete_oauth_output_specification["properties"])
                )
            if oauth_config_specification.complete_oauth_server_output_specification:
                paths_to_validate.update(
                    get_paths_in_connector_config(oauth_config_specification.complete_oauth_server_output_specification["properties"])
                )

        diff = paths_to_validate - set(get_expected_schema_structure(spec_schema))
        assert diff == set(), f"Specified oauth fields are missed from spec schema: {diff}"

    def test_oauth_is_default_method(self, skip_oauth_default_method_test: bool, actual_connector_spec: ConnectorSpecification):
        """
        OAuth is default check.
        If credentials do have oneOf: we check that the OAuth is listed at first.
        If there is no oneOf and Oauth: OAuth is only option to authenticate the source and no check is needed.
        """
        advanced_auth = actual_connector_spec.advanced_auth
        if not advanced_auth:
            pytest.skip("Source does not have OAuth method.")
        if not advanced_auth.predicate_key:
            pytest.skip("Advanced Auth object does not have predicate_key, only one option to authenticate.")

        spec_schema = actual_connector_spec.connectionSpecification
        credentials = advanced_auth.predicate_key[0]
        try:
            one_of_default_method = dpath.util.get(spec_schema, f"/**/{credentials}/oneOf/0")
        except KeyError as e:  # Key Error when oneOf is not in credentials object
            pytest.skip("Credentials object does not have oneOf option.")

        path_in_credentials = "/".join(advanced_auth.predicate_key[1:])
        auth_method_predicate_const = dpath.util.get(one_of_default_method, f"/**/{path_in_credentials}/const")
        assert (
            auth_method_predicate_const == advanced_auth.predicate_value
        ), f"Oauth method should be a default option. Current default method is {auth_method_predicate_const}."

    @pytest.mark.default_timeout(ONE_MINUTE)
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

    # This test should not be part of TestSpec because it's testing the connector's docker image content, not the spec itself
    # But it's cumbersome to declare a separate, non configurable, test class
    # See https://github.com/airbytehq/airbyte/issues/15551
    async def test_image_labels(self, docker_runner: ConnectorRunner, connector_metadata: dict):
        """Check that connector's docker image has required labels"""
        assert (
            await docker_runner.get_container_label("io.airbyte.name") == connector_metadata["data"]["dockerRepository"]
        ), "io.airbyte.name must be equal to dockerRepository in metadata.yaml"
        assert (
            await docker_runner.get_container_label("io.airbyte.version") == connector_metadata["data"]["dockerImageTag"]
        ), "io.airbyte.version must be equal to dockerImageTag in metadata.yaml"

    # This test should not be part of TestSpec because it's testing the connector's docker image content, not the spec itself
    # But it's cumbersome to declare a separate, non configurable, test class
    # See https://github.com/airbytehq/airbyte/issues/15551
    async def test_image_environment_variables(self, docker_runner: ConnectorRunner):
        """Check that connector's docker image has required envs"""
        assert await docker_runner.get_container_env_variable_value("AIRBYTE_ENTRYPOINT"), "AIRBYTE_ENTRYPOINT must be set in dockerfile"
        assert await docker_runner.get_container_env_variable_value("AIRBYTE_ENTRYPOINT") == await docker_runner.get_container_entrypoint()


@pytest.mark.default_timeout(ONE_MINUTE)
class TestConnection(BaseTest):
    async def test_check(self, connector_config, inputs: ConnectionTestConfig, docker_runner: ConnectorRunner):
        if inputs.status == ConnectionTestConfig.Status.Succeed:
            output = await docker_runner.call_check(config=connector_config)
            con_messages = filter_output(output, Type.CONNECTION_STATUS)

            assert len(con_messages) == 1, "Connection status message should be emitted exactly once"
            assert con_messages[0].connectionStatus.status == Status.SUCCEEDED
        elif inputs.status == ConnectionTestConfig.Status.Failed:
            output = await docker_runner.call_check(config=connector_config)
            con_messages = filter_output(output, Type.CONNECTION_STATUS)

            assert len(con_messages) == 1, "Connection status message should be emitted exactly once"
            assert con_messages[0].connectionStatus.status == Status.FAILED
        elif inputs.status == ConnectionTestConfig.Status.Exception:
            output = await docker_runner.call_check(config=connector_config, raise_container_error=False)
            trace_messages = filter_output(output, Type.TRACE)
            assert len(trace_messages) == 1, "A trace message should be emitted in case of unexpected errors"
            trace = trace_messages[0].trace
            assert isinstance(trace, AirbyteTraceMessage)
            assert trace.error is not None
            assert trace.error.message is not None


# Running tests in parallel can sometime delay the execution of the tests if downstream services are not able to handle the load.
# This is why we set a timeout on tests that call command that should return quickly, like discover
@pytest.mark.default_timeout(FIVE_MINUTES)
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

    @pytest.fixture()
    async def skip_backward_compatibility_tests_for_version(
        self, inputs: DiscoveryTestConfig, previous_connector_docker_runner: ConnectorRunner
    ):
        # Get the real connector version in case 'latest' is used in the config:
        previous_connector_version = await previous_connector_docker_runner.get_container_label("io.airbyte.version")
        if previous_connector_version == inputs.backward_compatibility_tests_config.disable_for_version:
            pytest.skip(f"Backward compatibility tests are disabled for version {previous_connector_version}.")
        return False

    @pytest.fixture(name="skip_backward_compatibility_tests")
    async def skip_backward_compatibility_tests_fixture(
        self,
        # Even if unused, this fixture is required to make sure that the skip_backward_compatibility_tests_for_version fixture is called.
        skip_backward_compatibility_tests_for_version: bool,
        previous_connector_docker_runner: ConnectorRunner,
        discovered_catalog: MutableMapping[str, AirbyteStream],
        previous_discovered_catalog: MutableMapping[str, AirbyteStream],
    ) -> bool:
        if discovered_catalog == previous_discovered_catalog:
            pytest.skip("The previous and actual discovered catalogs are identical.")

        if previous_connector_docker_runner is None:
            pytest.skip("The previous connector image could not be retrieved.")

        return False

    async def test_discover(self, connector_config, docker_runner: ConnectorRunner):
        """Verify that discover produce correct schema."""
        output = await docker_runner.call_discover(config=connector_config)
        catalog_messages = filter_output(output, Type.CATALOG)
        duplicated_stream_names = self.duplicated_stream_names(catalog_messages[0].catalog.streams)

        assert len(catalog_messages) == 1, "Catalog message should be emitted exactly once"
        assert catalog_messages[0].catalog, "Message should have catalog"
        assert catalog_messages[0].catalog.streams, "Catalog should contain streams"
        assert len(duplicated_stream_names) == 0, f"Catalog should have uniquely named streams, duplicates are: {duplicated_stream_names}"

    def duplicated_stream_names(self, streams) -> List[str]:
        """Counts number of times a stream appears in the catalog"""
        name_counts = dict()
        for stream in streams:
            count = name_counts.get(stream.name, 0)
            name_counts[stream.name] = count + 1
        return [k for k, v in name_counts.items() if v > 1]

    def test_streams_have_valid_json_schemas(self, discovered_catalog: Mapping[str, Any]):
        """Check if all stream schemas are valid json schemas."""
        for stream_name, stream in discovered_catalog.items():
            jsonschema.Draft7Validator.check_schema(stream.json_schema)

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

    @pytest.mark.default_timeout(ONE_MINUTE)
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

    def test_primary_keys_data_type(self, inputs: DiscoveryTestConfig, discovered_catalog: Mapping[str, Any]):
        if not inputs.validate_primary_keys_data_type:
            pytest.skip("Primary keys data type validation is disabled in config.")

        forbidden_primary_key_data_types: Set[str] = {"object", "array"}
        errors: List[str] = []

        for stream_name, stream in discovered_catalog.items():
            if not stream.source_defined_primary_key:
                continue

            for primary_key_part in stream.source_defined_primary_key:
                primary_key_path = "/properties/".join(primary_key_part)
                try:
                    primary_key_definition = dpath.util.get(stream.json_schema["properties"], primary_key_path)
                except KeyError:
                    errors.append(f"Stream {stream_name} does not have defined primary key in schema")
                    continue

                data_type = set(primary_key_definition.get("type", []))

                if data_type.intersection(forbidden_primary_key_data_types):
                    errors.append(f"Stream {stream_name} contains primary key with forbidden type of {data_type}")

        assert not errors, "\n".join(errors)


def primary_keys_for_records(streams, records):
    streams_with_primary_key = [stream for stream in streams if stream.stream.source_defined_primary_key]
    for stream in streams_with_primary_key:
        stream_records = [r for r in records if r.stream == stream.stream.name]
        for stream_record in stream_records:
            pk_values = _extract_primary_key_value(stream_record.data, stream.stream.source_defined_primary_key)
            yield pk_values, stream_record


def _extract_pk_values(records: Iterable[Mapping[str, Any]], primary_key: List[List[str]]) -> Iterable[dict[Tuple[str], Any]]:
    for record in records:
        yield _extract_primary_key_value(record, primary_key)


def _extract_primary_key_value(record: Mapping[str, Any], primary_key: List[List[str]]) -> dict[Tuple[str], Any]:
    pk_values = {}
    for pk_path in primary_key:
        pk_value: Any = reduce(lambda data, key: data.get(key) if isinstance(data, dict) else None, pk_path, record)
        pk_values[tuple(pk_path)] = pk_value
    return pk_values


@pytest.mark.default_timeout(TEN_MINUTES)
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
        there no common paths then raise an alert.

        :param records: List of airbyte record messages gathered from connector instances.
        :param configured_catalog: Testcase parameters parsed from yaml file
        """
        schemas: Dict[str, Set] = {}
        for stream in configured_catalog.streams:
            schemas[stream.stream.name] = set(get_expected_schema_structure(stream.stream.json_schema))

        for record in records:
            schema_paths = schemas.get(record.stream)
            if not schema_paths:
                continue
            record_fields = set(get_object_structure(record.data))
            common_fields = set.intersection(record_fields, schema_paths)

            assert (
                common_fields
            ), f" Record {record} from {record.stream} stream with fields {record_fields} should have some fields mentioned by json schema: {schema_paths}"

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
        expected_paths = set(flatten_tuples(tuple(expected_paths)))

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
        configured_catalog: ConfiguredAirbyteCatalog,
    ):
        """
        We expect some records from stream to match expected_records, partially or fully, in exact or any order.
        """
        actual_by_stream = self.group_by_stream(records)
        for stream_name, expected in expected_records_by_stream.items():
            actual = actual_by_stream.get(stream_name, [])
            detailed_logger.info(f"Actual records for stream {stream_name}:")
            detailed_logger.info(actual)
            ignored_field_names = [field.name for field in ignored_fields.get(stream_name, [])]
            self.compare_records(
                stream_name=stream_name,
                actual=actual,
                expected=expected,
                exact_order=flags.exact_order,
                detailed_logger=detailed_logger,
                configured_catalog=configured_catalog,
            )

    @pytest.fixture(name="should_validate_schema")
    def should_validate_schema_fixture(self, inputs: BasicReadTestConfig, test_strictness_level: Config.TestStrictnessLevel):
        if not inputs.validate_schema and test_strictness_level is Config.TestStrictnessLevel.high:
            pytest.fail("High strictness level error: validate_schema must be set to true in the basic read test configuration.")
        else:
            return inputs.validate_schema

    @pytest.fixture(name="should_validate_stream_statuses")
    def should_validate_stream_statuses_fixture(self, inputs: BasicReadTestConfig, is_connector_certified: bool):
        if inputs.validate_stream_statuses is None and is_connector_certified:
            return True
        if not inputs.validate_stream_statuses and is_connector_certified:
            pytest.fail("High strictness level error: validate_stream_statuses must be set to true in the basic read test configuration.")
        return inputs.validate_stream_statuses

    @pytest.fixture(name="should_validate_state_messages")
    def should_validate_state_messages_fixture(self, inputs: BasicReadTestConfig):
        return inputs.validate_state_messages

    @pytest.fixture(name="should_validate_primary_keys_data_type")
    def should_validate_primary_keys_data_type_fixture(self, inputs: BasicReadTestConfig):
        return inputs.validate_primary_keys_data_type

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

    _file_types: Set[str] = set()

    async def test_read(
        self,
        connector_config: SecretDict,
        configured_catalog: ConfiguredAirbyteCatalog,
        expect_records_config: ExpectedRecordsConfig,
        should_validate_schema: Boolean,
        should_validate_data_points: Boolean,
        should_validate_stream_statuses: Boolean,
        should_validate_state_messages: Boolean,
        should_validate_primary_keys_data_type: Boolean,
        should_fail_on_extra_columns: Boolean,
        empty_streams: Set[EmptyStreamConfiguration],
        ignored_fields: Optional[Mapping[str, List[IgnoredFieldsConfiguration]]],
        expected_records_by_stream: MutableMapping[str, List[MutableMapping]],
        docker_runner: ConnectorRunner,
        detailed_logger: Logger,
        certified_file_based_connector: bool,
    ):
        output = await docker_runner.call_read(connector_config, configured_catalog)

        records = [message.record for message in filter_output(output, Type.RECORD)]
        state_messages = [message for message in filter_output(output, Type.STATE)]

        if certified_file_based_connector:
            self._file_types.update(self._get_actual_file_types(records))

        assert records, "At least one record should be read using provided catalog"

        if should_validate_schema:
            self._validate_schema(records=records, configured_catalog=configured_catalog)

        self._validate_empty_streams(records=records, configured_catalog=configured_catalog, allowed_empty_streams=empty_streams)

        if should_validate_primary_keys_data_type:
            self._validate_primary_keys_data_type(streams=configured_catalog.streams, records=records)

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
                configured_catalog=configured_catalog,
            )

        if should_validate_stream_statuses:
            all_statuses = [
                message.trace.stream_status
                for message in filter_output(output, Type.TRACE)
                if message.trace.type == TraceType.STREAM_STATUS
            ]
            self._validate_stream_statuses(configured_catalog=configured_catalog, statuses=all_statuses)

        if should_validate_state_messages:
            self._validate_state_messages(state_messages=state_messages, configured_catalog=configured_catalog)

    async def test_airbyte_trace_message_on_failure(self, connector_config, inputs: BasicReadTestConfig, docker_runner: ConnectorRunner):
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

        output = await docker_runner.call_read(connector_config, invalid_configured_catalog, raise_container_error=False)
        trace_messages = filter_output(output, Type.TRACE)
        error_trace_messages = list(filter(lambda m: m.trace.type == TraceType.ERROR, trace_messages))

        assert len(error_trace_messages) >= 1, "Connector should emit at least one error trace message"

    @staticmethod
    def compare_records(
        stream_name: str,
        actual: List[Mapping[str, Any]],
        expected: List[Mapping[str, Any]],
        exact_order: bool,
        detailed_logger: Logger,
        configured_catalog: ConfiguredAirbyteCatalog,
    ):
        """Compare records using combination of restrictions"""
        configured_streams = [stream for stream in configured_catalog.streams if stream.stream.name == stream_name]
        if len(configured_streams) != 1:
            raise ValueError(f"Expected exactly one stream matching name {stream_name} but got {len(configured_streams)}")

        configured_stream = configured_streams[0]
        if configured_stream.stream.source_defined_primary_key:
            # as part of the migration for relaxing CATs, we are starting only with the streams that defines primary keys
            expected_primary_keys = list(_extract_pk_values(expected, configured_stream.stream.source_defined_primary_key))
            actual_primary_keys = list(_extract_pk_values(actual, configured_stream.stream.source_defined_primary_key))
            if exact_order:
                assert (
                    actual_primary_keys[: len(expected_primary_keys)] == expected_primary_keys
                ), f"Expected to see those primary keys in order in the actual response for stream {stream_name}."
            else:
                expected_but_not_found = set(map(make_hashable, expected_primary_keys)).difference(
                    set(map(make_hashable, actual_primary_keys))
                )
                assert (
                    not expected_but_not_found
                ), f"Expected to see those primary keys in the actual response for stream {stream_name} but they were not found."
        elif len(expected) > len(actual):
            if exact_order:
                detailed_logger.warning("exact_order is `True` but validation without primary key does not consider order")

            expected = set(map(make_hashable, expected))
            actual = set(map(make_hashable, actual))
            missing_expected = set(expected) - set(actual)

            extra = set(actual) - set(expected)
            msg = f"Expected to have at least as many records than expected for stream {stream_name}."
            detailed_logger.info(msg)
            detailed_logger.info("missing:")
            detailed_logger.log_json_list(sorted(missing_expected))
            detailed_logger.info("expected:")
            detailed_logger.log_json_list(sorted(expected))
            detailed_logger.info("actual:")
            detailed_logger.log_json_list(sorted(actual))
            detailed_logger.info("extra:")
            detailed_logger.log_json_list(sorted(extra))
            pytest.fail(msg)

    @staticmethod
    def group_by_stream(records: List[AirbyteRecordMessage]) -> MutableMapping[str, List[MutableMapping]]:
        """Group records by a source stream"""
        result = defaultdict(list)
        for record in records:
            result[record.stream].append(record.data)

        return result

    @pytest.fixture(name="certified_file_based_connector")
    def is_certified_file_based_connector(self, connector_metadata: Dict[str, Any], is_connector_certified: bool) -> bool:
        metadata = connector_metadata.get("data", {})

        # connector subtype is specified in data.connectorSubtype field
        file_based_connector = metadata.get("connectorSubtype") == "file"

        return file_based_connector and is_connector_certified

    @staticmethod
    def _get_file_extension(file_name: str) -> str:
        _, file_extension = splitext(file_name)
        return file_extension.casefold()

    def _get_actual_file_types(self, records: List[AirbyteRecordMessage]) -> Set[str]:
        return {self._get_file_extension(record.data.get("_ab_source_file_url", "")) for record in records}

    @staticmethod
    def _get_unsupported_file_types(config: List[UnsupportedFileTypeConfig]) -> Set[str]:
        return {t.extension.casefold() for t in config}

    async def test_all_supported_file_types_present(self, certified_file_based_connector: bool, inputs: BasicReadTestConfig):
        if not certified_file_based_connector or inputs.file_types.skip_test:
            reason = (
                "Skipping the test for supported file types"
                f"{' as it is only applicable for certified file-based connectors' if not certified_file_based_connector else ''}."
            )
            pytest.skip(reason)

        structured_types = {".avro", ".csv", ".jsonl", ".parquet"}
        unstructured_types = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".md"}

        if inputs.file_types.unsupported_types:
            unsupported_file_types = self._get_unsupported_file_types(inputs.file_types.unsupported_types)
            structured_types.difference_update(unsupported_file_types)
            unstructured_types.difference_update(unsupported_file_types)

        missing_structured_types = structured_types - self._file_types
        missing_unstructured_types = unstructured_types - self._file_types

        # all structured and at least one of unstructured supported file types should be present
        assert not missing_structured_types and len(missing_unstructured_types) != len(unstructured_types), (
            f"Please make sure you added files with the following supported structured types {missing_structured_types} "
            f"and at least one with unstructured type {unstructured_types} to the test account "
            "or add them to the `file_types -> unsupported_types` list in config."
        )

    @staticmethod
    def _validate_stream_statuses(configured_catalog: ConfiguredAirbyteCatalog, statuses: List[AirbyteStreamStatusTraceMessage]):
        """Validate all statuses for all streams in the catalogs were emitted in correct order:
        1. STARTED
        2. RUNNING (can be >1)
        3. COMPLETE
        """
        stream_statuses = defaultdict(list)
        for status in statuses:
            stream_statuses[f"{status.stream_descriptor.namespace}-{status.stream_descriptor.name}"].append(status.status)

        assert set(f"{x.stream.namespace}-{x.stream.name}" for x in configured_catalog.streams) == set(
            stream_statuses
        ), "All stream must emit status"

        for stream_name, status_list in stream_statuses.items():
            assert (
                len(status_list) >= 3
            ), f"Stream `{stream_name}` statuses should be emitted in the next order: `STARTED`, `RUNNING`,... `COMPLETE`"
            assert status_list[0] == AirbyteStreamStatus.STARTED
            assert status_list[-1] == AirbyteStreamStatus.COMPLETE
            assert all(x == AirbyteStreamStatus.RUNNING for x in status_list[1:-1])

    @staticmethod
    def _validate_state_messages(state_messages: List[AirbyteMessage], configured_catalog: ConfiguredAirbyteCatalog):
        # Ensure that at least one state message is emitted for each stream
        assert len(state_messages) >= len(
            configured_catalog.streams
        ), "At least one state message should be emitted for each configured stream."

        for state_message in state_messages:
            state = state_message.state
            stream_name = state.stream.stream_descriptor.name
            state_type = state.type

            # Ensure legacy state type is not emitted anymore
            assert state_type != AirbyteStateType.LEGACY, (
                f"Ensure that statuses from the {stream_name} stream are emitted using either "
                "`STREAM` or `GLOBAL` state types, as the `LEGACY` state type is now deprecated."
            )

            # Check if stats are of the correct type and present in state message
            assert isinstance(state.sourceStats, AirbyteStateStats), "Source stats should be in state message."

    @staticmethod
    def _validate_primary_keys_data_type(streams: List[ConfiguredAirbyteStream], records: List[AirbyteRecordMessage]):
        data_types_mapping = {"dict": "object", "list": "array"}
        for primary_keys, record in primary_keys_for_records(streams=streams, records=records):
            stream_name = record.stream
            non_nullable_key_part_found = False
            for primary_key_path, primary_key_value in primary_keys.items():
                if primary_key_value is not None:
                    non_nullable_key_part_found = True

                assert not isinstance(primary_key_value, (list, dict)), (
                    f"Stream {stream_name} contains primary key with forbidden type "
                    f"of '{data_types_mapping.get(primary_key_value.__class__.__name__)}'"
                )

            assert non_nullable_key_part_found, f"Stream {stream_name} contains primary key with null values in all its parts"


@pytest.mark.default_timeout(TEN_MINUTES)
class TestConnectorAttributes(BaseTest):
    # Override from BaseTest!
    # Used so that this is not part of the mandatory high strictness test suite yet
    MANDATORY_FOR_TEST_STRICTNESS_LEVELS = []

    @pytest.fixture(name="operational_certification_test")
    async def operational_certification_test_fixture(self, is_connector_certified: bool) -> bool:
        """
        Fixture that is used to skip a test that is reserved only for connectors that are supposed to be tested
        against operational certification criteria
        """

        if not is_connector_certified:
            pytest.skip("Skipping operational connector certification test for uncertified connector")
        return True

    @pytest.fixture(name="streams_without_primary_key")
    def streams_without_primary_key_fixture(self, inputs: ConnectorAttributesConfig) -> List[NoPrimaryKeyConfiguration]:
        return inputs.streams_without_primary_key or []

    async def test_streams_define_primary_key(
        self, operational_certification_test, streams_without_primary_key, connector_config, docker_runner: ConnectorRunner
    ) -> None:
        output = await docker_runner.call_discover(config=connector_config)
        catalog_messages = filter_output(output, Type.CATALOG)
        streams = catalog_messages[0].catalog.streams
        discovered_streams_without_primary_key = {stream.name for stream in streams if not stream.source_defined_primary_key}
        missing_primary_keys = discovered_streams_without_primary_key - {stream.name for stream in streams_without_primary_key}

        quoted_missing_primary_keys = {f"'{primary_key}'" for primary_key in missing_primary_keys}
        assert not missing_primary_keys, f"The following streams {', '.join(quoted_missing_primary_keys)} do not define a primary_key"

    @pytest.fixture(name="allowed_hosts_test")
    def allowed_hosts_fixture_test(self, inputs: ConnectorAttributesConfig) -> bool:
        allowed_hosts = inputs.allowed_hosts
        bypass_reason = allowed_hosts.bypass_reason if allowed_hosts else None
        if bypass_reason:
            pytest.skip(f"Skipping `metadata.allowedHosts` checks. Reason: {bypass_reason}")
        return True

    async def test_certified_connector_has_allowed_hosts(
        self, operational_certification_test, allowed_hosts_test, connector_metadata: dict
    ) -> None:
        """
        Checks whether or not the connector has `allowedHosts` and it's components defined in `metadata.yaml`.
        Suitable for certified connectors starting `ql` >= 400.

        Arguments:
            :: operational_certification_test -- pytest.fixure defines the connector is suitable for this test or not.
            :: connector_metadata -- `metadata.yaml` file content
        """
        metadata = connector_metadata.get("data", {})

        has_allowed_hosts_property = "allowedHosts" in metadata.keys()
        assert has_allowed_hosts_property, f"The `allowedHosts` property is missing in `metadata.data` for `metadata.yaml`."

        allowed_hosts = metadata.get("allowedHosts", {})
        has_hosts_property = "hosts" in allowed_hosts.keys() if allowed_hosts else False
        assert has_hosts_property, f"The `hosts` property is missing in `metadata.data.allowedHosts` for `metadata.yaml`."

        hosts = allowed_hosts.get("hosts", [])
        has_assigned_hosts = len(hosts) > 0 if hosts else False
        assert (
            has_assigned_hosts
        ), f"The `hosts` empty list is not allowed for `metadata.data.allowedHosts` for certified connectors. Please add `hosts` or define the `allowed_hosts.bypass_reason` in `acceptance-test-config.yaml`."

    @pytest.fixture(name="suggested_streams_test")
    def suggested_streams_fixture_test(self, inputs: ConnectorAttributesConfig) -> bool:
        suggested_streams = inputs.suggested_streams
        bypass_reason = suggested_streams.bypass_reason if suggested_streams else None
        if bypass_reason:
            pytest.skip(f"Skipping `metadata.suggestedStreams` checks. Reason: {bypass_reason}")
        return True

    async def test_certified_connector_has_suggested_streams(
        self, operational_certification_test, suggested_streams_test, connector_metadata: dict
    ) -> None:
        """
        Checks whether or not the connector has `suggestedStreams` and it's components defined in `metadata.yaml`.
        Suitable for certified connectors starting `ql` >= 400.

        Arguments:
            :: operational_certification_test -- pytest.fixure defines the connector is suitable for this test or not.
            :: connector_metadata -- `metadata.yaml` file content
        """

        metadata = connector_metadata.get("data", {})

        has_suggested_streams_property = "suggestedStreams" in metadata.keys()
        assert has_suggested_streams_property, f"The `suggestedStreams` property is missing in `metadata.data` for `metadata.yaml`."

        suggested_streams = metadata.get("suggestedStreams", {})
        has_streams_property = "streams" in suggested_streams.keys() if suggested_streams else False
        assert has_streams_property, f"The `streams` property is missing in `metadata.data.suggestedStreams` for `metadata.yaml`."

        streams = suggested_streams.get("streams", [])
        has_assigned_suggested_streams = len(streams) > 0 if streams else False
        assert (
            has_assigned_suggested_streams
        ), f"The `streams` empty list is not allowed for `metadata.data.suggestedStreams` for certified connectors."


class TestConnectorDocumentation(BaseTest):
    MANDATORY_FOR_TEST_STRICTNESS_LEVELS = []  # Used so that this is not part of the mandatory high strictness test suite yet

    PREREQUISITES = "Prerequisites"
    HEADING = "heading"
    CREDENTIALS_KEYWORDS = ["account", "auth", "credentials", "access"]
    CONNECTOR_SPECIFIC_HEADINGS = "<Connector-specific features>"

    @pytest.fixture(name="operational_certification_test")
    async def operational_certification_test_fixture(self, is_connector_certified: bool) -> bool:
        """
        Fixture that is used to skip a test that is reserved only for connectors that are supposed to be tested
        against operational certification criteria
        """
        if not is_connector_certified:
            pytest.skip("Skipping testing source connector documentation due to low ql.")
        return True

    def _get_template_headings(self, connector_name: str) -> tuple[tuple[str], tuple[str]]:
        """
        https://hackmd.io/Bz75cgATSbm7DjrAqgl4rw - standard template
        Headings in order to docs structure.
        """
        all_headings = (
            connector_name,
            "Prerequisites",
            "Setup guide",
            f"Set up {connector_name}",
            "For Airbyte Cloud:",
            "For Airbyte Open Source:",
            f"Set up the {connector_name} connector in Airbyte",
            "For Airbyte Cloud:",
            "For Airbyte Open Source:",
            "Supported sync modes",
            "Supported Streams",
            self.CONNECTOR_SPECIFIC_HEADINGS,
            "Performance considerations",
            "Data type map",
            "Troubleshooting",
            "Tutorials",
            "Changelog",
        )
        not_required_heading = (
            f"Set up the {connector_name} connector in Airbyte",
            "For Airbyte Cloud:",
            "For Airbyte Open Source:",
            self.CONNECTOR_SPECIFIC_HEADINGS,
            "Performance considerations",
            "Data type map",
            "Troubleshooting",
            "Tutorials",
        )
        return all_headings, not_required_heading

    def _headings_description(self, connector_name: str) -> dict[str:Path]:
        """
        Headings with path to file with template description
        """
        descriptions_paths = {
            connector_name: Path(__file__).parent / "doc_templates/source.txt",
            "For Airbyte Cloud:": Path(__file__).parent / "doc_templates/for_airbyte_cloud.txt",
            "For Airbyte Open Source:": Path(__file__).parent / "doc_templates/for_airbyte_open_source.txt",
            "Supported sync modes": Path(__file__).parent / "doc_templates/supported_sync_modes.txt",
            "Tutorials": Path(__file__).parent / "doc_templates/tutorials.txt",
        }
        return descriptions_paths

    def test_prerequisites_content(
        self, operational_certification_test, actual_connector_spec: ConnectorSpecification, connector_documentation: str, docs_path: str
    ):
        node = docs_utils.documentation_node(connector_documentation)
        header_line_map = {docs_utils.header_name(n): n.map[1] for n in node if n.type == self.HEADING}
        headings = tuple(header_line_map.keys())

        if not header_line_map.get(self.PREREQUISITES):
            pytest.fail(f"Documentation does not have {self.PREREQUISITES} section.")

        prereq_start_line = header_line_map[self.PREREQUISITES]
        prereq_end_line = docs_utils.description_end_line_index(self.PREREQUISITES, headings, header_line_map)

        with open(docs_path, "r") as docs_file:
            prereq_content_lines = docs_file.readlines()[prereq_start_line:prereq_end_line]
            # adding real character to avoid accidentally joining lines into a wanted title.
            prereq_content = "|".join(prereq_content_lines).lower()
            required_titles, has_credentials = docs_utils.required_titles_from_spec(actual_connector_spec.connectionSpecification)

            for title in required_titles:
                assert title in prereq_content, (
                    f"Required '{title}' field is not in {self.PREREQUISITES} section " f"or title in spec doesn't match name in the docs."
                )

            if has_credentials:
                # credentials has specific check for keywords as we have a lot of way how to describe this step
                credentials_validation = [k in prereq_content for k in self.CREDENTIALS_KEYWORDS]
                assert True in credentials_validation, f"Required 'credentials' field is not in {self.PREREQUISITES} section."

    def test_docs_structure(self, operational_certification_test, connector_documentation: str, connector_metadata: dict):
        """
        test_docs_structure gets all top-level headers from source documentation file and check that the order is correct.
        The order of the headers should follow our standard template https://hackmd.io/Bz75cgATSbm7DjrAqgl4rw.
        _get_template_headings returns tuple of headers as in standard template and non-required headers that might nor be in the source docs.
        CONNECTOR_SPECIFIC_HEADINGS value in list of required headers that shows a place where should be a connector specific headers,
        which can be skipped as out of standard template and depend of connector.
        """

        heading_names = docs_utils.prepare_headers(connector_documentation)
        template_headings, non_required_heading = self._get_template_headings(connector_metadata["data"]["name"])

        heading_names_len, template_headings_len = len(heading_names), len(template_headings)
        heading_names_index, template_headings_index = 0, 0

        while heading_names_index < heading_names_len and template_headings_index < template_headings_len:
            heading_names_value = heading_names[heading_names_index]
            template_headings_value = template_headings[template_headings_index]
            # check that template header is specific for connector and actual header should not be validated
            if template_headings_value == self.CONNECTOR_SPECIFIC_HEADINGS:
                # check that actual header is not in required headers, as required headers should be on a right place and order
                if heading_names_value not in template_headings:
                    heading_names_index += 1  # go to the next actual header as CONNECTOR_SPECIFIC_HEADINGS can be more than one
                    continue
                else:
                    # if actual header is required go to the next template header to validate actual header order
                    template_headings_index += 1
                    continue
            # strict check that actual header equals template header
            if heading_names_value == template_headings_value:
                # found expected header, go to the next header in template and actual headers
                heading_names_index += 1
                template_headings_index += 1
                continue
            # actual header != template header means that template value is not required and can be skipped
            if template_headings_value in non_required_heading:
                # found non-required header, go to the next template header to validate actual header
                template_headings_index += 1
                continue
            # any check is True, indexes didn't move to the next step
            pytest.fail(docs_utils.reason_titles_not_match(heading_names_value, template_headings_value, template_headings))
        # indexes didn't move to the last required one, so some headers are missed
        if template_headings_index != template_headings_len:
            pytest.fail(docs_utils.reason_missing_titles(template_headings_index, template_headings))

    def test_docs_descriptions(
        self, operational_certification_test, docs_path: str, connector_documentation: str, connector_metadata: dict
    ):
        connector_name = connector_metadata["data"]["name"]
        template_descriptions = self._headings_description(connector_name)

        node = docs_utils.documentation_node(connector_documentation)
        header_line_map = {docs_utils.header_name(n): n.map[1] for n in node if n.type == self.HEADING}
        actual_headings = tuple(header_line_map.keys())

        for heading, description in template_descriptions.items():
            if heading in actual_headings:

                description_start_line = header_line_map[heading]
                description_end_line = docs_utils.description_end_line_index(heading, actual_headings, header_line_map)

                with open(docs_path, "r") as docs_file, open(description, "r") as template_file:

                    docs_description_content = docs_file.readlines()[description_start_line:description_end_line]
                    template_description_content = template_file.readlines()

                    for d, t in zip(docs_description_content, template_description_content):
                        d, t = docs_utils.prepare_lines_to_compare(connector_name, d, t)
                        assert d == t, f"Description for '{heading}' does not follow structure.\nExpected: {t} Actual: {d}"

    def test_validate_links(self, operational_certification_test, connector_documentation: str):
        valid_status_codes = [200, 403, 401, 405]  # we skip 4xx due to needed access
        links = re.findall("(https?://[^\s)]+)", connector_documentation)
        invalid_links = []
        threads = []

        def validate_docs_links(docs_link):
            response = requests.get(docs_link)
            if response.status_code not in valid_status_codes:
                invalid_links.append(docs_link)

        for link in links:
            process = Thread(target=validate_docs_links, args=[link])
            process.start()
            threads.append(process)

        for process in threads:
            process.join(timeout=30)  # 30s timeout for process else link will be skipped
            process.is_alive()

        assert not invalid_links, f"{len(invalid_links)} invalid links were found in the connector documentation: {invalid_links}."
