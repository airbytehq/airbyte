import re
import yaml
import pathlib
from pydantic import ValidationError
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from typing import Optional, Tuple, Union
from metadata_service.docker_hub import is_image_on_docker_hub
from pydash.objects import get

ValidationResult = Tuple[bool, Optional[Union[ValidationError, str]]]

# These connectors were already on N.0.0 versions when the validation checking for breakingChanges entries
# on major version bumps was added - therefore they are exempt from the check. These connectors should be
# removed from the list as soon as their version is bumped to something else (ideally before their next
# major version bump).
MAJOR_VERSION_BREAKING_CHANGE_CHECK_EXCEPTIONS = [
    ("airbyte/destination-csv", "1.0.0"),
    ("airbyte/destination-meilisearch", "1.0.0"),
    ("airbyte/source-s3", "3.0.0"),
    ("airbyte/source-yandex-metrica", "1.0.0"),
    ("airbyte/source-onesignal", "1.0.0"),
]


def validate_metadata_images_in_dockerhub(metadata_definition: ConnectorMetadataDefinitionV0) -> ValidationResult:
    metadata_definition_dict = metadata_definition.dict()
    base_docker_image = get(metadata_definition_dict, "data.dockerRepository")
    base_docker_version = get(metadata_definition_dict, "data.dockerImageTag")

    oss_docker_image = get(metadata_definition_dict, "data.registries.oss.dockerRepository", base_docker_image)
    oss_docker_version = get(metadata_definition_dict, "data.registries.oss.dockerImageTag", base_docker_version)

    cloud_docker_image = get(metadata_definition_dict, "data.registries.cloud.dockerRepository", base_docker_image)
    cloud_docker_version = get(metadata_definition_dict, "data.registries.cloud.dockerImageTag", base_docker_version)

    normalization_docker_image = get(metadata_definition_dict, "data.normalizationConfig.normalizationRepository", None)
    normalization_docker_version = get(metadata_definition_dict, "data.normalizationConfig.normalizationTag", None)

    possible_docker_images = [
        (base_docker_image, base_docker_version),
        (oss_docker_image, oss_docker_version),
        (cloud_docker_image, cloud_docker_version),
        (normalization_docker_image, normalization_docker_version),
    ]

    # Filter out tuples with None and remove duplicates
    images_to_check = list(set(filter(lambda x: None not in x, possible_docker_images)))

    print(f"Checking that the following images are on dockerhub: {images_to_check}")

    for image, version in images_to_check:
        if not is_image_on_docker_hub(image, version):
            return False, f"Image {image}:{version} does not exist in DockerHub"

    return True, None


def validate_at_least_one_langauge_tag(metadata_definition: ConnectorMetadataDefinitionV0) -> ValidationResult:
    """Ensure that there is at least one tag in the data.tags field that matches language:<LANG>."""
    tags = get(metadata_definition, "data.tags", [])
    if not any([tag.startswith("language:") for tag in tags]):
        return False, "At least one tag must be of the form language:<LANG>"

    return True, None


def validate_all_tags_are_keyvalue_pairs(metadata_definition: ConnectorMetadataDefinitionV0) -> ValidationResult:
    """Ensure that all tags are of the form <KEY>:<VALUE>."""
    tags = get(metadata_definition, "data.tags", [])
    for tag in tags:
        if ":" not in tag:
            return False, f"Tag {tag} is not of the form <KEY>:<VALUE>"

    return True, None


def is_major_version(version: str) -> bool:
    return re.match(r"^\d\.0\.0$", version) is not None


def validate_major_version_has_breaking_change_entry(metadata_definition: ConnectorMetadataDefinitionV0) -> ValidationResult:
    """Ensure that if the major version is incremented, there is a breaking change entry for that version."""
    metadata_definition_dict = metadata_definition.dict()
    image_tag = get(metadata_definition_dict, "data.dockerImageTag", None)

    if not is_major_version(image_tag):
        return True, None

    base_docker_image = get(metadata_definition_dict, "data.dockerRepository")
    if (base_docker_image, image_tag) in MAJOR_VERSION_BREAKING_CHANGE_CHECK_EXCEPTIONS:
        return True, None

    releases = get(metadata_definition_dict, "data.releases", None)
    if not releases:
        return False, f"When doing a major version bump ({image_tag}), there must be a 'releases' property that contains 'breakingChanges' entries."

    breaking_changes = get(metadata_definition_dict, "data.releases.breakingChanges", None)
    if image_tag not in breaking_changes.keys():
        return False, f"Major version {image_tag} needs a 'releases.breakingChanges' entry indicating what changed."

    return True, None


def pre_upload_validations(metadata_definition: ConnectorMetadataDefinitionV0) -> ValidationResult:
    """
    Runs all validations that should be run before uploading a connector to the registry.
    """
    validations = [
        validate_all_tags_are_keyvalue_pairs,
        validate_at_least_one_langauge_tag,
        validate_major_version_has_breaking_change_entry,
    ]

    for validation in validations:
        valid, error = validation(metadata_definition)
        if not valid:
            return False, error

    return True, None


def validate_metadata_file(file_path: pathlib.Path) -> ValidationResult:
    """
    Validates a metadata YAML file against a metadata Pydantic model.
    """
    try:
        metadata = yaml.safe_load(file_path.read_text())
        metadata_model = ConnectorMetadataDefinitionV0.parse_obj(metadata)
        return pre_upload_validations(metadata_model)
    except ValidationError as e:
        return False, e
