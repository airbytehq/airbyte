#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import configparser
import io
import uuid
from enum import Enum, auto
from typing import Dict, Optional

import tomli
import tomli_w
from dagger import Container, Directory
from pipelines.consts import PYPROJECT_TOML_FILE_PATH, SETUP_PY_FILE_PATH
from pipelines.dagger.actions.python.poetry import with_poetry
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.contexts.python_registry_publish import PythonPackageMetadata, PythonRegistryPublishContext
from pipelines.models.steps import Step, StepResult


class PackageType(Enum):
    POETRY = auto()
    PIP = auto()


class PublishToPythonRegistry(Step):
    context: PythonRegistryPublishContext
    title = "Publish package to python registry"
    max_retries = 3

    def _get_base_container(self) -> Container:
        return with_poetry(self.context)

    async def _get_package_metadata_from_pyproject_toml(self, package_dir_to_publish: Directory) -> Optional[PythonPackageMetadata]:
        pyproject_toml = package_dir_to_publish.file(PYPROJECT_TOML_FILE_PATH)
        pyproject_toml_content = await pyproject_toml.contents()
        contents = tomli.loads(pyproject_toml_content)
        try:
            return PythonPackageMetadata(contents["tool"]["poetry"]["name"], contents["tool"]["poetry"]["version"])
        except KeyError:
            return None

    async def _get_package_type(self, package_dir_to_publish: Directory) -> Optional[PackageType]:
        files = await package_dir_to_publish.entries()
        has_pyproject_toml = PYPROJECT_TOML_FILE_PATH in files
        has_setup_py = SETUP_PY_FILE_PATH in files
        if has_pyproject_toml:
            return PackageType.POETRY
        elif has_setup_py:
            return PackageType.PIP
        else:
            return None

    async def _run(self) -> StepResult:
        package_dir_to_publish = await self.context.get_repo_dir(self.context.package_path)
        package_type = await self._get_package_type(package_dir_to_publish)

        if not package_type:
            return self.skip("Connector does not have a pyproject.toml file or setup.py file, skipping.")

        result = await self._ensure_package_name_and_version(package_dir_to_publish, package_type)
        if result:
            return result

        self.logger.info(
            f"Uploading package {self.context.package_metadata.name} version {self.context.package_metadata.version} to {self.context.registry}..."
        )

        return await self._publish(package_dir_to_publish, package_type)

    async def _ensure_package_name_and_version(self, package_dir_to_publish: Directory, package_type: PackageType) -> Optional[StepResult]:
        """
        Try to infer package name and version from the pyproject.toml file. If it is not present, we need to have the package name and version set.
        Setup.py packages need to set package name and version as parameter.

        Returns None if package name and version are set, otherwise a StepResult with a skip message.
        """
        if self.context.package_metadata.name and self.context.package_metadata.version:
            return None

        if package_type is not PackageType.POETRY:
            return self.skip("Connector does not have a pyproject.toml file and version and package name is not set otherwise, skipping.")

        inferred_package_metadata = await self._get_package_metadata_from_pyproject_toml(package_dir_to_publish)

        if not inferred_package_metadata:
            return self.skip(
                "Connector does not have a pyproject.toml file which specifies package name and version and they are not set otherwise, skipping."
            )

        if not self.context.package_metadata.name:
            self.context.package_metadata.name = inferred_package_metadata.name
        if not self.context.package_metadata.version:
            self.context.package_metadata.version = inferred_package_metadata.version

        return None

    async def _publish(self, package_dir_to_publish: Directory, package_type: PackageType) -> StepResult:
        if package_type is PackageType.PIP:
            return await self._pip_publish(package_dir_to_publish)
        else:
            return await self._poetry_publish(package_dir_to_publish)

    async def _poetry_publish(self, package_dir_to_publish: Directory) -> StepResult:
        pyproject_toml = package_dir_to_publish.file(PYPROJECT_TOML_FILE_PATH)
        pyproject_toml_content = await pyproject_toml.contents()
        contents = tomli.loads(pyproject_toml_content)
        # make sure package name and version are set to the configured one
        contents["tool"]["poetry"]["name"] = self.context.package_metadata.name
        contents["tool"]["poetry"]["version"] = self.context.package_metadata.version
        # enforce consistent author
        contents["tool"]["poetry"]["authors"] = ["Airbyte <contact@airbyte.io>"]
        poetry_publish = (
            self._get_base_container()
            .with_secret_variable("PYTHON_REGISTRY_TOKEN", self.context.python_registry_token.as_dagger_secret(self.dagger_client))
            .with_directory("package", package_dir_to_publish)
            .with_workdir("package")
            .with_new_file(PYPROJECT_TOML_FILE_PATH, contents=tomli_w.dumps(contents))
            # Make sure these steps are always executed and not cached as they are triggering a side-effect (calling the registry)
            # Env var setting needs to be in this block as well to make sure a change of the env var will be propagated correctly
            .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
            .with_exec(["poetry", "config", "repositories.mypypi", self.context.registry], use_entrypoint=True)
            .with_exec(sh_dash_c(["poetry config pypi-token.mypypi $PYTHON_REGISTRY_TOKEN"]))
            # Default timeout is set to 15 seconds
            # We sometime face 443 HTTP read timeout responses from PyPi
            # Setting it to 60 seconds to avoid transient publish failures
            .with_env_variable("POETRY_REQUESTS_TIMEOUT", "60")
            .with_exec(sh_dash_c(["poetry publish --build --repository mypypi -vvv --no-interaction"]))
        )

        return await self.get_step_result(poetry_publish)

    async def _pip_publish(self, package_dir_to_publish: Directory) -> StepResult:
        files = await package_dir_to_publish.entries()
        metadata: Dict[str, str] = {
            "name": str(self.context.package_metadata.name),
            "version": str(self.context.package_metadata.version),
            # Enforce consistent author
            "author": "Airbyte",
            "author_email": "contact@airbyte.io",
        }
        if "README.md" in files:
            metadata["long_description"] = await package_dir_to_publish.file("README.md").contents()
            metadata["long_description_content_type"] = "text/markdown"

        config = configparser.ConfigParser()
        config["metadata"] = metadata

        setup_cfg_io = io.StringIO()
        config.write(setup_cfg_io)
        setup_cfg = setup_cfg_io.getvalue()

        twine_upload = (
            self._get_base_container()
            .with_exec(sh_dash_c(["apt-get update", "apt-get install -y twine"]))
            .with_directory("package", package_dir_to_publish)
            .with_workdir("package")
            .with_exec(["sed", "-i", "/name=/d; /author=/d; /author_email=/d; /version=/d", SETUP_PY_FILE_PATH], use_entrypoint=True)
            .with_new_file("setup.cfg", contents=setup_cfg)
            .with_exec(["pip", "install", "--upgrade", "setuptools", "wheel"], use_entrypoint=True)
            .with_exec(["python", SETUP_PY_FILE_PATH, "sdist", "bdist_wheel"], use_entrypoint=True)
            # Make sure these steps are always executed and not cached as they are triggering a side-effect (calling the registry)
            # Env var setting needs to be in this block as well to make sure a change of the env var will be propagated correctly
            .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
            .with_secret_variable("TWINE_USERNAME", self.context.dagger_client.set_secret("pypi_username", "__token__"))
            .with_secret_variable("TWINE_PASSWORD", self.context.python_registry_token.as_dagger_secret(self.dagger_client))
            .with_exec(["twine", "upload", "--verbose", "--repository-url", self.context.registry, "dist/*"], use_entrypoint=True)
        )

        return await self.get_step_result(twine_upload)
