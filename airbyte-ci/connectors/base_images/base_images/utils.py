#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import importlib
import inspect
import pkgutil
from abc import ABC
from types import ModuleType
from typing import List, Type

import semver
from base_images import errors, consts


def find_modules_in_package(package: str) -> List[ModuleType]:
    package_path = f'{consts.PROJECT_DIR}/{package.replace(".", "/")}'
    return [importlib.import_module(f"{package}.{module_name}") for _, module_name, _ in pkgutil.iter_modules([package_path])]


def get_all_concrete_subclasses_in_module(module: ModuleType, SuperClass: Type) -> List[Type]:
    all_subclasses = []
    for _, cls_member in inspect.getmembers(module, inspect.isclass):
        if issubclass(cls_member, SuperClass) and cls_member != SuperClass and cls_member != ABC:
            all_subclasses.append(cls_member)
    return all_subclasses


def get_all_concrete_subclasses_in_package(package: str, SuperClass: Type) -> List[Type]:
    all_subclasses = []
    for module in find_modules_in_package(package):
        all_subclasses.extend(get_all_concrete_subclasses_in_module(module, SuperClass))
    return all_subclasses


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


def get_all_version_classes_in_package(abstract_base_version_class: Type, package: str) -> List[Type]:
    """Discover the base image versions declared in a package.
    It saves us from hardcoding the list of base images version: implementing a new subclass should be the only step to make a new base version available.

    Raises:
        BaseImageVersionError: Raised if two versions have the same name, this can happen if a same class name is used in two different modules of the current package.

    Returns:
        dict[str, Type[AirbyteConnectorBaseImage]]: A dictionary of the base image versions declared in the module, keys are base image name and tag as string.
    """
    all_base_image_classes = get_all_concrete_subclasses_in_package(package, abstract_base_version_class)
    all_base_image_classes_reverse_sorted_by_version = sorted(all_base_image_classes, key=lambda cls: cls.version, reverse=True)
    available_versions = [base_image_version_class.version for base_image_version_class in all_base_image_classes_reverse_sorted_by_version]
    unique_versions = set(available_versions)
    if len(available_versions) != len(unique_versions):
        raise errors.BaseImageVersionError(
            "Found duplicate versions. Two version classes with the same name are probably defined in different modules."
        )
    return all_base_image_classes_reverse_sorted_by_version
