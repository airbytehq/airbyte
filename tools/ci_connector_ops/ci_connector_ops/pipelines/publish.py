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
from ci_connector_ops.pipelines.utils import with_exit_code, with_stderr, with_stdout
from dagger import Container, File, ImageLayerCompression, QueryError
from pydantic import ValidationError


class CheckConnectorImageDoesNotExist(Step):
    title = "Check if the connector docker image does not exist on the registry."

    async def _run(self) -> StepResult:
        docker_repository, docker_tag = self.context.docker_image_name.split(":")
        crane_ls = (
            environments.with_crane(self.context).with_env_variable("CACHEBUSTER", str(uuid.uuid4())).with_exec(["ls", docker_repository])
        )
        crane_ls_exit_code = await with_exit_code(crane_ls)
        crane_ls_stderr = await with_stderr(crane_ls)
        crane_ls_stdout = await with_stdout(crane_ls)
        if crane_ls_exit_code != 0:
            if "NAME_UNKNOWN" in crane_ls_stderr:
                return StepResult(self, status=StepStatus.SUCCESS, stdout=f"The docker repository {docker_repository} does not exist.")
            else:
                return StepResult(self, status=StepStatus.FAILURE, stderr=crane_ls_stderr, stdout=crane_ls_stdout)
        else:  # The docker repo exists and ls was successful
            existing_tags = crane_ls_stdout.split("\n")
            docker_tag_already_exists = docker_tag in existing_tags
            if docker_tag_already_exists:
                return StepResult(self, status=StepStatus.SKIPPED, stderr=f"{self.context.docker_image_name} already exists.")
            return StepResult(self, status=StepStatus.SUCCESS, stdout=f"No manifest found for {self.context.docker_image_name}.")


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

    async def _run(self, built_containers_per_platform: List[Container], attempts: int = 3) -> StepResult:
        try:
            image_ref = await built_containers_per_platform[0].publish(
                f"docker.io/{self.context.docker_image_name}",
                platform_variants=built_containers_per_platform[1:],
                forced_compression=ImageLayerCompression.Gzip,
            )
            if not self.context.pre_release:
                image_ref = await built_containers_per_platform[0].publish(
                    f"docker.io/{self.latest_docker_image_name}",
                    platform_variants=built_containers_per_platform[1:],
                    forced_compression=ImageLayerCompression.Gzip,
                )
            return StepResult(self, status=StepStatus.SUCCESS, stdout=f"Published {image_ref}")
        except QueryError as e:
            if attempts > 0:
                self.context.logger.error(str(e))
                self.context.logger.warn(f"Failed to publish {self.context.docker_image_name}. Retrying. {attempts} attempts left.")
                await anyio.sleep(5)
                return await self._run(built_containers_per_platform, attempts - 1)
            return StepResult(self, status=StepStatus.FAILURE, stderr=str(e))


class PullConnectorImageFromRegistry(Step):
    title = "Pull connector image from registry"

    async def check_if_image_only_has_gzip_layers(self) -> bool:
        """Check if the image only has gzip layers.
        Docker version > 21 can create images that has some layers compressed with zstd.
        These layers are not supported by previous docker versions.
        We want to make sure that the image we are about to release is compatible with all docker versions.
        We use crane to inspect the manifest of the image and check if it only has gzip layers.
        """
        for platform in builds.BUILD_PLATFORMS:

            inspect = environments.with_crane(self.context).with_exec(
                ["manifest", "--platform", f"{str(platform)}", f"docker.io/{self.context.docker_image_name}"]
            )
            inspect_exit_code = await with_exit_code(inspect)
            inspect_stderr = await with_stderr(inspect)
            inspect_stdout = await with_stdout(inspect)
            if inspect_exit_code != 0:
                raise Exception(f"Failed to inspect {self.context.docker_image_name}: {inspect_stderr}")
            try:
                for layer in json.loads(inspect_stdout)["layers"]:
                    if not layer["mediaType"].endswith(".gzip"):
                        return False
                return True
            except (KeyError, json.JSONDecodeError) as e:
                raise Exception(f"Failed to parse manifest for {self.context.docker_image_name}: {inspect_stdout}") from e

    async def _run(self, attempt: int = 3) -> StepResult:
        try:
            exit_code = await with_exit_code(
                self.context.dagger_client.container().from_(f"docker.io/{self.context.docker_image_name}").with_exec(["spec"])
            )
            if exit_code != 0:
                if attempt > 0:
                    await anyio.sleep(10)
                    return await self._run(attempt - 1)
                else:
                    return StepResult(self, status=StepStatus.FAILURE, stderr=f"Failed to pull {self.context.docker_image_name}")
            if not await self.check_if_image_only_has_gzip_layers():
                return StepResult(
                    self,
                    status=StepStatus.FAILURE,
                    stderr=f"Image {self.context.docker_image_name} does not only have gzip compressed layers. Please rebuild the connector with Docker < 21.",
                )
            else:
                return StepResult(
                    self,
                    status=StepStatus.SUCCESS,
                    stdout=f"Pulled {self.context.docker_image_name} and validated it has gzip only compressed layers and we can run spec on it.",
                )
        except QueryError as e:
            if attempt > 0:
                await anyio.sleep(10)
                return await self._run(attempt - 1)
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
        parsed_spec_message = None
        for line in spec_output.split("\n"):
            try:
                parsed_json = json.loads(line)
                if parsed_json["type"] == "SPEC":
                    parsed_spec_message = parsed_json
                    break
            except (json.JSONDecodeError, KeyError):
                continue
        if parsed_spec_message:
            parsed_spec = parsed_spec_message["spec"]
            try:
                ConnectorSpecification.parse_obj(parsed_spec)
                return json.dumps(parsed_spec)
            except (ValidationError, ValueError) as e:
                raise InvalidSpecOutputError(f"The SPEC message did not pass schema validation: {str(e)}.")
        raise InvalidSpecOutputError("No spec found in the output of the SPEC command.")

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
                flags=['--cache-control="no-cache"'],
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
            if check_connector_image_results.status is StepStatus.SKIPPED and not context.pre_release:
                context.logger.info(
                    "The connector version is already published. Let's upload metadata.yaml to GCS even if no version bump happened."
                )
                metadata_upload_results = await metadata.MetadataUpload(context).run()
                results.append(metadata_upload_results)

            if check_connector_image_results.status is not StepStatus.SUCCESS:
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

            # Make sure the image published is healthy by pulling it and running SPEC on it.
            # See https://github.com/airbytehq/airbyte/issues/26085
            pull_connector_image_results = await PullConnectorImageFromRegistry(context).run()
            results.append(pull_connector_image_results)
            if pull_connector_image_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results)

            if not context.pre_release:
                # Only upload to spec cache bucket if the connector is not a pre-release.
                upload_to_spec_cache_results = await UploadSpecToCache(context).run(built_connector_platform_variants[0])
                results.append(upload_to_spec_cache_results)
                if upload_to_spec_cache_results.status is not StepStatus.SUCCESS:
                    return create_connector_report(results)

                # Only upload to metadata service bucket if the connector is not a pre-release.
                metadata_upload_results = await metadata.MetadataUpload(context).run()
                results.append(metadata_upload_results)

            return create_connector_report(results)
