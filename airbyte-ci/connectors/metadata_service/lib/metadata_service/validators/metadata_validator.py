import re
import semver
import pathlib
import yaml
from pydantic import ValidationError
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from typing import Optional, Tuple, Union, List, Callable
from metadata_service.docker_hub import is_image_on_docker_hub
from pydash.objects import get

ValidationResult = Tuple[bool, Optional[Union[ValidationError, str]]]
Validator = Callable[[ConnectorMetadataDefinitionV0], ValidationResult]

# TODO: Remove these when each of these connectors ship any new version
ALREADY_ON_MAJOR_VERSION_EXCEPTIONS = [
    ("airbyte/source-prestashop", "1.0.0"),
    ("airbyte/source-onesignal", "1.0.0"),
    ("airbyte/source-yandex-metrica", "1.0.0"),
    ("airbyte/destination-meilisearch", "1.0.0"),
    ("airbyte/destination-csv", "1.0.0"),
    ("airbyte/source-metabase", "1.0.0"),
    ("airbyte/source-typeform", "1.0.0"),
    ("airbyte/source-recharge", "1.0.0"),
    ("airbyte/source-pipedrive", "1.0.0"),
    ("airbyte/source-paypal-transaction", "2.0.0"),
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

    breaking_change_versions = get(metadata_definition_dict, "data.releases.breakingChanges", {}).keys()

    possible_docker_images = [
        (base_docker_image, base_docker_version),
        (oss_docker_image, oss_docker_version),
        (cloud_docker_image, cloud_docker_version),
        (normalization_docker_image, normalization_docker_version),
    ]
    possible_docker_images.extend([(base_docker_image, version) for version in breaking_change_versions])

    # Filter out tuples with None and remove duplicates
    images_to_check = list(set(filter(lambda x: None not in x, possible_docker_images)))

    print(f"Checking that the following images are on dockerhub: {images_to_check}")
    for image, version in images_to_check:
        if not is_image_on_docker_hub(image, version):
            return False, f"Image {image}:{version} does not exist in DockerHub"

    return True, None


def validate_at_least_one_language_tag(metadata_definition: ConnectorMetadataDefinitionV0) -> ValidationResult:
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
    """Check whether the version is of format N.0.0"""
    semver_version = semver.Version.parse(version)
    return semver_version.minor == 0 and semver_version.patch == 0


def validate_major_version_bump_has_breaking_change_entry(metadata_definition: ConnectorMetadataDefinitionV0) -> ValidationResult:
    """Ensure that if the major version is incremented, there is a breaking change entry for that version."""
    metadata_definition_dict = metadata_definition.dict()
    image_tag = get(metadata_definition_dict, "data.dockerImageTag")

    if not is_major_version(image_tag):
        return True, None

    # Some connectors had just done major version bumps when this check was introduced.
    # These do not need breaking change entries for these specific versions.
    # Future versions will still be validated to make sure an entry exists.
    # See comment by ALREADY_ON_MAJOR_VERSION_EXCEPTIONS for how to get rid of this list.
    docker_repo = get(metadata_definition_dict, "data.dockerRepository")
    if (docker_repo, image_tag) in ALREADY_ON_MAJOR_VERSION_EXCEPTIONS:
        return True, None

    releases = get(metadata_definition_dict, "data.releases")
    if not releases:
        return False, f"When doing a major version bump ({image_tag}), there must be a 'releases' property that contains 'breakingChanges' entries."

    breaking_changes = get(metadata_definition_dict, "data.releases.breakingChanges")
    if image_tag not in breaking_changes.keys():
        return False, f"Major version {image_tag} needs a 'releases.breakingChanges' entry indicating what changed."

    return True, None


PRE_UPLOAD_VALIDATORS = [
    validate_all_tags_are_keyvalue_pairs,
    validate_at_least_one_language_tag,
    validate_major_version_bump_has_breaking_change_entry,
]

POST_UPLOAD_VALIDATORS = PRE_UPLOAD_VALIDATORS + [
    validate_metadata_images_in_dockerhub,
]


def validate_and_load(
    file_path: pathlib.Path, validators_to_run: List[Validator]
) -> Tuple[Optional[ConnectorMetadataDefinitionV0], Optional[ValidationError]]:
    """Load a metadata file from a path (runs jsonschema validation) and run optional extra validators.

    Returns a tuple of (metadata_model, error_message).
    If the metadata file is valid, metadata_model will be populated.
    Otherwise, error_message will be populated with a string describing the error.
    """

    try:
        # Load the metadata file - this implicitly runs jsonschema validation
        metadata = yaml.safe_load(file_path.read_text())
        metadata_model = ConnectorMetadataDefinitionV0.parse_obj(metadata)
    except ValidationError as e:
        return None, f"Validation error: {e}"

    for validator in validators_to_run:
        is_valid, error = validator(metadata_model)
        if not is_valid:
            return None, f"Validation error: {error}"

    return metadata_model, None
