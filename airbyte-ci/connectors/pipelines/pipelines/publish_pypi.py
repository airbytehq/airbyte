#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from textwrap import dedent
from typing import List

import anyio
from connector_ops.utils import ConnectorLanguage
from pipelines.bases import ConnectorReport, Step, StepResult, StepStatus
from pipelines.contexts import PublishConnectorContext
from pipelines.pipelines import metadata


class PublishPyPIConnector(Step):
    title = "Publish connector to PyPI"

    async def _run(self) -> StepResult:
        if self.context.connector.language not in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
            return self.skip("Only Python connectors can be published to PyPI.")

        setup_cfg = dedent(
            f"""
            [metadata]
            name = airbyte-{self.context.connector.technical_name}
            version = {self.context.connector.version}
            author = Airbyte
            author_email = contact@airbyte.io
        """
        )

        twine_username = self.context.dagger_client.set_secret("twine_username", self.context.pypi_username)
        twine_password = self.context.dagger_client.set_secret("twine_password", self.context.pypi_password)

        twine_upload = await (
            self.context.dagger_client.container()
            .from_("python:3.10-slim")
            .with_exec(["apt-get", "update"])
            .with_exec(["apt-get", "install", "-y", "twine"])
            .with_directory("connector", (await self.context.get_connector_dir(exclude=["dist"])))
            .with_workdir("connector")
            .with_exec(["sed", "-i", "/name=/d; /author=/d; /author_email=/d; /version=/d", "setup.py"])
            .with_new_file("setup.cfg", setup_cfg)
            .with_exec(["pip", "install", "--upgrade", "setuptools", "wheel"])
            .with_exec(["python", "setup.py", "sdist", "bdist_wheel"])
            .with_secret_variable("TWINE_USERNAME", twine_username)
            .with_secret_variable("TWINE_PASSWORD", twine_password)
            .with_exec(["twine", "upload", "--verbose", "--repository", self.context.pypi_repository, "dist/*"])
        )

        return self.get_step_result(twine_upload)


async def run_connector_pypi_publish_pipeline(context: PublishConnectorContext, semaphore: anyio.Semaphore) -> ConnectorReport:
    """Run a publish pipeline for a single connector.

    1. Validate the metadata file.
    2. Build and publish the connector to PyPI.

    Returns:
        ConnectorReport: The reports holding publish results.
    """

    def create_connector_report(results: List[StepResult]) -> ConnectorReport:
        report = ConnectorReport(context, results, name="PYPI PUBLISH RESULTS")
        context.report = report
        return report

    async with semaphore:
        async with context:
            results = []

            metadata_validation_results = await metadata.MetadataValidation(context, context.metadata_path).run()
            results.append(metadata_validation_results)

            # Exit early if the metadata file is invalid.
            if metadata_validation_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results)

            publish_pypi_results = await PublishPyPIConnector(context).run()
            results.append(publish_pypi_results)

            return create_connector_report(results)
