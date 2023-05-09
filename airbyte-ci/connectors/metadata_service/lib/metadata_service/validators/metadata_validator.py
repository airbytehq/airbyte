import yaml
import pathlib
from pydantic import ValidationError
from metadata_service.models.generated.ConnectorMetadataDefinitionV1 import ConnectorMetadataDefinitionV1


def validate_metadata_file(file_path: pathlib.Path):
    """
    Validates a metadata YAML file against a metadata Pydantic model.
    """
    try:
        metadata = yaml.safe_load(file_path.read_text())
        ConnectorMetadataDefinitionV1.parse_obj(metadata)
        return True, None
    except ValidationError as e:
        return False, e
