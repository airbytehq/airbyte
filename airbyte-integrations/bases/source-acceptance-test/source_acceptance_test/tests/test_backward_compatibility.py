#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import pytest
from airbyte_cdk.models import ConnectorSpecification
from deepdiff import DeepDiff
from source_acceptance_test.base import BaseTest
from source_acceptance_test.config import SpecTestConfig


@pytest.mark.default_timeout(60)
@pytest.mark.backward_compatibility
class TestSpecBackwardCompatibility(BaseTest):
    @staticmethod
    def compute_spec_diff(actual_connector_spec: ConnectorSpecification, previous_connector_spec: ConnectorSpecification):
        return DeepDiff(previous_connector_spec.dict(), actual_connector_spec.dict(), view="tree")

    @pytest.fixture(scope="class")
    def spec_diff(
        self, inputs: SpecTestConfig, actual_connector_spec: ConnectorSpecification, previous_connector_spec: ConnectorSpecification
    ) -> DeepDiff:
        if not inputs.backward_compatibility_tests_config.run_backward_compatibility_tests:
            pytest.skip("Backward compatibility tests are disabled.")
        if previous_connector_spec is None:
            pytest.skip("The previous connector spec could not be retrieved.")
        assert isinstance(actual_connector_spec, ConnectorSpecification) and isinstance(previous_connector_spec, ConnectorSpecification)
        return self.compute_spec_diff(actual_connector_spec, previous_connector_spec)

    def test_new_required_field_declaration(self, spec_diff):
        added_required_fields = [
            addition for addition in spec_diff.get("dictionary_item_added", []) if addition.path(output_format="list")[-1] == "required"
        ]
        assert len(added_required_fields) == 0, f"The current spec has a new required field: {spec_diff.pretty()}"

    def test_new_required_property(self, spec_diff):
        added_required_properties = [
            addition for addition in spec_diff.get("iterable_item_added", []) if addition.up.path(output_format="list")[-1] == "required"
        ]
        assert len(added_required_properties) == 0, f"The current spec has a new required property: {spec_diff.pretty()}"

    def test_type_field_changed_from_list_to_string(self, spec_diff):
        type_changes = [
            type_change for type_change in spec_diff.get("type_changes", []) if type_change.path(output_format="list")[-1] == "type"
        ]
        for type_change in type_changes:
            if isinstance(type_change.t1, list) and isinstance(type_change.t2, str):
                raise AssertionError(f"The current spec narrowed a field type: {spec_diff.pretty()}")

    def test_type_field_has_narrowed(self, spec_diff):
        removals = [
            removal for removal in spec_diff.get("iterable_item_removed", []) if removal.up.path(output_format="list")[-1] == "type"
        ]
        assert len(removals) == 0, f"The current spec narrowed a field type: {spec_diff.pretty()}"

    def test_enum_field_has_narrowed(self, spec_diff):
        removals = [
            removal for removal in spec_diff.get("iterable_item_removed", []) if removal.up.path(output_format="list")[-1] == "enum"
        ]
        assert len(removals) == 0, f"The current spec narrowed a field enum: {spec_diff.pretty()}"

    def test_new_enum_field_declaration(self, spec_diff):
        added_enum_fields = [
            addition for addition in spec_diff.get("dictionary_item_added", []) if addition.path(output_format="list")[-1] == "enum"
        ]
        assert len(added_enum_fields) == 0, f"The current spec has a new enum field: {spec_diff.pretty()}"
