#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import importlib
import inspect
import pkgutil
from abc import ABC
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, List, Mapping, MutableMapping, Optional, Type

import semver
from base_images import consts, errors
from py_markdown_table.markdown_table import markdown_table  # type: ignore

if TYPE_CHECKING:
    from base_images.common import AirbyteConnectorBaseImage


def get_version_from_class_name(cls: Type) -> semver.VersionInfo:
    """The version is parsed from the class name.
    The class name must follow the naming convention: `_MAJOR_MINOR_PATCH` e.g `_1_0_0`.
    You can declare pre-release versions by adding a `__` followed by the pre-release version name e.g `_1_0_0__alpha`.
    Returns:
        semver.VersionInfo: The version parsed from the class name.
    """
    try:
        return semver.VersionInfo.parse(".".join(cls.__name__.replace("__", "-").split("_")[1:]))
    except ValueError as e:
        raise errors.BaseImageVersionError(f"The version class {cls.__name__} is not in the expected naming format: e.g `_1_0_0`.") from e


class VersionRegistry:
    def __init__(self, abstract_base_version_class: Type[AirbyteConnectorBaseImage]):
        self._versions: List[Type[AirbyteConnectorBaseImage]] = []
        self.abstract_base_version_class = abstract_base_version_class

    @property
    def base_image_name(self) -> str:
        return self.abstract_base_version_class.image_name  # type: ignore

    @staticmethod
    def build_from_package(abstract_base_version_class: Type[Any], package_name: str, package_path: List[str]) -> VersionRegistry:
        version_registry = VersionRegistry(abstract_base_version_class)
        all_base_image_versions = []
        for _, module_name, is_pkg in pkgutil.walk_packages(package_path, prefix=package_name + "."):
            if not is_pkg:
                module = importlib.import_module(module_name)
                all_base_image_versions.extend(version_registry._get_all_concrete_subclasses_in_module(module, abstract_base_version_class))

        version_registry._register_versions(all_base_image_versions)
        return version_registry

    def _get_all_concrete_subclasses_in_module(self, module: ModuleType, SuperClass: Type) -> List[Type]:
        all_subclasses = []
        for _, cls_member in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls_member, SuperClass) and cls_member != SuperClass and cls_member != ABC:
                all_subclasses.append(cls_member)
        return all_subclasses

    def _check_for_duplicate_versions(self, all_base_image_versions: List[Type[AirbyteConnectorBaseImage]]):
        """Checks that there are no duplicate versions. This can happen if two version classes with the same name are defined in different modules.

        Args:
            all_base_image_versions (List[AirbyteConnectorBaseImage]): A list of base image versions.

        Raises:
            errors.BaseImageVersionError: Raised if there are duplicate versions.
        """
        available_versions = [base_image_version_class.name_with_tag for base_image_version_class in all_base_image_versions]
        unique_versions = set(available_versions)
        if len(available_versions) != len(unique_versions):
            raise errors.BaseImageVersionError(
                "Found duplicate versions. Two version classes with the same name are probably defined in different modules."
            )

    def _register_versions(self, base_image_versions: List[Type[AirbyteConnectorBaseImage]]):
        """Registers a list of base image versions. We check that there are no duplicate versions. This can happen if two version classes with the same name are defined in different modules.

        Args:
            base_image_versions (List[Type[AirbyteConnectorBaseImage]]): _description_

        Returns:
            _type_: _description_
        """
        self._check_for_duplicate_versions(base_image_versions)
        self._versions.extend(base_image_versions)
        return self._versions

    @property
    def versions(self) -> List[Type[AirbyteConnectorBaseImage]]:
        """Returns all the base image versions sorted by version number in descending order.

        Returns:
            List[Type[AirbyteConnectorBaseImage]]: All the base image versions sorted by version number in descending order.
        """
        return sorted(self._versions, key=lambda cls: cls.version, reverse=True)

    @property
    def latest_version(self) -> Type[AirbyteConnectorBaseImage]:
        return self.versions[0]

    def get_previous_version(self, base_image_version: AirbyteConnectorBaseImage) -> Optional[Type[AirbyteConnectorBaseImage]]:
        for BaseImageVersion in self.versions:
            if BaseImageVersion.version < base_image_version.version:
                return BaseImageVersion
        return None

    def as_dict(self) -> Mapping[str, Type[AirbyteConnectorBaseImage]]:
        return {version.name_with_tag: version for version in self.versions}

    @property
    def changelog_path(self) -> Path:
        return consts.PROJECT_DIR / "generated" / "docs" / "base_images_changelogs" / f"{self.base_image_name}.md"

    def write_changelog(self) -> Path:
        """Writes the registry changelog file locally."""
        self.changelog_path.parent.mkdir(exist_ok=True, parents=True)
        self.changelog_path.unlink(missing_ok=True)
        entries = [
            {
                "Version": f"[{base_version_image_class.version}]({base_version_image_class.github_url})",
                "Changelog": base_version_image_class.changelog_entry,
            }
            for base_version_image_class in self.versions
        ]
        markdown = markdown_table(entries).set_params(row_sep="markdown", quote=False).get_markdown()
        with open(self.changelog_path, "w") as f:
            f.write(f"# Changelog for {self.base_image_name}\n\n")
            f.write(markdown)
        return self.changelog_path


class GlobalRegistry:
    def __init__(self, all_registries: List[VersionRegistry]) -> None:
        self.all_registries = all_registries

    def as_dict(self) -> MutableMapping[str, Type[AirbyteConnectorBaseImage]]:
        all_registries_dict: MutableMapping[str, Type[AirbyteConnectorBaseImage]] = {}
        for registry in self.all_registries:
            all_registries_dict = {**all_registries_dict, **registry.as_dict()}
        return all_registries_dict

    def get_version(self, image_name_with_tag: str) -> Type[AirbyteConnectorBaseImage]:
        """Returns the base image version class from its name with tag.

        Args:
            image_name_with_tag (str): The base image version name with tag.

        Raises:
            errors.BaseImageVersionError: Raised if the base image version is not found.

        Returns:
            Type[AirbyteConnectorBaseImage]: The base image version class.
        """
        try:
            return self.as_dict()[image_name_with_tag]
        except KeyError:
            raise errors.BaseImageVersionError(f"Could not find base image version {image_name_with_tag} in the global registry.")
