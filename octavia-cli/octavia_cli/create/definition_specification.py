import abc
import json

from airbyte_api_client.api import destination_definition_specification_api, source_definition_specification_api
from airbyte_api_client.model.destination_definition_id_request_body import DestinationDefinitionIdRequestBody
from airbyte_api_client.model.source_definition_id_request_body import SourceDefinitionIdRequestBody

class DefinitionSpecification(abc.ABC):
    COMMON_GET_FUNCTION_KWARGS = {"_check_return_type": False}

    @property
    @abc.abstractmethod
    def api(
        self,
    ):  # pragma: no cover
        pass


    @property
    @abc.abstractmethod
    def get_function_name(
        self,
    ):  # pragma: no cover
        pass

    @property
    def _get_fn(self):
        return getattr(self.api, self.get_function_name)
    
    @property
    def _get_fn_kwargs() -> dict:
        return {}
    
    def __init__(self, api_client, id:str) -> None:
        self.id = id
        self.api_instance = self.api(api_client)

    @property
    def json_schema(self):
        return json.dumps(self.get().connection_specification)

    def get(self):
        return self._get_fn(self.api_instance, **self._get_fn_kwargs, **self.COMMON_GET_FUNCTION_KWARGS)

class SourceDefinitionSpecification(DefinitionSpecification):
    api = source_definition_specification_api.SourceDefinitionSpecificationApi
    get_function_name = "get_source_definition_specification"

    @property
    def _get_fn_kwargs(self):
        return {"source_definition_id_request_body": SourceDefinitionIdRequestBody(source_definition_id=self.id)}

class DestinationDefinitionSpecification(DefinitionSpecification):
    api = destination_definition_specification_api.DestinationDefinitionSpecificationApi
    get_function_name = "get_destination_definition_specification"

    @property
    def _get_fn_kwargs(self):
        return {"destination_definition_id_request_body": DestinationDefinitionIdRequestBody(destination_definition_id=self.id)}