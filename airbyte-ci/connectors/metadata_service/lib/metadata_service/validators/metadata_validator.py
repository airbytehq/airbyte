#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pathlib
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple, Union

import semver
import yaml
from metadata_service.docker_hub import get_latest_version_on_dockerhub, is_image_on_docker_hub
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from pydantic import ValidationError
from pydash.objects import get


@dataclass(frozen=True)
class ValidatorOptions:
    docs_path: str
    prerelease_tag: Optional[str] = None


ValidationResult = Tuple[bool, Optional[Union[ValidationError, str]]]
Validator = Callable[[ConnectorMetadataDefinitionV0, ValidatorOptions], ValidationResult]

_SOURCE_DECLARATIVE_MANIFEST_DEFINITION_ID = "64a2f99c-542f-4af8-9a6f-355f1217b436"


def validate_metadata_images_in_dockerhub(
    metadata_definition: ConnectorMetadataDefinitionV0, validator_opts: ValidatorOptions
) -> ValidationResult:
    metadata_definition_dict = metadata_definition.dict()
    base_docker_image = get(metadata_definition_dict, "data.dockerRepository")
    base_docker_version = get(metadata_definition_dict, "data.dockerImageTag")

    oss_docker_image = get(metadata_definition_dict, "data.registryOverrides.oss.dockerRepository", base_docker_image)
    oss_docker_version = get(metadata_definition_dict, "data.registryOverrides.oss.dockerImageTag", base_docker_version)

    cloud_docker_image = get(metadata_definition_dict, "data.registryOverrides.cloud.dockerRepository", base_docker_image)
    cloud_docker_version = get(metadata_definition_dict, "data.registryOverrides.cloud.dockerImageTag", base_docker_version)

    normalization_docker_image = get(metadata_definition_dict, "data.normalizationConfig.normalizationRepository", None)
    normalization_docker_version = get(metadata_definition_dict, "data.normalizationConfig.normalizationTag", None)

    breaking_change_versions = get(metadata_definition_dict, "data.releases.breakingChanges", {}).keys()

    possible_docker_images = [
        (base_docker_image, base_docker_version),
        (oss_docker_image, oss_docker_version),
        (cloud_docker_image, cloud_docker_version),
        (normalization_docker_image, normalization_docker_version),
    ]

    if not validator_opts.prerelease_tag:
        possible_docker_images.extend([(base_docker_image, version) for version in breaking_change_versions])

    # Filter out tuples with None and remove duplicates
    images_to_check = list(set(filter(lambda x: None not in x, possible_docker_images)))

    print(f"Checking that the following images are on dockerhub: {images_to_check}")
    for image, version in images_to_check:
        if not is_image_on_docker_hub(image, version, retries=3):
            return False, f"Image {image}:{version} does not exist in DockerHub"

    return True, None


def validate_at_least_one_language_tag(
    metadata_definition: ConnectorMetadataDefinitionV0, _validator_opts: ValidatorOptions
) -> ValidationResult:
    """Ensure that there is at least one tag in the data.tags field that matches language:<LANG>."""
    tags = get(metadata_definition, "data.tags", [])
    if not any([tag.startswith("language:") for tag in tags]):
        return False, "At least one tag must be of the form language:<LANG>"

    return True, None


def validate_all_tags_are_keyvalue_pairs(
    metadata_definition: ConnectorMetadataDefinitionV0, _validator_opts: ValidatorOptions
) -> ValidationResult:
    """Ensure that all tags are of the form <KEY>:<VALUE>."""
    tags = get(metadata_definition, "data.tags", [])
    for tag in tags:
        if ":" not in tag:
            return False, f"Tag {tag} is not of the form <KEY>:<VALUE>"

    return True, None


def is_major_version(version: str) -> bool:
    """Check whether the version is of format N.0.0"""
    semver_version = semver.Version.parse(version)
    return semver_version.minor == 0 and semver_version.patch == 0 and semver_version.prerelease is None


def validate_major_version_bump_has_breaking_change_entry(
    metadata_definition: ConnectorMetadataDefinitionV0, _validator_opts: ValidatorOptions
) -> ValidationResult:
    """Ensure that if the major version is incremented, there is a breaking change entry for that version."""
    metadata_definition_dict = metadata_definition.dict()
    image_tag = get(metadata_definition_dict, "data.dockerImageTag")

    if not is_major_version(image_tag):
        return True, None

    # We are updating the same version since connector builder projects have a different concept of
    # versioning.
    # We do not check for breaking changes for source-declarative-connector in the metadata because the conenctor isn't directly used by any workspace.
    # Breaking changes are instead tracked at the CDK level
    if str(metadata_definition.data.definitionId) == _SOURCE_DECLARATIVE_MANIFEST_DEFINITION_ID:
        return True, None

    docker_repo = get(metadata_definition_dict, "data.dockerRepository")
    releases = get(metadata_definition_dict, "data.releases")
    if not releases:
        return (
            False,
            f"When doing a major version bump ({image_tag}), there must be a 'releases' property that contains 'breakingChanges' entries.",
        )

    breaking_changes = get(metadata_definition_dict, "data.releases.breakingChanges")
    if image_tag not in breaking_changes.keys():
        return False, f"Major version {image_tag} needs a 'releases.breakingChanges' entry indicating what changed."

    return True, None


def validate_docs_path_exists(metadata_definition: ConnectorMetadataDefinitionV0, validator_opts: ValidatorOptions) -> ValidationResult:
    """Ensure that the doc_path exists."""
    if not pathlib.Path(validator_opts.docs_path).exists():
        return False, f"Could not find {validator_opts.docs_path}."

    return True, None


def validate_metadata_base_images_in_dockerhub(
    metadata_definition: ConnectorMetadataDefinitionV0, validator_opts: ValidatorOptions
) -> ValidationResult:
    metadata_definition_dict = metadata_definition.dict()

    image_address = get(metadata_definition_dict, "data.connectorBuildOptions.baseImage")
    if image_address is None:
        return True, None

    try:
        image_name, tag_with_sha_prefix, digest = image_address.split(":")
        # As we query the DockerHub API we need to remove the docker.io prefix
        image_name = image_name.replace("docker.io/", "")
    except ValueError:
        return False, f"Image {image_address} is not in the format <image>:<tag>@<sha>"
    tag = tag_with_sha_prefix.split("@")[0]

    print(f"Checking that the base images is on dockerhub: {image_address}")

    if not is_image_on_docker_hub(image_name, tag, digest, retries=3):
        return False, f"Image {image_address} does not exist in DockerHub"

    return True, None


def validate_pypi_only_for_python(
    metadata_definition: ConnectorMetadataDefinitionV0, _validator_opts: ValidatorOptions
) -> ValidationResult:
    """Ensure that if pypi publishing is enabled for a connector, it has a python language tag."""

    pypi_enabled = get(metadata_definition, "data.remoteRegistries.pypi.enabled", False)
    if not pypi_enabled:
        return True, None

    tags = get(metadata_definition, "data.tags", [])
    if "language:python" not in tags and "language:low-code" not in tags:
        return False, "If pypi publishing is enabled, the connector must have a python language tag."

    return True, None


def validate_docker_image_tag_is_not_decremented(
    metadata_definition: ConnectorMetadataDefinitionV0, _validator_opts: ValidatorOptions
) -> ValidationResult:
    if _validator_opts and _validator_opts.prerelease_tag:
        return True, None
    docker_image_name = get(metadata_definition, "data.dockerRepository")
    if not docker_image_name:
        return False, "The dockerRepository field is not set"
    docker_image_tag = get(metadata_definition, "data.dockerImageTag")
    if not docker_image_tag:
        return False, "The dockerImageTag field is not set."
    latest_released_version = get_latest_version_on_dockerhub(docker_image_name)
    # This is happening when the connector has never been released to DockerHub
    if not latest_released_version:
        return True, None
    if docker_image_tag == latest_released_version:
        return True, None
    current_semver_version = semver.Version.parse(docker_image_tag)
    latest_released_semver_version = semver.Version.parse(latest_released_version)
    if current_semver_version < latest_released_semver_version:
        return (
            False,
            f"The dockerImageTag value ({current_semver_version}) can't be decremented: it should be equal to or above {latest_released_version}.",
        )
    return True, None


PRE_UPLOAD_VALIDATORS = [
    validate_all_tags_are_keyvalue_pairs,
    validate_at_least_one_language_tag,
    validate_major_version_bump_has_breaking_change_entry,
    validate_docs_path_exists,
    validate_metadata_base_images_in_dockerhub,
    validate_pypi_only_for_python,
    validate_docker_image_tag_is_not_decremented,
]

POST_UPLOAD_VALIDATORS = PRE_UPLOAD_VALIDATORS + [
    validate_metadata_images_in_dockerhub,
]


def validate_and_load(
    file_path: pathlib.Path,
    validators_to_run: List[Validator],
    validator_opts: ValidatorOptions,
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
        print(f"Running validator: {validator.__name__}")
        is_valid, error = validator(metadata_model, validator_opts)
        if not is_valid:
            return None, f"Validation error: {error}"

    return metadata_model, None
