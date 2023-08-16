#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import inspect
import sys
from abc import ABC, abstractmethod
from enum import Enum
from typing import Type

import dagger
from py_markdown_table.markdown_table import markdown_table


class PythonBase(Enum):
    # Using image digest to ensure that the image is not changed
    PYTHON_3_9 = "python:3.9@sha256:0596c508fdfdf28fd3b98e170f7e3d4708d01df6e6d4bffa981fd6dd22dbd1a5"
    PYTHON_3_10_12 = "python:3.10.12@sha256-527cc6f230cf7de1f972fbb0ffc850035e91fb4a52058b44906ea706b3018bb6"


class VersionError(Exception):
    pass


class AirbytePythonBase(ABC):

    name = "airbyte-python-base"

    TIMEZONE = "Etc/UTC"

    @property
    @abstractmethod
    def python_base_image(cls) -> PythonBase:
        raise NotImplementedError("Subclasses must define a 'python_base_image'.")

    @property
    @abstractmethod
    def changelog(cls) -> str:
        raise NotImplementedError("Subclasses must define a 'changelog' attribute.")

    def __init__(self, dagger_client: dagger.Client):
        self.dagger_client = dagger_client
        self.validate_version()

    @classmethod
    def name_and_version(cls) -> str:
        return f"{cls.name}:{cls.version()}"

    @classmethod
    def version(cls):
        return ".".join(cls.__name__.split("_")[1:])

    @property
    def base(self) -> dagger.Container:
        return self.dagger_client.container().from_(self.python_base_image.value).with_env_variable("BASE_IMAGE", self.name_and_version())

    @property
    @abstractmethod
    def container(self):
        raise NotImplementedError("Subclasses must define a 'container' property.")

    def validate_version(self):
        version_parts = self.version().split(".")
        if not len(version_parts) == 3 and all([v.isdigit() for v in version_parts]):
            raise VersionError("Version must be in the format 'x.y.z' and each part must be a digit.")


class _0_0_1(AirbytePythonBase):
    python_base_image = PythonBase.PYTHON_3_9

    apt_packages = [
        "curl",
        "bash",
        "build-essential",
        "cmake",
        "g++",
        "libffi-dev",
        "libstdc++6",
    ]

    changelog = "Declares the legacy base image with mandatory debian packages, pip upgrade, timezone settings ..."

    @property
    def container(self) -> dagger.Container:
        return (
            self.base.with_exec(["ln", "-snf", f"/usr/share/zoneinfo/{self.TIMEZONE}", "/etc/localtime"])
            .with_exec(["apt-get", "update"])
            .with_exec(["apt-get", "install", "-y", *self.apt_packages])
            .with_exec(["pip", "install", "--upgrade", "pip"])
        )


class _0_0_2(_0_0_1):
    python_base_image = PythonBase.PYTHON_3_9

    changelog = "Adds git to the base image."

    @property
    def container(self) -> dagger.Container:

        return super().with_exec(["apt-get", "install", "-y", "git"])


class _1_0_0(_0_0_2):
    python_base_image = PythonBase.PYTHON_3_10_12

    changelog = "Upgrades the base image to Python 3.10.12."


def get_all_base_images() -> dict[str, Type[AirbytePythonBase]]:
    # Reverse the order of the members so that the latest version is first
    cls_members = reversed(inspect.getmembers(sys.modules[__name__], inspect.isclass))
    return {
        cls_member.name_and_version(): cls_member
        for _, cls_member in cls_members
        if issubclass(type(cls_member), type(AirbytePythonBase)) and cls_member != AirbytePythonBase and cls_member != ABC
    }


ALL_BASE_IMAGES = get_all_base_images()


def write_changelog_file():
    entries = [{"Version": base_cls.version(), "Changelog": base_cls.changelog} for _, base_cls in ALL_BASE_IMAGES.items()]
    markdown = markdown_table(entries).set_params(row_sep="markdown", quote=False).get_markdown()
    with open("PYTHON_BASE_IMAGES_CHANGELOG.md", "w") as f:
        f.write(
            "Python base images used for connector built are declared [here](https://github.com/airbytehq/airbyte/blob/8328c9dd89f6417295a20f7c0f5b823a2f02ee8e/airbyte-ci/connectors/pipelines/pipelines/builds/base_images/python.py)"
        )
        f.write(f"# Changelog for {AirbytePythonBase.name}\n\n")
        f.write(markdown)


write_changelog_file()
