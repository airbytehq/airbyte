from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from metadata_service.constants import METADATA_FILE_NAME, ICON_FILE_NAME
from pydantic import ValidationError
from dataclasses import dataclass
from google.cloud import storage

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

@dataclass(frozen=True)
class LatestMetadataEntry:
    """Defines the field to add on a record"""

    metadata_definition: MetadataDefinition
    gcs_metadata_file_blob: storage.Blob

    @property
    def gcs_icon_file_blob(self) -> Optional[storage.Blob]:
        """Returns the icon file blob if it exists"""
        metadata_file_path = self.gcs_metadata_file_blob.name

        # replace the metadata file name with the icon file name
        icon_file_path = metadata_file_path.replace(METADATA_FILE_NAME, ICON_FILE_NAME)

        return self.gcs_metadata_file_blob.bucket.get_blob(icon_file_path)
