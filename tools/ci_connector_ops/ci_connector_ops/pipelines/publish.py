#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import uuid
from typing import List, Tuple

import anyio
from airbyte_protocol.models.airbyte_protocol import ConnectorSpecification
from ci_connector_ops.pipelines import builds
from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.actions.remote_storage import upload_to_gcs
from ci_connector_ops.pipelines.bases import ConnectorReport, Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import PublishConnectorContext
from ci_connector_ops.pipelines.pipelines import metadata
from ci_connector_ops.pipelines.utils import with_stderr, with_stdout
from dagger import Container, File, QueryError
from pydantic import ValidationError


class CheckConnectorImageDoesNotExist(Step):
    title = "Check if the connector docker image does not exist on the registry."

    async def _run(self) -> StepResult:
        manifest_inspect = (
            environments.with_docker_cli(self.context)
            .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
            .with_exec(["sh", "-c", f"docker manifest inspect {self.context.docker_image_name} || true"])
        )
        manifest_inspect_stderr = await with_stderr(manifest_inspect)
        manifest_inspect_stdout = await with_stdout(manifest_inspect)
        if "no such manifest" in manifest_inspect_stderr:
            return StepResult(self, status=StepStatus.SUCCESS, stdout=f"No manifest found for {self.context.docker_image_name}.")
        else:
            try:
                json.loads(manifest_inspect_stdout.replace("\n", ""))["manifests"]
                return StepResult(self, status=StepStatus.SKIPPED, stderr=f"{self.context.docker_image_name} already exists.")
            except (json.JSONDecodeError, KeyError):
                return StepResult(self, status=StepStatus.FAILURE, stderr=manifest_inspect_stderr, stdout=manifest_inspect_stdout)


class BuildConnectorForPublish(Step):
    title = "Build connector for publish"

    async def _run(self) -> StepResult:
        build_connectors_results = (await builds.run_connector_build(self.context)).values()
        for build_result in build_connectors_results:
            if build_result.status is not StepStatus.SUCCESS:
                return build_result
        built_connectors_platform_variants = [step_result.output_artifact for step_result in build_connectors_results]

        return StepResult(self, status=StepStatus.SUCCESS, output_artifact=built_connectors_platform_variants)


class PushConnectorImageToRegistry(Step):
    title = "Push connector image to registry"

    @property
    def latest_docker_image_name(self):
        return f"{self.context.metadata['dockerRepository']}:latest"

    async def _run(self, built_containers_per_platform: List[Container]) -> StepResult:
        try:
            image_ref = await built_containers_per_platform[0].publish(
                f"docker.io/{self.context.docker_image_name}", platform_variants=built_containers_per_platform[1:]
            )
            if not self.context.pre_release:
                image_ref = await built_containers_per_platform[0].publish(
                    f"docker.io/{self.latest_docker_image_name}", platform_variants=built_containers_per_platform[1:]
                )
            return StepResult(self, status=StepStatus.SUCCESS, stdout=f"Published {image_ref}")
        except QueryError as e:
            return StepResult(self, status=StepStatus.FAILURE, stderr=str(e))


class InvalidSpecOutputError(Exception):
    pass


class UploadSpecToCache(Step):
    title = "Upload connector spec to spec cache bucket"
    default_spec_file_name = "spec.json"
    cloud_spec_file_name = "spec.cloud.json"

    @property
    def spec_key_prefix(self):
        return "specs/" + self.context.docker_image_name.replace(":", "/")

    @property
    def cloud_spec_key(self):
        return f"{self.spec_key_prefix}/{self.cloud_spec_file_name}"

    @property
    def oss_spec_key(self):
        return f"{self.spec_key_prefix}/{self.default_spec_file_name}"

    def _parse_spec_output(self, spec_output: str) -> str:
        for line in spec_output.split("\n"):
            try:
                parsed_json = json.loads(line)
                if parsed_json["type"] == "SPEC":
                    parsed_spec = parsed_json["spec"]
                    ConnectorSpecification.parse_obj(parsed_spec)
                    return json.dumps(parsed_spec)
            except (json.JSONDecodeError, KeyError, ValidationError, ValueError):
                raise InvalidSpecOutputError("Could not parse the output of the SPEC command to a valid spec.")

    async def _get_connector_spec(self, connector: Container, deployment_mode: str) -> str:
        spec_output = await connector.with_env_variable("DEPLOYMENT_MODE", deployment_mode).with_exec(["spec"]).stdout()
        return self._parse_spec_output(spec_output)

    def _get_spec_as_file(self, spec: str, name="spec_to_cache.json") -> File:
        return self.context.get_connector_dir().with_new_file(name, spec).file(name)

    async def _run(self, built_connector: Container) -> StepResult:
        try:
            oss_spec: str = await self._get_connector_spec(built_connector, "OSS")
            cloud_spec: str = await self._get_connector_spec(built_connector, "CLOUD")
        except InvalidSpecOutputError as e:
            return StepResult(self, status=StepStatus.FAILURE, stderr=str(e))

        specs_to_uploads: List[Tuple[str, File]] = [(self.oss_spec_key, self._get_spec_as_file(oss_spec))]

        if oss_spec != cloud_spec:
            specs_to_uploads.append(self.cloud_spec_key, self._get_spec_as_file(cloud_spec, "cloud_spec_to_cache.json"))

        for key, file in specs_to_uploads:
            exit_code, stdout, stderr = await upload_to_gcs(
                self.context.dagger_client,
                file,
                key,
                self.context.spec_cache_bucket_name,
                self.context.spec_cache_gcs_credentials_secret,
            )
            if exit_code != 0:
                return StepResult(self, status=StepStatus.FAILURE, stdout=stdout, stderr=stderr)
        return StepResult(self, status=StepStatus.SUCCESS, stdout="Uploaded connector spec to spec cache bucket.")


async def run_connector_publish_pipeline(context: PublishConnectorContext, semaphore: anyio.Semaphore) -> ConnectorReport:
    """Run a publish pipeline for a single connector.

    1. Validate the metadata file.
    2. Check if the connector image already exists.
    3. Build the connector, with platform variants.
    4. Push the connector to DockerHub, with platform variants.
    5. Upload its spec to the spec cache bucket.
    6. Upload its metadata file to the metadata service bucket.

    Returns:
        ConnectorReport: The reports holding publish results.
    """

    def create_connector_report(results: List[StepResult]) -> ConnectorReport:
        report = ConnectorReport(context, results, name="PUBLISH RESULTS")
        context.report = report
        return report

    async with semaphore:
        async with context:
            results = []
            metadata_validation_results = await metadata.MetadataValidation(context, context.metadata_path).run()
            results.append(metadata_validation_results)
            if metadata_validation_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results)

            check_connector_image_results = await CheckConnectorImageDoesNotExist(context).run()
            results.append(check_connector_image_results)
            if check_connector_image_results.status is not StepStatus.SUCCESS:
                if check_connector_image_results.status is StepStatus.SKIPPED:
                    context.logger.info(
                        "The connector version is already published. Let's upload metadata.yaml to GCS even if no version bump happened."
                    )
                    metadata_upload_results = await metadata.MetadataUpload(context).run()
                    results.append(metadata_upload_results)
                return create_connector_report(results)

            build_connector_results = await BuildConnectorForPublish(context).run()
            results.append(build_connector_results)
            if build_connector_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results)

            built_connector_platform_variants = build_connector_results.output_artifact

            push_connector_image_results = await PushConnectorImageToRegistry(context).run(built_connector_platform_variants)
            results.append(push_connector_image_results)
            if push_connector_image_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results)

            upload_to_spec_cache_results = await UploadSpecToCache(context).run(built_connector_platform_variants[0])
            results.append(upload_to_spec_cache_results)
            if upload_to_spec_cache_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results)

            metadata_upload_results = await metadata.MetadataUpload(context).run()
            results.append(metadata_upload_results)
            return create_connector_report(results)
