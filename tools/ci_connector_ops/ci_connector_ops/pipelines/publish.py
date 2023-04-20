#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import os
import uuid
from abc import ABC
from typing import List, Tuple

import anyio
import dagger
from ci_connector_ops.pipelines import builds
from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.actions.remote_storage import upload_to_gcs
from ci_connector_ops.pipelines.bases import ConnectorReport, Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorContext
from ci_connector_ops.pipelines.pipelines import metadata
from ci_connector_ops.pipelines.utils import with_stderr, with_stdout
from dagger import Container, File, QueryError, Secret


class PublishStep(Step, ABC):
    def __init__(self, context: ConnectorContext, pre_release: bool = True) -> None:
        super().__init__(context)
        self.pre_release = pre_release

    @property
    def docker_image_name(self):
        if self.pre_release:
            return f"{self.context.docker_image_from_metadata}-dev.{self.context.git_revision[:10]}"
        else:
            return self.context.docker_image_from_metadata


class CheckConnectorImageDoesNotExist(PublishStep):
    title = "Check if the connector docker image does not exist on the registry."

    async def _run(self) -> StepResult:
        manifest_inspect = (
            environments.with_docker_cli(self.context)
            .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
            .with_exec(["docker", "manifest", "inspect", self.docker_image_name])
        )
        manifest_inspect_stderr = await with_stderr(manifest_inspect)
        manifest_inspect_stdout = await with_stdout(manifest_inspect)

        if "no such manifest" in manifest_inspect_stderr:
            return StepResult(self, status=StepStatus.SUCCESS, stdout=f"No manifest found for {self.context.docker_image_from_metadata}.")
        else:
            try:
                manifests = json.loads(manifest_inspect_stdout.replace("\n", "")).get("manifests", [])
                available_platforms = {f"{manifest['platform']['os']}/{manifest['platform']['architecture']}" for manifest in manifests}
                if available_platforms.issubset(set(builds.BUILD_PLATFORMS)):
                    return StepResult(self, status=StepStatus.FAILURE, stderr=f"{self.context.docker_image_from_metadata} already exists.")
                else:
                    return StepResult(
                        self, status=StepStatus.SUCCESS, stdout=f"No all manifests found for {self.context.docker_image_from_metadata}."
                    )
            except json.JSONDecodeError:
                return StepResult(self, status=StepStatus.FAILURE, stderr=manifest_inspect_stderr, stdout=manifest_inspect_stdout)


class BuildConnectorForPublish(Step):

    title = "Build connector for publish"

    async def _run(self) -> Tuple[StepResult, List[Container]]:
        build_connector_results_per_platform = await builds.run_connector_build(self.context)
        build_connector_results = [build_result for build_result, _ in build_connector_results_per_platform.values()]
        built_connectors = [built_connector for _, built_connector in build_connector_results_per_platform.values()]

        if not all([build_result.status is StepStatus.SUCCESS for build_result in build_connector_results]):
            return StepResult(self, status=StepStatus.FAILURE), []

        return StepResult(self, status=StepStatus.SUCCESS), built_connectors


class PushConnectorImageToRegistry(PublishStep):
    title = "Push connector image to registry"

    @property
    def latest_docker_image_name(self):
        return f"{self.context.metadata['dockerRepository']}:latest"

    async def _run(self, built_containers_per_platform: List[Container]) -> StepResult:
        try:
            image_ref = await built_containers_per_platform[0].publish(
                f"docker.io/{self.docker_image_name}", platform_variants=built_containers_per_platform[1:]
            )
            if not self.pre_release:
                image_ref = await built_containers_per_platform[0].publish(
                    f"docker.io/{self.latest_docker_image_name}", platform_variants=built_containers_per_platform[1:]
                )
            return StepResult(self, status=StepStatus.SUCCESS, stdout=f"Published {image_ref}")
        except QueryError as e:
            return StepResult(self, status=StepStatus.FAILURE, stderr=str(e))


class InvalidSpecOutputError(Exception):
    pass


class UploadSpecToCache(PublishStep):
    title = "Upload connector spec to spec cache bucket"
    default_spec_file_name = "spec.json"
    cloud_spec_file_name = "spec.cloud.json"

    def _parse_spec_output(self, spec_output: str) -> str:
        for line in spec_output.split("\n"):
            try:
                parsed_json = json.loads(line)
                if parsed_json["type"] == "SPEC":
                    return json.dumps(parsed_json)
            except (json.JSONDecodeError, KeyError):
                continue
        raise InvalidSpecOutputError("Could not parse the output of the spec command.")

    async def _get_connector_spec(self, connector: Container, deployment_mode: str) -> str:
        spec_output = await connector.with_env_variable("DEPLOYMENT_MODE", deployment_mode).with_exec(["spec"]).stdout()
        return self._parse_spec_output(spec_output)

    def _get_spec_as_file(self, spec: str, name="spec_to_cache.json") -> File:
        return self.context.get_connector_dir().with_new_file(name, spec).file(name)

    @property
    def spec_key_prefix(self):
        return "specs/" + self.docker_image_name.replace(":", "/")

    @property
    def cloud_spec_key(self):
        return f"{self.spec_key_prefix}/{self.cloud_spec_file_name}"

    @property
    def oss_spec_key(self):
        return f"{self.spec_key_prefix}/{self.default_spec_file_name}"

    def __init__(self, context: ConnectorContext, pre_release: bool, spec_bucket_name: str, gcs_credentials: Secret) -> None:
        super().__init__(context, pre_release)
        self.spec_bucket_name = spec_bucket_name
        self.gcs_credentials = gcs_credentials

    async def _run(self, built_connector: Container) -> List[StepResult]:
        oss_spec: str = await self._get_connector_spec(built_connector, "OSS")
        cloud_spec: str = await self._get_connector_spec(built_connector, "CLOUD")

        specs_to_uploads: List[Tuple[str, File]] = [(self.oss_spec_key, self._get_spec_as_file(oss_spec))]

        if oss_spec != cloud_spec:
            specs_to_uploads.append(self.cloud_spec_key, self._get_spec_as_file(cloud_spec, "cloud_spec_to_cache.json"))

        upload_results = []
        for key, file in specs_to_uploads:
            exit_code, stdout, stderr = await upload_to_gcs(
                self.context.dagger_client, file, key, self.spec_bucket_name, self.gcs_credentials
            )
            upload_results.append(StepResult(self, status=StepStatus.from_exit_code(exit_code), stdout=stdout, stderr=stderr))
        return upload_results


async def run_connector_publish_pipeline(
    context: ConnectorContext, semaphore: anyio.Semaphore, pre_release: bool, spec_bucket_name: str, metadata_bucket_name: str
) -> ConnectorReport:
    """Run a publish pipeline for a single connector.

    1. Validate the metadata file.
    2. Check if the connector image already exists.
    3. Build the connector, with platform variants.
    4. Upload its spec to the spec cache bucket.
    5. Push the connector to DockerHub, with platform variants.
    6. Upload its metadata file to the metadata service bucket.

    Returns:
        ConnectorReport: The reports holding publish results.
    """
    async with semaphore:
        async with context:
            report_name = "PUBLISH RESULTS"
            spec_cache_service_account: dagger.Secret = context.dagger_client.set_secret(
                "spec_cache_service_account_key", os.environ["SPEC_CACHE_SERVICE_ACCOUNT_KEY"]
            )
            metadata_service_account: dagger.Secret = context.dagger_client.set_secret(
                "metadata_service_account_key", os.environ["METADATA_SERVICE_ACCOUNT_KEY"]
            )

            metadata_validation_step = metadata.MetadataValidation(context, context.metadata_path)
            check_connector_image_does_not_exists_step = CheckConnectorImageDoesNotExist(context, pre_release)
            build_connector_step = BuildConnectorForPublish(context)
            upload_spec_to_cache_step = UploadSpecToCache(context, pre_release, spec_bucket_name, spec_cache_service_account)
            push_connector_image_to_registry_step = PushConnectorImageToRegistry(context, pre_release)
            metadata_upload_step = metadata.MetadataUpload(
                context, context.metadata_path, metadata_bucket_name, await metadata_service_account.plaintext()
            )
            step_results = []

            # TODO this sequence of "return on Failure" is not beautiful.
            # We'll improve this soon with a different and global approach to chain steps.
            metadata_validation_result = await metadata_validation_step.run()
            step_results.append(metadata_validation_result)
            if metadata_validation_result.status is StepStatus.FAILURE:
                context.report = ConnectorReport(context, step_results, name=report_name)
                return context.report

            check_connector_image_does_not_exists_result = await check_connector_image_does_not_exists_step.run()
            step_results.append(check_connector_image_does_not_exists_result)
            if check_connector_image_does_not_exists_result.status is StepStatus.FAILURE:
                context.report = ConnectorReport(context, step_results, name=report_name)
                return context.report

            build_connector_result, built_connectors = await build_connector_step.run()
            step_results.append(build_connector_result)
            if build_connector_result.status is StepStatus.FAILURE:
                context.report = ConnectorReport(context, step_results, name=report_name)
                return context.report

            upload_spec_to_cache_results: List[StepResult] = await upload_spec_to_cache_step.run(built_connectors[0])
            step_results += upload_spec_to_cache_results
            if any(
                [upload_spec_to_cache_result.status is StepStatus.FAILURE for upload_spec_to_cache_result in upload_spec_to_cache_results]
            ):
                context.report = ConnectorReport(context, step_results, name=report_name)
                return context.report

            push_connector_image_to_registry_result = await push_connector_image_to_registry_step.run(built_connectors)
            step_results.append(push_connector_image_to_registry_result)
            if push_connector_image_to_registry_result.status is StepStatus.FAILURE:
                context.report = ConnectorReport(context, step_results, name=report_name)
                return context.report

            metadata_upload_results = await metadata_upload_step.run()
            step_results.append(metadata_upload_results)
            context.report = ConnectorReport(context, step_results, name=report_name)
        return context.report
