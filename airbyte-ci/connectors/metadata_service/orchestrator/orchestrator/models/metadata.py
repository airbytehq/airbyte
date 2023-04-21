from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from pydantic import ValidationError

from pydantic import ValidationError
from typing import Tuple, Any, Optional


class PydanticDelayValidationMixin:
    """
    This is to allow us to delay validation until we have all the data we need.
    Note: To use this mixin you will want to construct your model with the pydantic
    `construct` method. This will allow you to set the values of the model before
    validation occurs.
    """

    def validate(self):
        if hasattr(super(), "validate"):
            super().validate(self.dict())

    @property
    def is_valid(self) -> Tuple[bool, Optional[Any]]:
        try:
            self.validate()
            return (True, None)
        except ValidationError as e:
            return (False, e)


class PydanticDictMixin:
    def __getitem__(self, key: str):
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any):
        self.__dict__[key] = value


class PartialMetadataDefinition(PydanticDelayValidationMixin, PydanticDictMixin, ConnectorMetadataDefinitionV0):
    pass


class MetadataDefinition(PydanticDictMixin, ConnectorMetadataDefinitionV0):
    pass
