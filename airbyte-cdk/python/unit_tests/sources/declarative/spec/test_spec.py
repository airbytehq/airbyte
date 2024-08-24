#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.models import AdvancedAuth, AuthFlowType, ConnectorSpecification
from airbyte_cdk.sources.declarative.models.declarative_component_schema import AuthFlow
from airbyte_cdk.sources.declarative.spec.spec import Spec


@pytest.mark.parametrize(
    "spec, expected_connection_specification",
    [
        (
            Spec(connection_specification={"client_id": "my_client_id"}, parameters={}),
            ConnectorSpecification(connectionSpecification={"client_id": "my_client_id"}),
        ),
        (
            Spec(connection_specification={"client_id": "my_client_id"}, parameters={}, documentation_url="https://airbyte.io"),
            ConnectorSpecification(connectionSpecification={"client_id": "my_client_id"}, documentationUrl="https://airbyte.io"),
        ),
        (
            Spec(connection_specification={"client_id": "my_client_id"}, parameters={}, advanced_auth=AuthFlow(auth_flow_type="oauth2.0")),
            ConnectorSpecification(
                connectionSpecification={"client_id": "my_client_id"}, advanced_auth=AdvancedAuth(auth_flow_type=AuthFlowType.oauth2_0)
            ),
        ),
    ],
    ids=[
        "test_only_connection_specification",
        "test_with_doc_url",
        "test_auth_flow",
    ],
)
def test_spec(spec, expected_connection_specification):
    assert spec.generate_spec() == expected_connection_specification
