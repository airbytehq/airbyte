import yaml
import pathlib
from pydantic import ValidationError
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from typing import Optional, Tuple, Union
from metadata_service.docker_hub import is_image_on_docker_hub
from pydash.objects import get

ValidationResult = Tuple[bool, Optional[Union[ValidationError, str]]]


def validate_metadata_images_in_dockerhub(metadata_definition: ConnectorMetadataDefinitionV0) -> ValidationResult:
    metadata_definition_dict = metadata_definition.dict()
    base_docker_image = get(metadata_definition_dict, "data.dockerRepository")
    base_docker_version = get(metadata_definition_dict, "data.dockerImageTag")

    oss_docker_image = get(metadata_definition_dict, "data.registries.oss.dockerRepository", base_docker_image)
    oss_docker_version = get(metadata_definition_dict, "data.registries.oss.dockerImageTag", base_docker_version)

    cloud_docker_image = get(metadata_definition_dict, "data.registries.cloud.dockerRepository", base_docker_image)
    cloud_docker_version = get(metadata_definition_dict, "data.registries.cloud.dockerImageTag", base_docker_version)

    possible_docker_images = [
        (base_docker_image, base_docker_version),
        (oss_docker_image, oss_docker_version),
        (cloud_docker_image, cloud_docker_version),
    ]

    # Filter out tuples with None and remove duplicates
    images_to_check = list(set(filter(lambda x: None not in x, possible_docker_images)))

    print(f"Checking that the following images are on dockerhub: {images_to_check}")

    for image, version in images_to_check:
        if not is_image_on_docker_hub(image, version):
            return False, f"Image {image}:{version} does not exist in DockerHub"

    return True, None


def validate_metadata_file(file_path: pathlib.Path) -> ValidationResult:
    """
    Validates a metadata YAML file against a metadata Pydantic model.
    """
    try:
        metadata = yaml.safe_load(file_path.read_text())
        ConnectorMetadataDefinitionV0.parse_obj(metadata)
        return True, None
    except ValidationError as e:
        return False, e
