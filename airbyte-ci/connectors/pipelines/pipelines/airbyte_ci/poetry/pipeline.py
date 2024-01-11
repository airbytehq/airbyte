#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import tomli
import uuid
from typing import Optional

import dagger
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.steps.docker import SimpleDockerStep
from pipelines.airbyte_ci.steps.poetry import PoetryRunStep
from pipelines.consts import DOCS_DIRECTORY_ROOT_PATH, INTERNAL_TOOL_PATHS
from pipelines.dagger.actions.python.common import with_pip_packages
from pipelines.dagger.containers.python import with_python_base
from pipelines.helpers.run_steps import STEP_TREE, StepToRun, run_steps
from pipelines.helpers.utils import get_file_contents
from pipelines.models.reports import Report
from pipelines.models.steps import MountPath, Step, StepResult
from pipelines.models.contexts.pipeline_context import PipelineContext



from textwrap import dedent
from typing import List

import anyio


class PyPIPublishContext(PipelineContext):
    def __init__(
        self,
        pypi_username: str,
        pypi_password: str,
        pypi_repository: str,
        package_path: str,
        ci_report_bucket: str,
        report_output_prefix: str,
        is_local: bool,
        git_branch: bool,
        git_revision: bool,
        gha_workflow_run_url: Optional[str] = None,
        dagger_logs_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
        ci_gcs_credentials: str = None,
        package_name: Optional[str] = None,
        version: Optional[str] = None,
    ):
        self.pypi_username = pypi_username
        self.pypi_password = pypi_password
        self.pypi_repository = pypi_repository
        self.package_path = package_path
        self.package_name = package_name
        self.version = version

        pipeline_name = f"Publish PyPI {package_path}"

        super().__init__(
            pipeline_name=pipeline_name,
            report_output_prefix=report_output_prefix,
            ci_report_bucket=ci_report_bucket,
            is_local=is_local,
            git_branch=git_branch,
            git_revision=git_revision,
            gha_workflow_run_url=gha_workflow_run_url,
            dagger_logs_url=dagger_logs_url,
            pipeline_start_timestamp=pipeline_start_timestamp,
            ci_context=ci_context,
            ci_gcs_credentials=ci_gcs_credentials,
        )


class PublishToPyPI(Step):
    title = "Publish package to PyPI"

    async def _run(self) -> StepResult:
        context: PyPIPublishContext = self.context # TODO: Add logic to create a PyPIPublishContext out of a ConnectorContext (check the instance type to decide whether it's necessary)
        dir_to_publish = await context.get_repo_dir(context.package_path)

        if not context.package_name or not context.version:
            # check whether it has a pyproject.toml file
            if "pyproject.toml" not in (await dir_to_publish.entries()):
                return self.skip("Connector does not have a pyproject.toml file and version and package name is not set otherwise, skipping.")
            
            # get package name and version from pyproject.toml
            pyproject_toml = dir_to_publish.file("pyproject.toml")
            pyproject_toml_content = await pyproject_toml.contents()
            contents = tomli.loads(pyproject_toml_content)
            if "tool" not in contents or "poetry" not in contents["tool"] or "name" not in contents["tool"]["poetry"] or "version" not in contents["tool"]["poetry"]:
                return self.skip("Connector does not have a pyproject.toml file with a poetry section, skipping.")
            
            context.package_name = contents["tool"]["poetry"]["name"]
            context.version = contents["tool"]["poetry"]["version"]

        setup_cfg = dedent(
            f"""
            [metadata]
            name = {context.package_name}
            version = {context.version}
            author = Airbyte
            author_email = contact@airbyte.io
        """
        )

        twine_username = self.context.dagger_client.set_secret("twine_username", context.pypi_username)
        twine_password = self.context.dagger_client.set_secret("twine_password", context.pypi_password)

        twine_upload = (
            self.context.dagger_client.container()
            .from_("python:3.10-slim")
            .with_exec(["apt-get", "update"])
            .with_exec(["apt-get", "install", "-y", "twine"])
            .with_directory("package", dir_to_publish)
            .with_workdir("package")
            .with_exec(["sed", "-i", "/name=/d; /author=/d; /author_email=/d; /version=/d", "setup.py"])
            .with_new_file("setup.cfg", contents=setup_cfg)
            .with_exec(["pip", "install", "--upgrade", "setuptools", "wheel"])
            .with_exec(["python", "setup.py", "sdist", "bdist_wheel"])
            .with_secret_variable("TWINE_USERNAME", twine_username)
            .with_secret_variable("TWINE_PASSWORD", twine_password)
            .with_exec(["twine", "upload", "--verbose", "--repository", self.context.pypi_repository, "dist/*"])
        )

        return await self.get_step_result(twine_upload)

