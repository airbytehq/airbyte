#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_api_client.api import (
    destination_definition_api,
    destination_definition_specification_api,
    source_definition_api,
    source_definition_specification_api,
)
from airbyte_api_client.exceptions import ApiException
from airbyte_api_client.model.destination_definition_id_request_body import DestinationDefinitionIdRequestBody
from airbyte_api_client.model.source_definition_id_request_body import SourceDefinitionIdRequestBody
from octavia_cli.generate.definitions import (
    BaseDefinition,
    DefinitionNotFoundError,
    DefinitionSpecification,
    DestinationDefinition,
    DestinationDefinitionSpecification,
    SourceDefinition,
    SourceDefinitionSpecification,
    factory,
)


class TestBaseDefinition:
    @pytest.fixture
    def patch_base_class(self, mocker):
        # Mock abstract methods to enable instantiating abstract class
        mocker.patch.object(BaseDefinition, "__abstractmethods__", set())
        mocker.patch.object(BaseDefinition, "api", mocker.Mock())
        mocker.patch.object(BaseDefinition, "get_function_name", "foo")

    def test_init(self, patch_base_class, mock_api_client, mocker):
        mocker.patch.object(BaseDefinition, "_read", mocker.Mock())
        base_definition = BaseDefinition(mock_api_client, "my_definition_id")
        assert base_definition.specification is None
        assert base_definition.id == "my_definition_id"
        assert base_definition.api_instance == base_definition.api.return_value
        assert base_definition._api_data == base_definition._read.return_value
        base_definition.api.assert_called_with(mock_api_client)
        assert base_definition._get_fn_kwargs == {}
        assert base_definition._get_fn == getattr(base_definition.api, base_definition.get_function_name)

    def test_get_attr(self, patch_base_class, mock_api_client):
        base_definition = BaseDefinition(mock_api_client, "my_definition_id")
        base_definition._api_data = {"foo": "bar"}
        assert base_definition.foo == "bar"
        with pytest.raises(AttributeError):
            base_definition.not_existing

    def test_read_success(self, patch_base_class, mock_api_client, mocker):
        mocker.patch.object(BaseDefinition, "_get_fn", mocker.Mock())
        base_definition = BaseDefinition(mock_api_client, "my_definition_id")
        read_output = base_definition._read()
        assert read_output == base_definition._get_fn.return_value
        base_definition._get_fn.assert_called_with(base_definition.api_instance, **base_definition._get_fn_kwargs, _check_return_type=False)

    @pytest.mark.parametrize("status_code", [404, 422])
    def test_read_error_not_found(self, status_code, patch_base_class, mock_api_client, mocker):
        mocker.patch.object(BaseDefinition, "_get_fn", mocker.Mock(side_effect=ApiException(status=status_code)))
        with pytest.raises(DefinitionNotFoundError):
            BaseDefinition(mock_api_client, "my_definition_id")

    def test_read_error_other(self, patch_base_class, mock_api_client, mocker):
        expected_error = ApiException(status=42)
        mocker.patch.object(BaseDefinition, "_get_fn", mocker.Mock(side_effect=expected_error))
        with pytest.raises(ApiException) as e:
            BaseDefinition(mock_api_client, "my_definition_id")
            assert e == expected_error


class TestSourceDefinition:
    def test_init(self, mock_api_client):
        assert SourceDefinition.__base__ == BaseDefinition
        source_definition = SourceDefinition(mock_api_client, "source_id")
        assert source_definition.api == source_definition_api.SourceDefinitionApi
        assert source_definition.type == "source"
        assert source_definition.get_function_name == "get_source_definition"
        assert source_definition._get_fn_kwargs == {"source_definition_id_request_body": SourceDefinitionIdRequestBody("source_id")}


class TestDestinationDefinition:
    def test_init(self, mock_api_client):
        assert DestinationDefinition.__base__ == BaseDefinition
        destination_definition = DestinationDefinition(mock_api_client, "source_id")
        assert destination_definition.api == destination_definition_api.DestinationDefinitionApi
        assert destination_definition.type == "destination"
        assert destination_definition.get_function_name == "get_destination_definition"
        assert destination_definition._get_fn_kwargs == {
            "destination_definition_id_request_body": DestinationDefinitionIdRequestBody("source_id")
        }


class TestSourceDefinitionSpecification:
    def test_init(self, mock_api_client):
        assert SourceDefinitionSpecification.__base__ == DefinitionSpecification
        source_specification = SourceDefinitionSpecification(mock_api_client, "workspace_id", "source_id")
        assert source_specification.api == source_definition_specification_api.SourceDefinitionSpecificationApi
        assert source_specification.get_function_name == "get_source_definition_specification"


class TestDestinationDefinitionSpecification:
    def test_init(self, mock_api_client):
        assert DestinationDefinitionSpecification.__base__ == DefinitionSpecification
        destination_specification = DestinationDefinitionSpecification(mock_api_client, "workspace_id", "source_id")
        assert destination_specification.api == destination_definition_specification_api.DestinationDefinitionSpecificationApi
        assert destination_specification.get_function_name == "get_destination_definition_specification"


def test_factory(mock_api_client):
    source_definition = factory("source", mock_api_client, "workspace_id", "source_definition_id")
    assert isinstance(source_definition, SourceDefinition)
    assert isinstance(source_definition.specification, SourceDefinitionSpecification)

    destination_definition = factory("destination", mock_api_client, "workspace_id", "destination_definition_id")
    assert isinstance(destination_definition, DestinationDefinition)
    assert isinstance(destination_definition.specification, DestinationDefinitionSpecification)

    with pytest.raises(ValueError):
        factory("random", mock_api_client, "workspace_id", "random_definition_id")
