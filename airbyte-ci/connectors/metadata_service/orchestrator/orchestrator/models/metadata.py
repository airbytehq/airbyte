#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Optional, Tuple

import orchestrator.hacks as HACKS
from metadata_service.constants import METADATA_FILE_NAME
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from orchestrator.config import CONNECTOR_DEPENDENCY_FILE_NAME, CONNECTOR_DEPENDENCY_FOLDER, get_public_url_for_gcs_file
from pydantic import BaseModel, ValidationError
from pydash import get


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


class LatestMetadataEntry(BaseModel):
    metadata_definition: MetadataDefinition
    icon_url: Optional[str] = None
    bucket_name: Optional[str] = None
    file_path: Optional[str] = None
    etag: Optional[str] = None
    last_modified: Optional[str] = None

    @property
    def is_latest_version_path(self) -> bool:
        """
        Path is considered a latest version path if the subfolder containing METADATA_FILE_NAME is "latest"
        """
        ending_path = f"latest/{METADATA_FILE_NAME}"
        return self.file_path.endswith(ending_path)

    @property
    def is_release_candidate_version_path(self) -> bool:
        """
        Path is considered a latest version path if the subfolder containing METADATA_FILE_NAME is "latest"
        """
        ending_path = f"release_candidate/{METADATA_FILE_NAME}"
        return self.file_path.endswith(ending_path)

    @property
    def dependency_file_url(self) -> Optional[str]:
        if not self.bucket_name or not self.metadata_definition:
            return None

        connector_technical_name = get(self.metadata_definition, "data.dockerRepository")
        connector_version = get(self.metadata_definition, "data.dockerImageTag")
        sanitized_connector_technical_name = HACKS.sanitize_docker_repo_name_for_dependency_file(connector_technical_name)

        file_path = (
            f"{CONNECTOR_DEPENDENCY_FOLDER}/{sanitized_connector_technical_name}/{connector_version}/{CONNECTOR_DEPENDENCY_FILE_NAME}"
        )
        return get_public_url_for_gcs_file(self.bucket_name, file_path)
