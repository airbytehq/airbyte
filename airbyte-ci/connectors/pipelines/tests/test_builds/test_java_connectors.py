#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import random
import tarfile

import dagger
import pytest
from pipelines import bases
from pipelines.builds import java_connectors
from pipelines.contexts import ConnectorContext

pytestmark = [
    pytest.mark.anyio,
]


class TestBuildConnectorDistributionTar:

    STABLE_SOURCE_CONNECTORS = ["source-postgres"]
    STABLE_DESTINATION_CONNECTORS = ["destination-bigquery"]

    def test_attributes(self):
        assert java_connectors.BuildConnectorDistributionTar.gradle_task_name == "distTar"
        assert java_connectors.BuildConnectorDistributionTar.title == "Build connector tar"

    @staticmethod
    def get_context_for_connector(dagger_client: dagger.Client, connector: bases.ConnectorWithModifiedFiles) -> ConnectorContext:
        context = ConnectorContext(
            pipeline_name="test",
            connector=connector,
            is_local=True,
            git_branch="test",
            git_revision="123",
            report_output_prefix="test",
        )
        context.dagger_client = dagger_client
        return context

    @pytest.fixture
    def stable_source_connector(self) -> bases.ConnectorWithModifiedFiles:
        return bases.ConnectorWithModifiedFiles(random.choice(self.STABLE_SOURCE_CONNECTORS), frozenset())

    @pytest.fixture
    def stable_destination_connector(self) -> bases.ConnectorWithModifiedFiles:
        return bases.ConnectorWithModifiedFiles(random.choice(self.STABLE_DESTINATION_CONNECTORS), frozenset())

    async def test__prepare_container_for_build(self, dagger_client, stable_source_connector):
        context = self.get_context_for_connector(dagger_client, stable_source_connector)
        step = java_connectors.BuildConnectorDistributionTar(context)
        container = await step._prepare_container_for_build()
        container_code_directory_content = await container.directory(str(context.connector.code_directory)).entries()
        assert "build" not in container_code_directory_content
        assert "Dockerfile" not in container_code_directory_content
        assert "build.gradle" in container_code_directory_content

    async def test__get_container_with_built_tar_failure(self, mocker, dagger_client, stable_source_connector):
        mocker.patch.object(java_connectors.BuildConnectorDistributionTar, "_get_gradle_command", side_effect="exit 1")

        context = self.get_context_for_connector(dagger_client, stable_source_connector)
        step = java_connectors.BuildConnectorDistributionTar(context)
        # Awaiting this coroutine should not evaluate the exit 1 command
        # Awaiting the container returned by this coroutine should evaluate the exit 1 command and raise an ExecError
        with_built_tar = await step._get_container_with_built_tar()
        with pytest.raises(dagger.ExecError):
            await with_built_tar

    @pytest.mark.slow
    async def test__get_container_with_built_tar_success(self, dagger_client, stable_source_connector):
        context = self.get_context_for_connector(dagger_client, stable_source_connector)
        step = java_connectors.BuildConnectorDistributionTar(context)
        with_built_tar = await step._get_container_with_built_tar()
        current_workdir = await with_built_tar.workdir()
        assert current_workdir == f"/airbyte/{str(context.connector.code_directory)}/build/distributions"
        distributions_entries = await with_built_tar.directory(current_workdir).entries()
        assert len(distributions_entries) == 1
        assert distributions_entries[0].endswith(".tar")
        assert distributions_entries[0].startswith(f"{context.connector.technical_name}-")
        assert "BUILD SUCCESSFUL" in await with_built_tar.stdout()

    async def test__run_failure(self, mocker, dagger_client, stable_source_connector):
        mocker.patch.object(java_connectors.BuildConnectorDistributionTar, "_get_gradle_command", side_effect="exit 1")
        context = self.get_context_for_connector(dagger_client, stable_source_connector)
        step = java_connectors.BuildConnectorDistributionTar(context)
        result = await step._run()
        assert result.status == bases.StepStatus.FAILURE
        assert isinstance(result.output_artifact, dagger.Container)

    async def test__run_failure_multiple_tars(self, mocker, dagger_client, stable_source_connector):
        context = self.get_context_for_connector(dagger_client, stable_source_connector)
        container_with_multiple_tars = dagger_client.container().from_("bash").with_exec(["-c", "touch a.tar && touch b.tar"])
        mocker.patch.object(
            java_connectors.BuildConnectorDistributionTar, "_get_container_with_built_tar", return_value=container_with_multiple_tars
        )
        mocker.patch.object(
            java_connectors.BuildConnectorDistributionTar, "get_step_result", return_value=mocker.Mock(status=bases.StepStatus.SUCCESS)
        )

        step = java_connectors.BuildConnectorDistributionTar(context)
        result = await step._run()
        assert result.status == bases.StepStatus.FAILURE
        assert (
            result.stderr
            == "The distributions directory contains multiple connector tar files. We can't infer which one should be used. Please review and delete any unnecessary tar files."
        )
        assert not result.output_artifact

    @pytest.mark.slow
    @pytest.mark.parametrize("connector_type", ["source", "destination"])
    async def test__run_success(self, dagger_client, connector_type, tmpdir, stable_source_connector, stable_destination_connector):
        if connector_type == "source":
            connector = stable_source_connector
        else:
            connector = stable_destination_connector

        context = self.get_context_for_connector(dagger_client, connector)
        step = java_connectors.BuildConnectorDistributionTar(context)
        result = await step._run()
        assert result.status == bases.StepStatus.SUCCESS
        assert "BUILD SUCCESSFUL" in result.stdout
        assert isinstance(result.output_artifact, dagger.File)
        local_tar_path = str(tmpdir / f"{context.connector.technical_name}.tar")
        assert await result.output_artifact.export(local_tar_path)
        with tarfile.open(local_tar_path, mode="r") as tar:
            tar.extractall(path=tmpdir)
            extracted_files = tar.getnames()
        assert extracted_files
        assert extracted_files[0].startswith(f"{context.connector.technical_name}-")
