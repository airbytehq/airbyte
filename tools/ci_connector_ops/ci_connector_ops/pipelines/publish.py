#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import uuid
from typing import List, Tuple

import anyio
from airbyte_protocol.models.airbyte_protocol import ConnectorSpecification
from ci_connector_ops.pipelines import builds, consts
from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.actions.remote_storage import upload_to_gcs
from ci_connector_ops.pipelines.bases import ConnectorReport, Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import PublishConnectorContext
from ci_connector_ops.pipelines.pipelines import metadata
from dagger import Container, ExecError, File, ImageLayerCompression, QueryError
from pydantic import ValidationError


class CheckConnectorImageDoesNotExist(Step):
    title = "Check if the connector docker image does not exist on the registry."

    async def _run(self) -> StepResult:
        docker_repository, docker_tag = self.context.docker_image_name.split(":")
        crane_ls = (
            environments.with_crane(
                self.context,
            )
            .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
            .with_exec(["ls", docker_repository])
        )
        try:
            crane_ls_stdout = await crane_ls.stdout()
        except ExecError as e:
            if "NAME_UNKNOWN" in e.stderr:
                return StepResult(self, status=StepStatus.SUCCESS, stdout=f"The docker repository {docker_repository} does not exist.")
            else:
                return StepResult(self, status=StepStatus.FAILURE, stderr=e.stderr, stdout=e.stdout)
        else:  # The docker repo exists and ls was successful
            existing_tags = crane_ls_stdout.split("\n")
            docker_tag_already_exists = docker_tag in existing_tags
            if docker_tag_already_exists:
                return StepResult(self, status=StepStatus.SKIPPED, stderr=f"{self.context.docker_image_name} already exists.")
            return StepResult(self, status=StepStatus.SUCCESS, stdout=f"No manifest found for {self.context.docker_image_name}.")


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
        for platform in consts.BUILD_PLATFORMS:
            inspect = environments.with_crane(self.context).with_exec(
                ["manifest", "--platform", f"{str(platform)}", f"docker.io/{self.context.docker_image_name}"]
            )
            try:
                inspect_stdout = await inspect.stdout()
            except ExecError as e:
                raise Exception(f"Failed to inspect {self.context.docker_image_name}: {e.stderr}") from e
            try:
                for layer in json.loads(inspect_stdout)["layers"]:
                    if not layer["mediaType"].endswith("gzip"):
                        return False
                return True
            except (KeyError, json.JSONDecodeError) as e:
                raise Exception(f"Failed to parse manifest for {self.context.docker_image_name}: {inspect_stdout}") from e

    async def _run(self, attempt: int = 3) -> StepResult:
        try:
            try:
                await self.context.dagger_client.container().from_(f"docker.io/{self.context.docker_image_name}").with_exec(["spec"])
            except ExecError:
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

    if not context.pre_release:
        metadata_upload_step = metadata.MetadataUpload(
            context=context,
            metadata_service_gcs_credentials_secret=context.metadata_service_gcs_credentials_secret,
            docker_hub_username_secret=context.docker_hub_username_secret,
            docker_hub_password_secret=context.docker_hub_password_secret,
            metadata_bucket_name=context.metadata_bucket_name,
            metadata_path=context.metadata_path,
        )
    else:
        metadata_upload_step = None

    def create_connector_report(results: List[StepResult]) -> ConnectorReport:
        report = ConnectorReport(context, results, name="PUBLISH RESULTS")
        context.report = report
        return report

    async with semaphore:
        async with context:
            # TODO add a strucutre to hold the results of each step. and perform skips and failures.

            results = []

            metadata_validation_results = await metadata.MetadataValidation(context, context.metadata_path).run()
            results.append(metadata_validation_results)

            # Exit early if the metadata file is invalid.
            if metadata_validation_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results)

            check_connector_image_results = await CheckConnectorImageDoesNotExist(context).run()
            results.append(check_connector_image_results)

            # If the connector image already exists, we don't need to build it, but we still need to upload the metadata file.
            # We also need to upload the spec to the spec cache bucket.
            if check_connector_image_results.status is StepStatus.SKIPPED and not context.pre_release:
                context.logger.info(
                    "The connector version is already published. Let's upload metadata.yaml and spec to GCS even if no version bump happened."
                )
                already_published_connector = context.dagger_client.container().from_(context.docker_image_from_metadata)
                upload_to_spec_cache_results = await UploadSpecToCache(context).run(already_published_connector)
                results.append(upload_to_spec_cache_results)
                if upload_to_spec_cache_results.status is not StepStatus.SUCCESS:
                    return create_connector_report(results)
                metadata_upload_results = await metadata_upload_step.run()
                results.append(metadata_upload_results)

            # Exit early if the connector image already exists or has failed to build
            if check_connector_image_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results)

            build_connector_results = await builds.run_connector_build(context)
            results.append(build_connector_results)

            # Exit early if the connector image failed to build
            if build_connector_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results)

            built_connector_platform_variants = list(build_connector_results.output_artifact.values())
            push_connector_image_results = await PushConnectorImageToRegistry(context).run(built_connector_platform_variants)
            results.append(push_connector_image_results)

            # Exit early if the connector image failed to push
            if push_connector_image_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results)

            # Make sure the image published is healthy by pulling it and running SPEC on it.
            # See https://github.com/airbytehq/airbyte/issues/26085
            pull_connector_image_results = await PullConnectorImageFromRegistry(context).run()
            results.append(pull_connector_image_results)

            # Exit early if the connector image failed to pull
            if pull_connector_image_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results)

            upload_to_spec_cache_results = await UploadSpecToCache(context).run(built_connector_platform_variants[0])
            results.append(upload_to_spec_cache_results)
            if upload_to_spec_cache_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results)

            if not context.pre_release:
                # Only upload to metadata service bucket if the connector is not a pre-release.
                metadata_upload_results = await metadata_upload_step.run()
                results.append(metadata_upload_results)

            return create_connector_report(results)


def reorder_contexts(contexts: List[PublishConnectorContext]) -> List[PublishConnectorContext]:
    """Reorder contexts so that the ones that are for strict-encrypt/secure connectors come first.
    The metadata upload on publish checks if the the connectors referenced in the metadata file are already published to DockerHub.
    Non strict-encrypt variant reference the strict-encrypt variant in their metadata file for cloud.
    So if we publish the non strict-encrypt variant first, the metadata upload will fail if the strict-encrypt variant is not published yet.
    As strict-encrypt variant are often modified in the same PR as the non strict-encrypt variant, we want to publish them first.
    This is an hacky approach: as connector names with -strict-encrypt/secure prefix are longer,
    they will be sorted first with our reverse sort below.
    """

    return sorted(contexts, key=lambda context: context.connector.technical_name, reverse=True)
