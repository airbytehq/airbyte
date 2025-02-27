#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import os
import random
from typing import List

import anyio
import pytest

from pipelines.airbyte_ci.connectors.publish import pipeline as publish_pipeline
from pipelines.airbyte_ci.connectors.publish.context import RolloutMode
from pipelines.models.steps import StepStatus

pytestmark = [
    pytest.mark.anyio,
]


@pytest.fixture
def publish_context(mocker, dagger_client, tmpdir):
    return mocker.MagicMock(
        dagger_client=dagger_client,
        get_connector_dir=mocker.MagicMock(return_value=dagger_client.host().directory(str(tmpdir))),
        docker_hub_username=None,
        docker_hub_password=None,
        docker_image="hello-world:latest",
        rollout_mode=RolloutMode.PUBLISH,
    )


class TestCheckConnectorImageDoesNotExists:
    @pytest.fixture(scope="class")
    def three_random_connectors_image_names(self, oss_registry: dict) -> List[str]:
        connectors = oss_registry["sources"] + oss_registry["destinations"]
        random.shuffle(connectors)
        return [f"{connector['dockerRepository']}:{connector['dockerImageTag']}" for connector in connectors[:3]]

    async def test_run_skipped_when_already_published(self, three_random_connectors_image_names, publish_context):
        """We pick three random connectors from the OSS registry. They should be published. We check that the step is skipped."""
        for image_name in three_random_connectors_image_names:
            publish_context.docker_image = image_name
            step = publish_pipeline.CheckConnectorImageDoesNotExist(publish_context)
            step_result = await step.run()
            assert step_result.status == StepStatus.SKIPPED

    async def test_run_success_when_already_published(self, publish_context):
        publish_context.docker_image = "airbyte/source-pokeapi:0.0.0"
        step = publish_pipeline.CheckConnectorImageDoesNotExist(publish_context)
        step_result = await step.run()
        assert step_result.status == StepStatus.SUCCESS


class TestUploadSpecToCache:
    @pytest.fixture(scope="class")
    def random_connector(self, oss_registry: dict) -> dict:
        connectors = oss_registry["sources"] + oss_registry["destinations"]
        random.shuffle(connectors)
        return connectors[0]

    @pytest.mark.parametrize(
        "valid_spec, successful_upload",
        [
            [True, True],
            [False, True],
            [True, False],
            [False, False],
        ],
    )
    async def test_run(self, mocker, dagger_client, valid_spec, successful_upload, random_connector, publish_context):
        """Test that the spec is correctly uploaded to the spec cache bucket.
        We pick a random connector from the oss registry, by nature this connector should have a valid spec and be published.
        We load this connector as a Dagger container and run spec against it.
        We validate that the outputted spec is the same as the one in the OSS registry.
        We also artificially set the spec to be invalid and check that the step fails.
        """
        image_name = f"{random_connector['dockerRepository']}:{random_connector['dockerImageTag']}"
        publish_context.docker_image = image_name
        expected_spec = random_connector["spec"]
        connector_container = dagger_client.container().from_(image_name)

        upload_exit_code = 0 if successful_upload else 1
        mocker.patch.object(
            publish_pipeline,
            "upload_to_gcs",
            mocker.AsyncMock(return_value=(upload_exit_code, "upload_to_gcs_stdout", "upload_to_gcs_stderr")),
        )
        if not valid_spec:
            mocker.patch.object(
                publish_pipeline.UploadSpecToCache,
                "_get_connector_spec",
                mocker.Mock(side_effect=publish_pipeline.InvalidSpecOutputError("Invalid spec.")),
            )

        step = publish_pipeline.UploadSpecToCache(publish_context)
        step_result = await step.run(connector_container)
        if valid_spec:
            # First call should be for OSS spec
            publish_pipeline.upload_to_gcs.assert_any_call(
                publish_context.dagger_client,
                mocker.ANY,
                f"specs/{image_name.replace(':', '/')}/spec.json",
                publish_context.spec_cache_bucket_name,
                publish_context.spec_cache_gcs_credentials,
                flags=['--cache-control="no-cache"'],
            )

            # Second call should be for Cloud spec if different from OSS
            cloud_spec = await step._get_connector_spec(connector_container, "CLOUD")
            oss_spec = await step._get_connector_spec(connector_container, "OSS")
            if cloud_spec != oss_spec:
                publish_pipeline.upload_to_gcs.assert_any_call(
                    publish_context.dagger_client,
                    mocker.ANY,
                    f"specs/{image_name.replace(':', '/')}/spec.cloud.json",
                    publish_context.spec_cache_bucket_name,
                    publish_context.spec_cache_gcs_credentials,
                    flags=['--cache-control="no-cache"'],
                )

            spec_file = publish_pipeline.upload_to_gcs.call_args.args[1]
            uploaded_content = await spec_file.contents()
            assert json.loads(uploaded_content) == expected_spec

        if successful_upload and valid_spec:
            assert step_result.status == StepStatus.SUCCESS
            assert step_result.stdout == "Uploaded connector spec to spec cache bucket."
            assert step_result.stderr is None
        if valid_spec and not successful_upload:
            assert step_result.status == StepStatus.FAILURE
            assert step_result.stdout == "upload_to_gcs_stdout"
            assert step_result.stderr == "upload_to_gcs_stderr"
        if (not valid_spec and successful_upload) or (not valid_spec and not successful_upload):
            assert step_result.status == StepStatus.FAILURE
            assert step_result.stderr == "Invalid spec."
            assert step_result.stdout is None
            publish_pipeline.upload_to_gcs.assert_not_called()

    def test_parse_spec_output_valid(self, publish_context, random_connector):
        step = publish_pipeline.UploadSpecToCache(publish_context)
        correct_spec_message = json.dumps({"type": "SPEC", "spec": random_connector["spec"]})
        spec_output = f'random_stuff\n{{"type": "RANDOM_MESSAGE"}}\n{correct_spec_message}'
        result = step._parse_spec_output(spec_output)
        assert json.loads(result) == random_connector["spec"]

    def test_parse_spec_output_invalid_json(self, publish_context):
        step = publish_pipeline.UploadSpecToCache(publish_context)
        spec_output = "Invalid JSON"
        with pytest.raises(publish_pipeline.InvalidSpecOutputError):
            step._parse_spec_output(spec_output)

    def test_parse_spec_output_invalid_key(self, publish_context):
        step = publish_pipeline.UploadSpecToCache(publish_context)
        spec_output = '{"type": "SPEC", "spec": {"invalid_key": "value"}}'
        with pytest.raises(publish_pipeline.InvalidSpecOutputError):
            step._parse_spec_output(spec_output)

    def test_parse_spec_output_no_spec(self, publish_context):
        step = publish_pipeline.UploadSpecToCache(publish_context)
        spec_output = '{"type": "OTHER"}'
        with pytest.raises(publish_pipeline.InvalidSpecOutputError):
            step._parse_spec_output(spec_output)


STEPS_TO_PATCH = [
    (publish_pipeline, "MetadataValidation"),
    (publish_pipeline, "MetadataUpload"),
    (publish_pipeline, "CheckConnectorImageDoesNotExist"),
    (publish_pipeline, "UploadSpecToCache"),
    (publish_pipeline, "PushConnectorImageToRegistry"),
    (publish_pipeline, "PullConnectorImageFromRegistry"),
    (publish_pipeline.steps, "run_connector_build"),
    (publish_pipeline, "CheckPythonRegistryPackageDoesNotExist"),
    (publish_pipeline, "UploadSbom"),
]


@pytest.mark.parametrize("pre_release", [True, False])
async def test_run_connector_publish_pipeline_when_failed_validation(mocker, pre_release):
    """We validate that no other steps are called if the metadata validation step fails."""
    for module, to_mock in STEPS_TO_PATCH:
        mocker.patch.object(module, to_mock, return_value=mocker.AsyncMock())

    run_metadata_validation = publish_pipeline.MetadataValidation.return_value.run
    run_metadata_validation.return_value = mocker.Mock(status=StepStatus.FAILURE)

    context = mocker.MagicMock(pre_release=pre_release, rollout_mode=RolloutMode.PUBLISH)
    semaphore = anyio.Semaphore(1)
    report = await publish_pipeline.run_connector_publish_pipeline(context, semaphore)
    run_metadata_validation.assert_called_once()

    # Check that nothing else is called
    for module, to_mock in STEPS_TO_PATCH:
        if to_mock != "MetadataValidation":
            getattr(module, to_mock).return_value.run.assert_not_called()

    assert (
        report.steps_results
        == context.report.steps_results
        == [
            run_metadata_validation.return_value,
        ]
    )


@pytest.mark.parametrize(
    "check_image_exists_status",
    [StepStatus.SKIPPED, StepStatus.FAILURE],
)
async def test_run_connector_publish_pipeline_when_image_exists_or_failed(mocker, check_image_exists_status, publish_context):
    """We validate that when the connector image exists or the check fails, we don't run the rest of the pipeline.
    We also validate that the metadata upload step is called when the image exists (Skipped status).
    We do this to ensure that the metadata is still updated in the case where the connector image already exists.
    It's the role of the metadata service upload command to actually upload the file if the metadata has changed.
    But we check that the metadata upload step does not happen if the image check fails (Failure status).
    """
    for module, to_mock in STEPS_TO_PATCH:
        mocker.patch.object(module, to_mock, return_value=mocker.AsyncMock())

    run_metadata_validation = publish_pipeline.MetadataValidation.return_value.run
    run_metadata_validation.return_value = mocker.Mock(status=StepStatus.SUCCESS)

    # ensure spec and sbom upload always succeeds
    run_upload_spec_to_cache = publish_pipeline.UploadSpecToCache.return_value.run
    run_upload_spec_to_cache.return_value = mocker.Mock(status=StepStatus.SUCCESS)
    run_upload_sbom = publish_pipeline.UploadSbom.return_value.run
    run_upload_sbom.return_value = mocker.Mock(status=StepStatus.SUCCESS)

    run_check_connector_image_does_not_exist = publish_pipeline.CheckConnectorImageDoesNotExist.return_value.run
    run_check_connector_image_does_not_exist.return_value = mocker.Mock(status=check_image_exists_status)

    run_metadata_upload = publish_pipeline.MetadataUpload.return_value.run

    semaphore = anyio.Semaphore(1)
    report = await publish_pipeline.run_connector_publish_pipeline(publish_context, semaphore)
    run_metadata_validation.assert_called_once()
    run_check_connector_image_does_not_exist.assert_called_once()

    # Check that nothing else is called
    for module, to_mock in STEPS_TO_PATCH:
        if to_mock not in ["MetadataValidation", "MetadataUpload", "CheckConnectorImageDoesNotExist", "UploadSpecToCache", "UploadSbom"]:
            getattr(module, to_mock).return_value.run.assert_not_called()

    if check_image_exists_status is StepStatus.SKIPPED:
        run_metadata_upload.assert_called_once()
        assert (
            report.steps_results
            == publish_context.report.steps_results
            == [
                run_metadata_validation.return_value,
                run_check_connector_image_does_not_exist.return_value,
                run_upload_spec_to_cache.return_value,
                run_upload_sbom.return_value,
                run_metadata_upload.return_value,
            ]
        )

    if check_image_exists_status is StepStatus.FAILURE:
        run_metadata_upload.assert_not_called()
        assert (
            report.steps_results
            == publish_context.report.steps_results
            == [
                run_metadata_validation.return_value,
                run_check_connector_image_does_not_exist.return_value,
            ]
        )


@pytest.mark.parametrize(
    "pre_release, build_step_status, push_step_status, pull_step_status, upload_to_spec_cache_step_status, metadata_upload_step_status",
    [
        (False, StepStatus.SUCCESS, StepStatus.SUCCESS, StepStatus.SUCCESS, StepStatus.SUCCESS, StepStatus.SUCCESS),
        (False, StepStatus.SUCCESS, StepStatus.SUCCESS, StepStatus.SUCCESS, StepStatus.SUCCESS, StepStatus.FAILURE),
        (False, StepStatus.SUCCESS, StepStatus.SUCCESS, StepStatus.SUCCESS, StepStatus.FAILURE, None),
        (False, StepStatus.SUCCESS, StepStatus.SUCCESS, StepStatus.FAILURE, None, None),
        (False, StepStatus.SUCCESS, StepStatus.FAILURE, None, None, None),
        (False, StepStatus.FAILURE, None, None, None, None),
        (True, StepStatus.SUCCESS, StepStatus.SUCCESS, StepStatus.SUCCESS, StepStatus.SUCCESS, StepStatus.SUCCESS),
    ],
)
async def test_run_connector_publish_pipeline_when_image_does_not_exist(
    mocker,
    pre_release,
    build_step_status,
    push_step_status,
    pull_step_status,
    upload_to_spec_cache_step_status,
    metadata_upload_step_status,
):
    """We check that the full pipeline is executed as expected when the connector image does not exist and the metadata validation passed."""
    for module, to_mock in STEPS_TO_PATCH:
        mocker.patch.object(module, to_mock, return_value=mocker.AsyncMock())
    publish_pipeline.MetadataValidation.return_value.run.return_value = mocker.Mock(
        name="metadata_validation_result", status=StepStatus.SUCCESS
    )
    publish_pipeline.CheckConnectorImageDoesNotExist.return_value.run.return_value = mocker.Mock(
        name="check_connector_image_does_not_exist_result", status=StepStatus.SUCCESS
    )

    # have output.values return []
    built_connector_platform = mocker.Mock()
    built_connector_platform.values.return_value = ["linux/amd64"]

    publish_pipeline.steps.run_connector_build.return_value = mocker.Mock(
        name="build_connector_for_publish_result", status=build_step_status, output=built_connector_platform
    )

    publish_pipeline.PushConnectorImageToRegistry.return_value.run.return_value = mocker.Mock(
        name="push_connector_image_to_registry_result", status=push_step_status
    )

    publish_pipeline.PullConnectorImageFromRegistry.return_value.run.return_value = mocker.Mock(
        name="pull_connector_image_from_registry_result", status=pull_step_status
    )

    publish_pipeline.UploadSpecToCache.return_value.run.return_value = mocker.Mock(
        name="upload_spec_to_cache_result", status=upload_to_spec_cache_step_status
    )
    publish_pipeline.MetadataUpload.return_value.run.return_value = mocker.Mock(
        name="metadata_upload_result", status=metadata_upload_step_status
    )

    context = mocker.MagicMock(pre_release=pre_release, rollout_mode=RolloutMode.PUBLISH)
    semaphore = anyio.Semaphore(1)
    report = await publish_pipeline.run_connector_publish_pipeline(context, semaphore)

    steps_to_run = [
        publish_pipeline.MetadataValidation.return_value.run,
        publish_pipeline.CheckConnectorImageDoesNotExist.return_value.run,
        publish_pipeline.steps.run_connector_build,
        publish_pipeline.PushConnectorImageToRegistry.return_value.run,
        publish_pipeline.PullConnectorImageFromRegistry.return_value.run,
    ]

    for i, step_to_run in enumerate(steps_to_run):
        if step_to_run.return_value.status is StepStatus.FAILURE or i == len(steps_to_run) - 1:
            assert len(report.steps_results) == len(context.report.steps_results)

            previous_steps = steps_to_run[:i]
            for _, step_ran in enumerate(previous_steps):
                step_ran.assert_called_once()
                step_ran.return_value

            remaining_steps = steps_to_run[i + 1 :]
            for step_to_run in remaining_steps:
                step_to_run.assert_not_called()
            break
    if build_step_status is StepStatus.SUCCESS:
        publish_pipeline.PushConnectorImageToRegistry.return_value.run.assert_called_once_with(["linux/amd64"])
    else:
        publish_pipeline.PushConnectorImageToRegistry.return_value.run.assert_not_called()
        publish_pipeline.PullConnectorImageFromRegistry.return_value.run.assert_not_called()
        publish_pipeline.UploadSpecToCache.return_value.run.assert_not_called()
        publish_pipeline.MetadataUpload.return_value.run.assert_not_called()


@pytest.mark.parametrize(
    "pypi_enabled, pypi_package_does_not_exist_status, publish_step_status, expect_publish_to_pypi_called, expect_build_connector_called,api_token",
    [
        pytest.param(True, StepStatus.SUCCESS, StepStatus.SUCCESS, True, True, "test", id="happy_path"),
        pytest.param(False, StepStatus.SUCCESS, StepStatus.SUCCESS, False, True, "test", id="pypi_disabled, skip all pypi steps"),
        pytest.param(True, StepStatus.SKIPPED, StepStatus.SUCCESS, False, True, "test", id="pypi_package_exists, skip publish_to_pypi"),
        pytest.param(True, StepStatus.SUCCESS, StepStatus.FAILURE, True, False, "test", id="publish_step_fails, abort"),
        pytest.param(True, StepStatus.FAILURE, StepStatus.FAILURE, False, False, "test", id="pypi_package_does_not_exist_fails, abort"),
        pytest.param(True, StepStatus.SUCCESS, StepStatus.SUCCESS, False, False, None, id="no_api_token, abort"),
    ],
)
async def test_run_connector_python_registry_publish_pipeline(
    mocker,
    pypi_enabled,
    pypi_package_does_not_exist_status,
    publish_step_status,
    expect_publish_to_pypi_called,
    expect_build_connector_called,
    api_token,
):
    for module, to_mock in STEPS_TO_PATCH:
        mocker.patch.object(module, to_mock, return_value=mocker.AsyncMock())

    mocked_publish_to_python_registry = mocker.patch(
        "pipelines.airbyte_ci.connectors.publish.pipeline.PublishToPythonRegistry", return_value=mocker.AsyncMock()
    )

    for step in [
        publish_pipeline.MetadataValidation,
        publish_pipeline.CheckConnectorImageDoesNotExist,
        publish_pipeline.UploadSpecToCache,
        publish_pipeline.MetadataUpload,
        publish_pipeline.PushConnectorImageToRegistry,
        publish_pipeline.PullConnectorImageFromRegistry,
    ]:
        step.return_value.run.return_value = mocker.Mock(name=f"{step.title}_result", status=StepStatus.SUCCESS)

    mocked_publish_to_python_registry.return_value.run.return_value = mocker.Mock(
        name="publish_to_python_registry_result", status=publish_step_status
    )

    publish_pipeline.CheckPythonRegistryPackageDoesNotExist.return_value.run.return_value = mocker.Mock(
        name="python_registry_package_does_not_exist_result", status=pypi_package_does_not_exist_status
    )

    context = mocker.MagicMock(
        ci_gcp_credentials="",
        pre_release=False,
        connector=mocker.MagicMock(
            code_directory="path/to/connector",
            metadata={"dockerImageTag": "1.2.3", "remoteRegistries": {"pypi": {"enabled": pypi_enabled, "packageName": "test"}}},
        ),
        python_registry_token=api_token,
        python_registry_url="https://test.pypi.org/legacy/",
        rollout_mode=RolloutMode.PUBLISH,
    )
    semaphore = anyio.Semaphore(1)
    if api_token is None:
        with pytest.raises(AssertionError):
            await publish_pipeline.run_connector_publish_pipeline(context, semaphore)
    else:
        await publish_pipeline.run_connector_publish_pipeline(context, semaphore)
        if expect_publish_to_pypi_called:
            mocked_publish_to_python_registry.return_value.run.assert_called_once()
            # assert that the first argument passed to mocked_publish_to_pypi contains the things from the context
            assert mocked_publish_to_python_registry.call_args.args[0].python_registry_token == api_token
            assert mocked_publish_to_python_registry.call_args.args[0].package_metadata.name == "test"
            assert mocked_publish_to_python_registry.call_args.args[0].package_metadata.version == "1.2.3"
            assert mocked_publish_to_python_registry.call_args.args[0].registry == "https://test.pypi.org/legacy/"
            assert mocked_publish_to_python_registry.call_args.args[0].package_path == "path/to/connector"
        else:
            mocked_publish_to_python_registry.return_value.run.assert_not_called()

        if expect_build_connector_called:
            publish_pipeline.steps.run_connector_build.assert_called_once()


class TestPushConnectorImageToRegistry:
    @pytest.mark.parametrize(
        "is_pre_release, version, should_publish_latest",
        [
            (False, "1.0.0", True),
            (True, "1.1.0-dev", False),
            (False, "1.1.0-rc.1", False),
            (True, "1.1.0-rc.1", False),
        ],
    )
    async def test_publish_latest_tag(self, mocker, publish_context, is_pre_release, version, should_publish_latest):
        publish_context.docker_image = "airbyte/source-pokeapi:0.0.0"
        publish_context.docker_repository = "airbyte/source-pokeapi"
        publish_context.pre_release = is_pre_release
        publish_context.connector.version = version
        publish_context.connector.metadata = {"dockerImageTag": version}
        step = publish_pipeline.PushConnectorImageToRegistry(publish_context)
        amd_built_container = mocker.Mock(publish=mocker.AsyncMock())
        arm_built_container = mocker.Mock(publish=mocker.AsyncMock())
        built_containers_per_platform = [amd_built_container, arm_built_container]
        await step.run(built_containers_per_platform)
        assert amd_built_container.publish.call_args_list[0][0][0] == "docker.io/airbyte/source-pokeapi:0.0.0"
        if should_publish_latest:
            assert amd_built_container.publish.await_count == 2, "Expected to publish the latest tag and the specific version tag"
            assert amd_built_container.publish.call_args_list[1][0][0] == "docker.io/airbyte/source-pokeapi:latest"
        else:
            assert amd_built_container.publish.await_count == 1, "Expected to publish only the specific version tag"
