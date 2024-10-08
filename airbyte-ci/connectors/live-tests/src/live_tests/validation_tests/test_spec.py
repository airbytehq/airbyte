#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Set, Tuple

import dpath.util
import jsonschema
import pytest
from airbyte_protocol.models import ConnectorSpecification
from live_tests.commons.json_schema_helper import JsonSchemaHelper, get_expected_schema_structure, get_paths_in_connector_config
from live_tests.commons.models import ExecutionResult, SecretDict
from live_tests.utils import fail_test_on_failing_execution_results, find_all_values_for_key_in_schema, get_test_logger

pytestmark = [
    pytest.mark.anyio,
]

if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest


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


async def test_spec(
    record_property: Callable,
    spec_target_execution_result: ExecutionResult,
):
    """Check that the spec call succeeds"""
    fail_test_on_failing_execution_results(record_property, [spec_target_execution_result])


@pytest.mark.allow_diagnostic_mode
async def test_config_match_spec(
    target_spec: ConnectorSpecification,
    connector_config: Optional[SecretDict],
):
    """Check that config matches the actual schema from the spec call"""
    # Getting rid of technical variables that start with an underscore
    config = {key: value for key, value in connector_config.data.items() if not key.startswith("_")}
    try:
        jsonschema.validate(instance=config, schema=target_spec.connectionSpecification)
    except jsonschema.exceptions.ValidationError as err:
        pytest.fail(f"Config invalid: {err}")
    except jsonschema.exceptions.SchemaError as err:
        pytest.fail(f"Spec is invalid: {err}")


async def test_enum_usage(target_spec: ConnectorSpecification):
    """Check that enum lists in specs contain distinct values."""
    docs_url = "https://docs.airbyte.io/connector-development/connector-specification-reference"
    docs_msg = f"See specification reference at {docs_url}."

    schema_helper = JsonSchemaHelper(target_spec.connectionSpecification)
    enum_paths = schema_helper.find_nodes(keys=["enum"])

    for path in enum_paths:
        enum_list = schema_helper.get_node(path)
        assert len(set(enum_list)) == len(
            enum_list
        ), f"Enum lists should not contain duplicate values. Misconfigured enum array: {enum_list}. {docs_msg}"


async def test_oneof_usage(target_spec: ConnectorSpecification):
    """Check that if spec contains oneOf it follows the rules according to reference
    https://docs.airbyte.io/connector-development/connector-specification-reference
    """
    docs_url = "https://docs.airbyte.io/connector-development/connector-specification-reference"
    docs_msg = f"See specification reference at {docs_url}."

    schema_helper = JsonSchemaHelper(target_spec.connectionSpecification)
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
        enum_common_props = set()
        for common_prop in common_props:
            if all(["const" in variant["properties"][common_prop] for variant in variants]):
                const_common_props.add(common_prop)
            if all(["enum" in variant["properties"][common_prop] for variant in variants]):
                enum_common_props.add(common_prop)
        assert len(const_common_props) == 1 or (
            len(const_common_props) == 0 and len(enum_common_props) == 1
        ), f"There should be exactly one common property with 'const' keyword (or equivalent) for {oneof_path} subobjects. {docs_msg}"

        const_common_prop = const_common_props.pop() if const_common_props else enum_common_props.pop()
        for n, variant in enumerate(variants):
            prop_obj = variant["properties"][const_common_prop]
            prop_info = f"common property {oneof_path}[{n}].{const_common_prop}. It's recommended to just use `const`."
            if "const" in prop_obj:
                const_value = prop_obj["const"]
                assert (
                    "default" not in prop_obj or prop_obj["default"] == const_value
                ), f"'default' needs to be identical to 'const' in {prop_info}. {docs_msg}"
                assert "enum" not in prop_obj or prop_obj["enum"] == [
                    const_value
                ], f"'enum' needs to be an array with a single item identical to 'const' in {prop_info}. {docs_msg}"
            else:
                assert (
                    "enum" in prop_obj and "default" in prop_obj and prop_obj["enum"] == [prop_obj["default"]]
                ), f"'enum' needs to be an array with a single item identical to 'default' in {prop_info}. {docs_msg}"


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


async def test_secret_is_properly_marked(target_spec: ConnectorSpecification, secret_property_names):
    """
    Each field has a type, therefore we can make a flat list of fields from the returned specification.
    Iterate over the list, check if a field name is a secret name, can potentially hold a secret value
    and make sure it is marked as `airbyte_secret`.
    """
    secrets_exposed = []
    non_secrets_hidden = []
    spec_properties = target_spec.connectionSpecification["properties"]
    for type_path, type_value in dpath.util.search(spec_properties, "**/type", yielded=True):
        _, is_property_name_secret = _is_spec_property_name_secret(type_path, secret_property_names)
        if not is_property_name_secret:
            continue
        absolute_path = f"/{type_path}"
        property_path, _ = absolute_path.rsplit(sep="/", maxsplit=1)
        property_definition = dpath.util.get(spec_properties, property_path)
        marked_as_secret = property_definition.get("airbyte_secret", False)
        possibly_a_secret = _property_can_store_secret(property_definition)
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


def _fail_on_errors(errors: List[str]):
    if len(errors) > 0:
        pytest.fail("\n".join(errors))


def test_property_type_is_not_array(target_spec: ConnectorSpecification):
    """
    Each field has one or multiple types, but the UI only supports a single type and optionally "null" as a second type.
    """
    errors = []
    for type_path, type_value in dpath.util.search(target_spec.connectionSpecification, "**/properties/*/type", yielded=True):
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
    _fail_on_errors(errors)


def test_object_not_empty(target_spec: ConnectorSpecification):
    """
    Each object field needs to have at least one property as the UI won't be able to show them otherwise.
    If the whole spec is empty, it's allowed to have a single empty object at the top level
    """
    schema_helper = JsonSchemaHelper(target_spec.connectionSpecification)
    errors = []
    for type_path, type_value in dpath.util.search(target_spec.connectionSpecification, "**/type", yielded=True):
        if type_path == "type":
            # allow empty root object
            continue
        if type_value == "object":
            property = schema_helper.get_parent(type_path)
            if "oneOf" not in property and ("properties" not in property or len(property["properties"]) == 0):
                errors.append(
                    f"{type_path} is an empty object which will not be represented correctly in the UI. Either remove or add specific properties"
                )
    _fail_on_errors(errors)


async def test_array_type(target_spec: ConnectorSpecification):
    """
    Each array has one or multiple types for its items, but the UI only supports a single type which can either be object, string or an enum
    """
    schema_helper = JsonSchemaHelper(target_spec.connectionSpecification)
    errors = []
    for type_path, type_type in dpath.util.search(target_spec.connectionSpecification, "**/type", yielded=True):
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
    _fail_on_errors(errors)


async def test_forbidden_complex_types(target_spec: ConnectorSpecification):
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
        for path, value in dpath.util.search(target_spec.connectionSpecification, f"**/{forbidden_key}", yielded=True):
            found_keys.add(path)

    for forbidden_key in forbidden_keys:
        # remove forbidden keys if they are used as properties directly
        for path, _value in dpath.util.search(target_spec.connectionSpecification, f"**/properties/{forbidden_key}", yielded=True):
            found_keys.remove(path)

    if len(found_keys) > 0:
        key_list = ", ".join(found_keys)
        pytest.fail(f"Found the following disallowed JSON schema features: {key_list}")


async def test_date_pattern(request: "SubRequest", target_spec: ConnectorSpecification):
    """
    Properties with format date or date-time should always have a pattern defined how the date/date-time should be formatted
    that corresponds with the format the datepicker component is creating.
    """
    schema_helper = JsonSchemaHelper(target_spec.connectionSpecification)
    for format_path, format in dpath.util.search(target_spec.connectionSpecification, "**/format", yielded=True):
        if not isinstance(format, str):
            # format is not a format definition here but a property named format
            continue
        property_definition = schema_helper.get_parent(format_path)
        pattern = property_definition.get("pattern")
        logger = get_test_logger(request)
        if format == "date" and not pattern == DATE_PATTERN:
            logger.warning(
                f"{format_path} is defining a date format without the corresponding pattern. Consider setting the pattern to {DATE_PATTERN} to make it easier for users to edit this field in the UI."
            )
        if format == "date-time" and not pattern == DATETIME_PATTERN:
            logger.warning(
                f"{format_path} is defining a date-time format without the corresponding pattern Consider setting the pattern to {DATETIME_PATTERN} to make it easier for users to edit this field in the UI."
            )


async def test_date_format(request: "SubRequest", target_spec: ConnectorSpecification):
    """
    Properties with a pattern that looks like a date should have their format set to date or date-time.
    """
    schema_helper = JsonSchemaHelper(target_spec.connectionSpecification)
    for pattern_path, pattern in dpath.util.search(target_spec.connectionSpecification, "**/pattern", yielded=True):
        if not isinstance(pattern, str):
            # pattern is not a pattern definition here but a property named pattern
            continue
        if pattern == DATE_PATTERN or pattern == DATETIME_PATTERN:
            property_definition = schema_helper.get_parent(pattern_path)
            format = property_definition.get("format")
            logger = get_test_logger(request)
            if not format == "date" and pattern == DATE_PATTERN:
                logger.warning(
                    f"{pattern_path} is defining a pattern that looks like a date without setting the format to `date`. Consider specifying the format to make it easier for users to edit this field in the UI."
                )
            if not format == "date-time" and pattern == DATETIME_PATTERN:
                logger.warning(
                    f"{pattern_path} is defining a pattern that looks like a date-time without setting the format to `date-time`. Consider specifying the format to make it easier for users to edit this field in the UI."
                )


async def test_duplicate_order(target_spec: ConnectorSpecification):
    """
    Custom ordering of field (via the "order" property defined in the field) is not allowed to have duplicates within the same group.
    `{ "a": { "order": 1 }, "b": { "order": 1 } }` is invalid because there are two fields with order 1
    `{ "a": { "order": 1 }, "b": { "order": 1, "group": "x" } }` is valid because the fields with the same order are in different groups
    """
    schema_helper = JsonSchemaHelper(target_spec.connectionSpecification)
    errors = []
    for properties_path, properties in dpath.util.search(target_spec.connectionSpecification, "**/properties", yielded=True):
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
    _fail_on_errors(errors)


async def test_nested_group(target_spec: ConnectorSpecification):
    """
    Groups can only be defined on the top level properties
    `{ "a": { "group": "x" }}` is valid because field "a" is a top level field
    `{ "a": { "oneOf": [{ "type": "object", "properties": { "b": { "group": "x" } } }] }}` is invalid because field "b" is nested in a oneOf
    """
    errors = []
    schema_helper = JsonSchemaHelper(target_spec.connectionSpecification)
    for result in dpath.util.search(target_spec.connectionSpecification, "/properties/**/group", yielded=True):
        group_path = result[0]
        parent_path = schema_helper.get_parent_path(group_path)
        is_property_named_group = parent_path.endswith("properties")
        grandparent_path = schema_helper.get_parent_path(parent_path)
        if grandparent_path != "/properties" and not is_property_named_group:
            errors.append(f"Groups can only be defined on top level, is defined at {group_path}")
    _fail_on_errors(errors)


async def test_display_type(target_spec: ConnectorSpecification):
    """
    The display_type property can only be set on fields which have a oneOf property, and must be either "dropdown" or "radio"
    """
    errors = []
    schema_helper = JsonSchemaHelper(target_spec.connectionSpecification)
    for result in dpath.util.search(target_spec.connectionSpecification, "/properties/**/display_type", yielded=True):
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
            errors.append(f"display_type must be either 'dropdown' or 'radio', but is set to '{display_type_value}' at {display_type_path}")
    _fail_on_errors(errors)


async def test_defined_refs_exist_in_json_spec_file(target_spec: ConnectorSpecification):
    """Checking for the presence of unresolved `$ref`s values within each json spec file"""
    check_result = list(find_all_values_for_key_in_schema(target_spec.connectionSpecification["properties"], "$ref"))
    assert not check_result, "Found unresolved `$refs` value in spec.json file"


async def test_oauth_flow_parameters(target_spec: ConnectorSpecification):
    """Check if connector has correct oauth flow parameters according to
    https://docs.airbyte.io/connector-development/connector-specification-reference
    """
    advanced_auth = target_spec.advanced_auth
    if not advanced_auth:
        return
    spec_schema = target_spec.connectionSpecification
    paths_to_validate = set()
    if advanced_auth.predicate_key:
        paths_to_validate.add("/" + "/".join(advanced_auth.predicate_key))
    oauth_config_specification = advanced_auth.oauth_config_specification
    if oauth_config_specification:
        if oauth_config_specification.oauth_user_input_from_connector_config_specification:
            paths_to_validate.update(
                get_paths_in_connector_config(oauth_config_specification.oauth_user_input_from_connector_config_specification["properties"])
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


async def test_oauth_is_default_method(target_spec: ConnectorSpecification):
    """
    OAuth is default check.
    If credentials do have oneOf: we check that the OAuth is listed at first.
    If there is no oneOf and Oauth: OAuth is only option to authenticate the source and no check is needed.
    """
    advanced_auth = target_spec.advanced_auth
    if not advanced_auth:
        pytest.skip("Source does not have OAuth method.")
    if not advanced_auth.predicate_key:
        pytest.skip("Advanced Auth object does not have predicate_key, only one option to authenticate.")

    spec_schema = target_spec.connectionSpecification
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


async def test_additional_properties_is_true(target_spec: ConnectorSpecification):
    """Check that value of the "additionalProperties" field is always true.
    A spec declaring "additionalProperties": false introduces the risk of accidental breaking changes.
    Specifically, when removing a property from the spec, existing connector configs will no longer be valid.
    False value introduces the risk of accidental breaking changes.
    Read https://github.com/airbytehq/airbyte/issues/14196 for more details"""
    additional_properties_values = find_all_values_for_key_in_schema(target_spec.connectionSpecification, "additionalProperties")
    if additional_properties_values:
        assert all(
            [additional_properties_value is True for additional_properties_value in additional_properties_values]
        ), "When set, additionalProperties field value must be true for backward compatibility."
