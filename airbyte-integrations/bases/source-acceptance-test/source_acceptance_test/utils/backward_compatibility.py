#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import jsonschema
from airbyte_cdk.models import ConnectorSpecification
from deepdiff import DeepDiff
from hypothesis import given, settings
from hypothesis_jsonschema import from_schema
from source_acceptance_test.utils import SecretDict


class NonBackwardCompatibleSpecError(Exception):
    pass


class SpecDiffChecker:
    """A class to perform multiple backward compatible checks on a spec diff"""

    def __init__(self, diff: DeepDiff) -> None:
        self._diff = diff

    def assert_spec_is_backward_compatible(self):
        self.check_if_declared_new_required_field()
        self.check_if_added_a_new_required_property()
        self.check_if_value_of_type_field_changed()
        # self.check_if_new_type_was_added() We want to allow type expansion atm
        self.check_if_type_of_type_field_changed()
        self.check_if_field_was_made_not_nullable()
        self.check_if_enum_was_narrowed()
        self.check_if_declared_new_enum_field()

    def _raise_error(self, message: str):
        raise NonBackwardCompatibleSpecError(f"{message}: {self._diff.pretty()}")

    def check_if_declared_new_required_field(self):
        """Check if the new spec declared a 'required' field."""
        added_required_fields = [
            addition for addition in self._diff.get("dictionary_item_added", []) if addition.path(output_format="list")[-1] == "required"
        ]
        if added_required_fields:
            self._raise_error("The current spec declared a new 'required' field")

    def check_if_added_a_new_required_property(self):
        """Check if the new spec added a property to the 'required' list."""
        added_required_properties = [
            addition for addition in self._diff.get("iterable_item_added", []) if addition.up.path(output_format="list")[-1] == "required"
        ]
        if added_required_properties:
            self._raise_error("A new property was added to 'required'")

    def check_if_value_of_type_field_changed(self):
        """Check if a type was changed"""
        # Detect type value change in case type field is declared as a string (e.g "str" -> "int"):
        type_values_changed = [change for change in self._diff.get("values_changed", []) if change.path(output_format="list")[-1] == "type"]

        # Detect type value change in case type field is declared as a single item list (e.g ["str"] -> ["int"]):
        type_values_changed_in_list = [
            change for change in self._diff.get("values_changed", []) if change.path(output_format="list")[-2] == "type"
        ]
        if type_values_changed or type_values_changed_in_list:
            self._raise_error("The current spec changed the value of a 'type' field")

    def check_if_new_type_was_added(self):
        """Detect type value added to type list if new type value is not None (e.g ["str"] -> ["str", "int"])"""
        new_values_in_type_list = [
            change
            for change in self._diff.get("iterable_item_added", [])
            if change.path(output_format="list")[-2] == "type"
            if change.t2 != "null"
        ]
        if new_values_in_type_list:
            self._raise_error("The current spec changed the value of a 'type' field")

    def check_if_type_of_type_field_changed(self):
        """
        Detect the change of type of a type field
        e.g:
        - "str" -> ["str"] VALID
        - "str" -> ["str", "null"] VALID
        - "str" -> ["str", "int"] VALID
        - "str" -> 1 INVALID
        - ["str"] -> "str" VALID
        - ["str"] -> "int" INVALID
        - ["str"] -> 1 INVALID
        """
        type_changes = [change for change in self._diff.get("type_changes", []) if change.path(output_format="list")[-1] == "type"]
        for change in type_changes:
            # We only accept change on the type field if the new type for this field is list or string
            # This might be something already guaranteed by JSON schema validation.
            if isinstance(change.t1, str):
                if not isinstance(change.t2, list):
                    self._raise_error("The current spec change a type field from string to an invalid value.")
                if not 0 < len(change.t2) <= 2:
                    self._raise_error(
                        "The current spec change a type field from string to an invalid value. The type list length should not be empty and have a maximum of two items."
                    )
                # If the new type field is a list we want to make sure it only has the original type (t1) and null: e.g. "str" -> ["str", "null"]
                # We want to raise an error otherwise.
                t2_not_null_types = [_type for _type in change.t2 if _type != "null"]
                if not (len(t2_not_null_types) == 1 and t2_not_null_types[0] == change.t1):
                    self._raise_error("The current spec change a type field to a list with multiple invalid values.")
            if isinstance(change.t1, list):
                if not isinstance(change.t2, str):
                    self._raise_error("The current spec change a type field from list to an invalid value.")
                if not (len(change.t1) == 1 and change.t2 == change.t1[0]):
                    self._raise_error("The current spec narrowed a field type.")

    def check_if_field_was_made_not_nullable(self):
        """Detect when field was made not nullable but is still a list: e.g ["string", "null"] -> ["string"]"""
        removed_nullable = [
            change for change in self._diff.get("iterable_item_removed", []) if change.path(output_format="list")[-2] == "type"
        ]
        if removed_nullable:
            self._raise_error("The current spec narrowed a field type or made a field not nullable.")

    def check_if_enum_was_narrowed(self):
        """Check if the list of values in a enum was shortened in a spec."""
        enum_removals = [
            enum_removal
            for enum_removal in self._diff.get("iterable_item_removed", [])
            if enum_removal.up.path(output_format="list")[-1] == "enum"
        ]
        if enum_removals:
            self._raise_error("The current spec narrowed an enum field.")

    def check_if_declared_new_enum_field(self):
        """Check if an 'enum' field was added to the spec."""
        enum_additions = [
            enum_addition
            for enum_addition in self._diff.get("dictionary_item_added", [])
            if enum_addition.path(output_format="list")[-1] == "enum"
        ]
        if enum_additions:
            self._raise_error("An 'enum' field was declared on an existing property of the spec.")


def validate_previous_configs(
    previous_connector_spec: ConnectorSpecification, actual_connector_spec: ConnectorSpecification, number_of_configs_to_generate=100
):
    """Use hypothesis and hypothesis-jsonschema to run property based testing:
    1. Generate fake previous config with the previous connector specification json schema.
    2. Validate a fake previous config against the actual connector specification json schema."""

    @given(from_schema(previous_connector_spec.dict()["connectionSpecification"]))
    @settings(max_examples=number_of_configs_to_generate)
    def check_fake_previous_config_against_actual_spec(fake_previous_config):
        fake_previous_config = SecretDict(fake_previous_config)
        filtered_fake_previous_config = {key: value for key, value in fake_previous_config.data.items() if not key.startswith("_")}
        try:
            jsonschema.validate(instance=filtered_fake_previous_config, schema=actual_connector_spec.connectionSpecification)
        except jsonschema.exceptions.ValidationError as err:
            raise NonBackwardCompatibleSpecError(err)

    check_fake_previous_config_against_actual_spec()
