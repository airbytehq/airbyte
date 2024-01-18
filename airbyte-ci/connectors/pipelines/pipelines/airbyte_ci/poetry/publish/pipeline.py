#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import configparser
import io
import uuid
from enum import Enum, auto
from typing import Dict, Optional, Tuple

import tomli
import tomli_w
from dagger import Container, Directory
from pipelines.airbyte_ci.poetry.publish.context import PyPIPublishContext
from pipelines.consts import PYPROJECT_TOML_FILE_PATH, SETUP_PY_FILE_PATH
from pipelines.dagger.actions.python.poetry import with_poetry
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.steps import Step, StepResult


class PackageType(Enum):
    POETRY = auto()
    PIP = auto()
    NONE = auto()


class PublishToPyPI(Step):
    context: PyPIPublishContext
    title = "Publish package to PyPI"

    def _get_base_container(self) -> Container:
        return with_poetry(self.context)

    async def _get_package_metadata_from_pyproject_toml(self, dir_to_publish: Directory) -> Optional[Tuple[str, str]]:
        pyproject_toml = dir_to_publish.file(PYPROJECT_TOML_FILE_PATH)
        pyproject_toml_content = await pyproject_toml.contents()
        contents = tomli.loads(pyproject_toml_content)
        if (
            "tool" not in contents
            or "poetry" not in contents["tool"]
            or "name" not in contents["tool"]["poetry"]
            or "version" not in contents["tool"]["poetry"]
        ):
            return None

        return (contents["tool"]["poetry"]["name"], contents["tool"]["poetry"]["version"])

    async def _get_package_type(self, dir_to_publish: Directory) -> PackageType:
        files = await dir_to_publish.entries()
        has_pyproject_toml = PYPROJECT_TOML_FILE_PATH in files
        has_setup_py = SETUP_PY_FILE_PATH in files
        if has_pyproject_toml:
            return PackageType.POETRY
        elif has_setup_py:
            return PackageType.PIP
        else:
            return PackageType.NONE

    async def _run(self) -> StepResult:
        dir_to_publish = await self.context.get_repo_dir(self.context.package_path)
        package_type = await self._get_package_type(dir_to_publish)

        if package_type == PackageType.NONE:
            return self.skip("Connector does not have a pyproject.toml file or setup.py file, skipping.")

        # Try to infer package name and version from the pyproject.toml file. If it is not present, we need to have the package name and version set
        # Setup.py packages need to set package name and version as parameter
        if not self.context.package_name or not self.context.version:
            if not package_type == PackageType.POETRY:
                return self.skip(
                    "Connector does not have a pyproject.toml file and version and package name is not set otherwise, skipping."
                )

            package_metadata = await self._get_package_metadata_from_pyproject_toml(dir_to_publish)

            if not package_metadata:
                return self.skip(
                    "Connector does not have a pyproject.toml file which specifies package name and version and they are not set otherwise, skipping."
                )

            self.context.package_name = package_metadata[0]
            self.context.version = package_metadata[1]

        self.logger.info(f"Uploading package {self.context.package_name} version {self.context.version} to {self.context.registry}...")

        if package_type == PackageType.PIP:
            return await self._pip_publish(dir_to_publish)
        else:
            return await self._poetry_publish(dir_to_publish)

    async def _poetry_publish(self, dir_to_publish: Directory) -> StepResult:
        pypi_token = self.context.dagger_client.set_secret("pypi_token", f"pypi-{self.context.pypi_token}")
        pyproject_toml = dir_to_publish.file(PYPROJECT_TOML_FILE_PATH)
        pyproject_toml_content = await pyproject_toml.contents()
        contents = tomli.loads(pyproject_toml_content)
        # make sure package name and version are set to the configured one
        contents["tool"]["poetry"]["name"] = self.context.package_name
        contents["tool"]["poetry"]["version"] = self.context.version
        # enforce consistent author
        contents["tool"]["poetry"]["authors"] = ["Airbyte <contact@airbyte.io>"]
        poetry_publish = (
            self._get_base_container()
            .with_secret_variable("PYPI_TOKEN", pypi_token)
            .with_directory("package", dir_to_publish)
            .with_workdir("package")
            .with_new_file(PYPROJECT_TOML_FILE_PATH, contents=tomli_w.dumps(contents))
            .with_exec(["poetry", "config", "repositories.mypypi", self.context.registry])
            .with_exec(sh_dash_c(["poetry config pypi-token.mypypi $PYPI_TOKEN"]))
            .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
            .with_exec(sh_dash_c(["poetry publish --build --repository mypypi -vvv --no-interaction"]))
        )

        return await self.get_step_result(poetry_publish)

    async def _pip_publish(self, dir_to_publish: Directory) -> StepResult:
        files = await dir_to_publish.entries()
        pypi_username = self.context.dagger_client.set_secret("pypi_username", "__token__")
        pypi_password = self.context.dagger_client.set_secret("pypi_password", f"pypi-{self.context.pypi_token}")
        metadata: Dict[str, str] = {
            "name": str(self.context.package_name),
            "version": str(self.context.version),
            # Enforce consistent author
            "author": "Airbyte",
            "author_email": "contact@airbyte.io",
        }
        if "README.md" in files:
            metadata["long_description"] = await dir_to_publish.file("README.md").contents()
            metadata["long_description_content_type"] = "text/markdown"

        config = configparser.ConfigParser()
        config["metadata"] = metadata

        setup_cfg_io = io.StringIO()
        config.write(setup_cfg_io)
        setup_cfg = setup_cfg_io.getvalue()

        twine_upload = (
            self._get_base_container()
            .with_exec(sh_dash_c(["apt-get update", "apt-get install -y twine"]))
            .with_directory("package", dir_to_publish)
            .with_workdir("package")
            # clear out setup.py metadata so setup.cfg is used
            .with_exec(["sed", "-i", "/name=/d; /author=/d; /author_email=/d; /version=/d", SETUP_PY_FILE_PATH])
            .with_new_file("setup.cfg", contents=setup_cfg)
            .with_exec(["pip", "install", "--upgrade", "setuptools", "wheel"])
            .with_exec(["python", SETUP_PY_FILE_PATH, "sdist", "bdist_wheel"])
            .with_secret_variable("TWINE_USERNAME", pypi_username)
            .with_secret_variable("TWINE_PASSWORD", pypi_password)
            .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
            .with_exec(["twine", "upload", "--verbose", "--repository-url", self.context.registry, "dist/*"])
        )

        return await self.get_step_result(twine_upload)
