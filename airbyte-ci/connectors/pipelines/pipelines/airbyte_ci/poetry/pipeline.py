#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import tomli
import tomli_w
from typing import Optional
import configparser
import io

from pipelines.airbyte_ci.connectors.context import PipelineContext
from pipelines.models.steps import Step, StepResult
from pipelines.models.contexts.pipeline_context import PipelineContext



from textwrap import dedent


class PyPIPublishContext(PipelineContext):
    def __init__(
        self,
        pypi_token: str,
        test_pypi: bool,
        package_path: str,
        build_docker_image: str,
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
        self.pypi_token = pypi_token
        self.test_pypi = test_pypi
        self.package_path = package_path
        self.package_name = package_name
        self.version = version
        self.build_docker_image = build_docker_image

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
        
        files = await dir_to_publish.entries()
        is_poetry_package = "pyproject.toml" in files
        is_pip_package = "setup.py" in files

        if not context.package_name or not context.version:
            # check whether it has a pyproject.toml file
            if not is_poetry_package:
                return self.skip("Connector does not have a pyproject.toml file and version and package name is not set otherwise, skipping.")
            
            # get package name and version from pyproject.toml
            pyproject_toml = dir_to_publish.file("pyproject.toml")
            pyproject_toml_content = await pyproject_toml.contents()
            contents = tomli.loads(pyproject_toml_content)
            if "tool" not in contents or "poetry" not in contents["tool"] or "name" not in contents["tool"]["poetry"] or "version" not in contents["tool"]["poetry"]:
                return self.skip("Connector does not have a pyproject.toml file which specifies package name and version and they are not set otherwise, skipping.")
            
            context.package_name = contents["tool"]["poetry"]["name"]
            context.version = contents["tool"]["poetry"]["version"]


        print(f"Uploading package {context.package_name} version {context.version} to {'testpypi' if context.test_pypi else 'pypi'}...")
        
        if is_pip_package:
            pypi_username = self.context.dagger_client.set_secret("pypi_username", "__token__")
            pypi_password = self.context.dagger_client.set_secret("pypi_password", f"pypi-{context.pypi_token}")
            metadata = {
                "name": context.package_name,
                "version": context.version,
                "author": "Airbyte",
                "author_email": "contact@airbyte.io",
            }
            if "README.md" in files:
                metadata["long_description"] = await dir_to_publish.file("README.md").contents()
                metadata["long_description_content_type"] = "text/markdown"

            # legacy publish logic
            config = configparser.ConfigParser()
            config["metadata"] = metadata

            setup_cfg_io = io.StringIO()
            config.write(setup_cfg_io)
            setup_cfg = setup_cfg_io.getvalue()

            twine_upload = (
                self.context.dagger_client.container()
                .from_(context.build_docker_image)
                .with_exec(["apt-get", "update"])
                .with_exec(["apt-get", "install", "-y", "twine"])
                .with_directory("package", dir_to_publish)
                .with_workdir("package")
                # clear out setup.py metadata so setup.cfg is used
                .with_exec(["sed", "-i", "/name=/d; /author=/d; /author_email=/d; /version=/d", "setup.py"])
                .with_new_file("setup.cfg", contents=setup_cfg)
                .with_exec(["pip", "install", "--upgrade", "setuptools", "wheel"])
                .with_exec(["python", "setup.py", "sdist", "bdist_wheel"])
                .with_secret_variable("TWINE_USERNAME", pypi_username)
                .with_secret_variable("TWINE_PASSWORD", pypi_password)
                .with_exec(["twine", "upload", "--verbose", "--repository", "testpypi" if context.test_pypi else "pypi", "dist/*"])
            )

            return await self.get_step_result(twine_upload)
        else:
            pypi_token = self.context.dagger_client.set_secret("pypi_token", f"pypi-{context.pypi_token}")
            pyproject_toml = dir_to_publish.file("pyproject.toml")
            pyproject_toml_content = await pyproject_toml.contents()
            contents = tomli.loads(pyproject_toml_content)
            # set package name and version
            contents["tool"]["poetry"]["name"] = context.package_name
            contents["tool"]["poetry"]["version"] = context.version
            # poetry publish logic
            poetry_publish = (
                self.context.dagger_client.container()
                .from_(context.build_docker_image)
                .with_secret_variable("PYPI_TOKEN", pypi_token)
                .with_directory("package", dir_to_publish)
                .with_workdir("package")
                .with_new_file("pyproject.toml", contents=tomli_w.dumps(contents))
                .with_exec(["poetry", "config", "repositories.testpypi", "https://test.pypi.org/legacy/"])
                .with_exec(["sh", "-c", f"poetry config {'pypi-token.testpypi' if context.test_pypi else 'pypi-token.pypi'} $PYPI_TOKEN"])
                .with_exec(["poetry", "publish", "--build", "--repository", "testpypi" if context.test_pypi else "pypi"])
            )

            return await self.get_step_result(poetry_publish)


