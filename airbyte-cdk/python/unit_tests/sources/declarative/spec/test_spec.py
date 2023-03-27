#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.models.airbyte_protocol import AdvancedAuth, ConnectorSpecification
from airbyte_cdk.sources.declarative.models.declarative_component_schema import AuthFlow
from airbyte_cdk.sources.declarative.spec.spec import Spec


@pytest.mark.parametrize(
    "test_name, spec, expected_connection_specification",
    [
        ("test_only_connection_specification", Spec(connection_specification={"client_id": "my_client_id"}, parameters={}), ConnectorSpecification(connectionSpecification={"client_id": "my_client_id"})),
        ("test_with_doc_url", Spec(connection_specification={"client_id": "my_client_id"}, parameters={}, documentation_url="https://airbyte.io"), ConnectorSpecification(connectionSpecification={"client_id": "my_client_id"}, documentationUrl="https://airbyte.io")),
        ("test_auth_flow", Spec(connection_specification={"client_id": "my_client_id"}, parameters={}, advanced_auth=AuthFlow(auth_flow_type="oauth2.0")), ConnectorSpecification(connectionSpecification={"client_id": "my_client_id"}, advanced_auth=AdvancedAuth(auth_flow_type="oauth2.0"))),
    ],
)
def test_spec(test_name, spec, expected_connection_specification):
    assert spec.generate_spec() == expected_connection_specification
