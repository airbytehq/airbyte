#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import random
from typing import List

import anyio
import pytest
from pipelines import publish
from pipelines.bases import StepStatus

pytestmark = [
    pytest.mark.anyio,
]


@pytest.fixture
def publish_context(mocker, dagger_client, tmpdir):
    return mocker.MagicMock(
        dagger_client=dagger_client,
        get_connector_dir=mocker.MagicMock(return_value=dagger_client.host().directory(str(tmpdir))),
        docker_hub_username_secret=None,
        docker_hub_password_secret=None,
        docker_image="hello-world:latest",
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
            step = publish.CheckConnectorImageDoesNotExist(publish_context)
            step_result = await step.run()
            assert step_result.status == StepStatus.SKIPPED

    async def test_run_success_when_already_published(self, publish_context):
        publish_context.docker_image = "airbyte/source-pokeapi:0.0.0"
        step = publish.CheckConnectorImageDoesNotExist(publish_context)
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
            publish, "upload_to_gcs", mocker.AsyncMock(return_value=(upload_exit_code, "upload_to_gcs_stdout", "upload_to_gcs_stderr"))
        )
        if not valid_spec:
            mocker.patch.object(
                publish.UploadSpecToCache, "_get_connector_spec", mocker.Mock(side_effect=publish.InvalidSpecOutputError("Invalid spec."))
            )

        step = publish.UploadSpecToCache(publish_context)
        step_result = await step.run(connector_container)
        if valid_spec:
            publish.upload_to_gcs.assert_called_once_with(
                publish_context.dagger_client,
                mocker.ANY,
                f"specs/{image_name.replace(':', '/')}/spec.json",
                publish_context.spec_cache_bucket_name,
                publish_context.spec_cache_gcs_credentials_secret,
                flags=['--cache-control="no-cache"'],
            )

            spec_file = publish.upload_to_gcs.call_args.args[1]
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
            publish.upload_to_gcs.assert_not_called()

    def test_parse_spec_output_valid(self, publish_context, random_connector):
        step = publish.UploadSpecToCache(publish_context)
        correct_spec_message = json.dumps({"type": "SPEC", "spec": random_connector["spec"]})
        spec_output = f'random_stuff\n{{"type": "RANDOM_MESSAGE"}}\n{correct_spec_message}'
        result = step._parse_spec_output(spec_output)
        assert json.loads(result) == random_connector["spec"]

    def test_parse_spec_output_invalid_json(self, publish_context):
        step = publish.UploadSpecToCache(publish_context)
        spec_output = "Invalid JSON"
        with pytest.raises(publish.InvalidSpecOutputError):
            step._parse_spec_output(spec_output)

    def test_parse_spec_output_invalid_key(self, publish_context):
        step = publish.UploadSpecToCache(publish_context)
        spec_output = '{"type": "SPEC", "spec": {"invalid_key": "value"}}'
        with pytest.raises(publish.InvalidSpecOutputError):
            step._parse_spec_output(spec_output)

    def test_parse_spec_output_no_spec(self, publish_context):
        step = publish.UploadSpecToCache(publish_context)
        spec_output = '{"type": "OTHER"}'
        with pytest.raises(publish.InvalidSpecOutputError):
            step._parse_spec_output(spec_output)


STEPS_TO_PATCH = [
    (publish.metadata, "MetadataValidation"),
    (publish.metadata, "MetadataUpload"),
    (publish, "CheckConnectorImageDoesNotExist"),
    (publish, "UploadSpecToCache"),
    (publish, "PushConnectorImageToRegistry"),
    (publish, "PullConnectorImageFromRegistry"),
    (publish.builds, "run_connector_build"),
]


@pytest.mark.parametrize("pre_release", [True, False])
async def test_run_connector_publish_pipeline_when_failed_validation(mocker, pre_release):
    """We validate that no other steps are called if the metadata validation step fails."""
    for module, to_mock in STEPS_TO_PATCH:
        mocker.patch.object(module, to_mock, return_value=mocker.AsyncMock())

    run_metadata_validation = publish.metadata.MetadataValidation.return_value.run
    run_metadata_validation.return_value = mocker.Mock(status=StepStatus.FAILURE)

    context = mocker.MagicMock(pre_release=pre_release)
    semaphore = anyio.Semaphore(1)
    report = await publish.run_connector_publish_pipeline(context, semaphore)
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

    run_metadata_validation = publish.metadata.MetadataValidation.return_value.run
    run_metadata_validation.return_value = mocker.Mock(status=StepStatus.SUCCESS)

    # ensure spec always succeeds
    run_upload_spec_to_cache = publish.UploadSpecToCache.return_value.run
    run_upload_spec_to_cache.return_value = mocker.Mock(status=StepStatus.SUCCESS)

    run_check_connector_image_does_not_exist = publish.CheckConnectorImageDoesNotExist.return_value.run
    run_check_connector_image_does_not_exist.return_value = mocker.Mock(status=check_image_exists_status)

    run_metadata_upload = publish.metadata.MetadataUpload.return_value.run

    semaphore = anyio.Semaphore(1)
    report = await publish.run_connector_publish_pipeline(publish_context, semaphore)
    run_metadata_validation.assert_called_once()
    run_check_connector_image_does_not_exist.assert_called_once()

    # Check that nothing else is called
    for module, to_mock in STEPS_TO_PATCH:
        if to_mock not in ["MetadataValidation", "MetadataUpload", "CheckConnectorImageDoesNotExist", "UploadSpecToCache"]:
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
    publish.metadata.MetadataValidation.return_value.run.return_value = mocker.Mock(
        name="metadata_validation_result", status=StepStatus.SUCCESS
    )
    publish.CheckConnectorImageDoesNotExist.return_value.run.return_value = mocker.Mock(
        name="check_connector_image_does_not_exist_result", status=StepStatus.SUCCESS
    )

    # have output_artifact.values return []
    built_connector_platform = mocker.Mock()
    built_connector_platform.values.return_value = ["linux/amd64"]

    publish.builds.run_connector_build.return_value = mocker.Mock(
        name="build_connector_for_publish_result", status=build_step_status, output_artifact=built_connector_platform
    )

    publish.PushConnectorImageToRegistry.return_value.run.return_value = mocker.Mock(
        name="push_connector_image_to_registry_result", status=push_step_status
    )

    publish.PullConnectorImageFromRegistry.return_value.run.return_value = mocker.Mock(
        name="pull_connector_image_from_registry_result", status=pull_step_status
    )

    publish.UploadSpecToCache.return_value.run.return_value = mocker.Mock(
        name="upload_spec_to_cache_result", status=upload_to_spec_cache_step_status
    )
    publish.metadata.MetadataUpload.return_value.run.return_value = mocker.Mock(
        name="metadata_upload_result", status=metadata_upload_step_status
    )

    context = mocker.MagicMock(
        pre_release=pre_release,
    )
    semaphore = anyio.Semaphore(1)
    report = await publish.run_connector_publish_pipeline(context, semaphore)

    steps_to_run = [
        publish.metadata.MetadataValidation.return_value.run,
        publish.CheckConnectorImageDoesNotExist.return_value.run,
        publish.builds.run_connector_build,
        publish.PushConnectorImageToRegistry.return_value.run,
        publish.PullConnectorImageFromRegistry.return_value.run,
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
        publish.PushConnectorImageToRegistry.return_value.run.assert_called_once_with(["linux/amd64"])
    else:
        publish.PushConnectorImageToRegistry.return_value.run.assert_not_called()
        publish.PullConnectorImageFromRegistry.return_value.run.assert_not_called()
        publish.UploadSpecToCache.return_value.run.assert_not_called()
        publish.metadata.MetadataUpload.return_value.run.assert_not_called()
