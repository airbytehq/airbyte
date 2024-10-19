#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import anyio
import semver
import yaml
from airbyte_protocol.models.airbyte_protocol import ConnectorSpecification  # type: ignore
from connector_ops.utils import METADATA_FILE_NAME, ConnectorLanguage  # type: ignore
from dagger import Container, Directory, ExecError, File, ImageLayerCompression, Platform, QueryError
from pipelines import consts
from pipelines.airbyte_ci.connectors.build_image import steps
from pipelines.airbyte_ci.connectors.publish.context import PublishConnectorContext, RolloutMode
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.airbyte_ci.metadata.pipeline import MetadataRollbackReleaseCandidate, MetadataUpload, MetadataValidation
from pipelines.airbyte_ci.steps.bump_version import SetConnectorVersion
from pipelines.airbyte_ci.steps.changelog import AddChangelogEntry
from pipelines.airbyte_ci.steps.pull_request import CreateOrUpdatePullRequest
from pipelines.airbyte_ci.steps.python_registry import PublishToPythonRegistry, PythonRegistryPublishContext
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.dagger.actions.remote_storage import upload_to_gcs
from pipelines.dagger.actions.system import docker
from pipelines.helpers.connectors.dagger_fs import dagger_read_file, dagger_write_file
from pipelines.helpers.pip import is_package_published
from pipelines.models.steps import Step, StepModifyingFiles, StepResult, StepStatus
from pydantic import BaseModel, ValidationError


class InvalidSpecOutputError(Exception):
    pass


class CheckConnectorImageDoesNotExist(Step):
    context: PublishConnectorContext
    title = "Check if the connector docker image does not exist on the registry."

    async def _run(self) -> StepResult:
        docker_repository, docker_tag = self.context.docker_image.split(":")
        crane_ls = (
            docker.with_crane(
                self.context,
            )
            .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
            .with_exec(["ls", docker_repository], use_entrypoint=True)
        )
        try:
            crane_ls_stdout = await crane_ls.stdout()
        except ExecError as e:
            if "NAME_UNKNOWN" in e.stderr:
                return StepResult(step=self, status=StepStatus.SUCCESS, stdout=f"The docker repository {docker_repository} does not exist.")
            else:
                return StepResult(step=self, status=StepStatus.FAILURE, stderr=e.stderr, stdout=e.stdout)
        else:  # The docker repo exists and ls was successful
            existing_tags = crane_ls_stdout.split("\n")
            docker_tag_already_exists = docker_tag in existing_tags
            if docker_tag_already_exists:
                return StepResult(step=self, status=StepStatus.SKIPPED, stderr=f"{self.context.docker_image} already exists.")
            return StepResult(step=self, status=StepStatus.SUCCESS, stdout=f"No manifest found for {self.context.docker_image}.")


class CheckPythonRegistryPackageDoesNotExist(Step):
    context: PythonRegistryPublishContext
    title = "Check if the connector is published on python registry"

    async def _run(self) -> StepResult:
        is_published = is_package_published(
            self.context.package_metadata.name, self.context.package_metadata.version, self.context.registry_check_url
        )
        if is_published:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr=f"{self.context.package_metadata.name} already exists in version {self.context.package_metadata.version}.",
            )
        else:
            return StepResult(
                step=self,
                status=StepStatus.SUCCESS,
                stdout=f"{self.context.package_metadata.name} does not exist in version {self.context.package_metadata.version}.",
            )


class ConnectorDependenciesMetadata(BaseModel):
    connector_technical_name: str
    connector_repository: str
    connector_version: str
    connector_definition_id: str
    dependencies: List[Dict[str, str]]
    generation_time: datetime = datetime.utcnow()


class UploadDependenciesToMetadataService(Step):
    context: PublishConnectorContext
    title = "Upload connector dependencies list to GCS."
    key_prefix = "connector_dependencies"

    async def _run(self, built_containers_per_platform: Dict[Platform, Container]) -> StepResult:
        assert self.context.connector.language in [
            ConnectorLanguage.PYTHON,
            ConnectorLanguage.LOW_CODE,
        ], "This step can only run for Python connectors."
        built_container = built_containers_per_platform[LOCAL_BUILD_PLATFORM]
        pip_freeze_output = await built_container.with_exec(["pip", "freeze"]).stdout()
        dependencies = [
            {"package_name": line.split("==")[0], "version": line.split("==")[1]} for line in pip_freeze_output.splitlines() if "==" in line
        ]
        connector_technical_name = self.context.connector.technical_name
        connector_version = self.context.metadata["dockerImageTag"]
        dependencies_metadata = ConnectorDependenciesMetadata(
            connector_technical_name=connector_technical_name,
            connector_repository=self.context.metadata["dockerRepository"],
            connector_version=connector_version,
            connector_definition_id=self.context.metadata["definitionId"],
            dependencies=dependencies,
        ).json()
        file = (
            (await self.context.get_connector_dir())
            .with_new_file("dependencies.json", contents=dependencies_metadata)
            .file("dependencies.json")
        )
        key = f"{self.key_prefix}/{connector_technical_name}/{connector_version}/dependencies.json"
        exit_code, stdout, stderr = await upload_to_gcs(
            self.context.dagger_client,
            file,
            key,
            self.context.metadata_bucket_name,
            self.context.metadata_service_gcs_credentials,
            flags=['--cache-control="no-cache"'],
        )
        if exit_code != 0:
            return StepResult(step=self, status=StepStatus.FAILURE, stdout=stdout, stderr=stderr)
        return StepResult(step=self, status=StepStatus.SUCCESS, stdout="Uploaded connector dependencies to metadata service bucket.")


class PushConnectorImageToRegistry(Step):
    context: PublishConnectorContext
    title = "Push connector image to registry"

    @property
    def latest_docker_image_name(self) -> str:
        return f"{self.context.docker_repository}:latest"

    @property
    def should_push_latest_tag(self) -> bool:
        """
        We don't want to push the latest tag for release candidates or pre-releases.

        Returns:
            bool: True if the latest tag should be pushed, False otherwise.
        """
        is_release_candidate = "-rc" in self.context.connector.version
        is_pre_release = self.context.pre_release
        return not (is_release_candidate or is_pre_release)

    async def _run(self, built_containers_per_platform: List[Container], attempts: int = 3) -> StepResult:
        try:
            image_ref = await built_containers_per_platform[0].publish(
                f"docker.io/{self.context.docker_image}",
                platform_variants=built_containers_per_platform[1:],
                forced_compression=ImageLayerCompression.Gzip,
            )
            if self.should_push_latest_tag:
                image_ref = await built_containers_per_platform[0].publish(
                    f"docker.io/{self.latest_docker_image_name}",
                    platform_variants=built_containers_per_platform[1:],
                    forced_compression=ImageLayerCompression.Gzip,
                )
            return StepResult(step=self, status=StepStatus.SUCCESS, stdout=f"Published {image_ref}")
        except QueryError as e:
            if attempts > 0:
                self.context.logger.error(str(e))
                self.context.logger.warn(f"Failed to publish {self.context.docker_image}. Retrying. {attempts} attempts left.")
                await anyio.sleep(5)
                return await self._run(built_containers_per_platform, attempts - 1)
            return StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e))


class PushVersionImageAsLatest(Step):
    context: PublishConnectorContext
    title = "Push existing version image as latest"

    @property
    def latest_docker_image_name(self) -> str:
        return f"{self.context.docker_repository}:latest"

    async def _run(self, attempts: int = 3) -> StepResult:
        per_platform_containers = [
            self.context.dagger_client.container(platform=platform).from_(f"docker.io/{self.context.docker_image}")
            for platform in consts.BUILD_PLATFORMS
        ]

        try:
            image_ref = await per_platform_containers[0].publish(
                f"docker.io/{self.latest_docker_image_name}",
                platform_variants=per_platform_containers[1:],
                forced_compression=ImageLayerCompression.Gzip,
            )
            return StepResult(step=self, status=StepStatus.SUCCESS, stdout=f"Published {image_ref}")
        except QueryError as e:
            if attempts > 0:
                self.context.logger.error(str(e))
                self.context.logger.warn(f"Failed to publish {self.context.docker_image}. Retrying. {attempts} attempts left.")
                await anyio.sleep(5)
                return await self._run(attempts - 1)
            return StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e))


class PullConnectorImageFromRegistry(Step):
    context: PublishConnectorContext
    title = "Pull connector image from registry"

    async def check_if_image_only_has_gzip_layers(self) -> bool:
        """Check if the image only has gzip layers.
        Docker version > 21 can create images that has some layers compressed with zstd.
        These layers are not supported by previous docker versions.
        We want to make sure that the image we are about to release is compatible with all docker versions.
        We use crane to inspect the manifest of the image and check if it only has gzip layers.
        """
        has_only_gzip_layers = True
        for platform in consts.BUILD_PLATFORMS:
            inspect = docker.with_crane(self.context).with_exec(
                ["manifest", "--platform", f"{str(platform)}", f"docker.io/{self.context.docker_image}"], use_entrypoint=True
            )
            try:
                inspect_stdout = await inspect.stdout()
            except ExecError as e:
                raise Exception(f"Failed to inspect {self.context.docker_image}: {e.stderr}") from e
            try:
                for layer in json.loads(inspect_stdout)["layers"]:
                    if not layer["mediaType"].endswith("gzip"):
                        has_only_gzip_layers = False
                        break
            except (KeyError, json.JSONDecodeError) as e:
                raise Exception(f"Failed to parse manifest for {self.context.docker_image}: {inspect_stdout}") from e
        return has_only_gzip_layers

    async def _run(self, attempt: int = 3) -> StepResult:
        try:
            try:
                await self.context.dagger_client.container().from_(f"docker.io/{self.context.docker_image}").with_exec(
                    ["spec"], use_entrypoint=True
                )
            except ExecError:
                if attempt > 0:
                    await anyio.sleep(10)
                    return await self._run(attempt - 1)
                else:
                    return StepResult(step=self, status=StepStatus.FAILURE, stderr=f"Failed to pull {self.context.docker_image}")
            if not await self.check_if_image_only_has_gzip_layers():
                return StepResult(
                    step=self,
                    status=StepStatus.FAILURE,
                    stderr=f"Image {self.context.docker_image} does not only have gzip compressed layers. Please rebuild the connector with Docker < 21.",
                )
            else:
                return StepResult(
                    step=self,
                    status=StepStatus.SUCCESS,
                    stdout=f"Pulled {self.context.docker_image} and validated it has gzip only compressed layers and we can run spec on it.",
                )
        except QueryError as e:
            if attempt > 0:
                await anyio.sleep(10)
                return await self._run(attempt - 1)
            return StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e))


class UploadSpecToCache(Step):
    context: PublishConnectorContext
    title = "Upload connector spec to spec cache bucket"
    default_spec_file_name = "spec.json"
    cloud_spec_file_name = "spec.cloud.json"

    @property
    def spec_key_prefix(self) -> str:
        return "specs/" + self.context.docker_image.replace(":", "/")

    @property
    def cloud_spec_key(self) -> str:
        return f"{self.spec_key_prefix}/{self.cloud_spec_file_name}"

    @property
    def oss_spec_key(self) -> str:
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
        spec_output = (
            await connector.with_env_variable("DEPLOYMENT_MODE", deployment_mode).with_exec(["spec"], use_entrypoint=True).stdout()
        )
        return self._parse_spec_output(spec_output)

    async def _get_spec_as_file(self, spec: str, name: str = "spec_to_cache.json") -> File:
        return (await self.context.get_connector_dir()).with_new_file(name, contents=spec).file(name)

    async def _run(self, built_connector: Container) -> StepResult:
        try:
            oss_spec: str = await self._get_connector_spec(built_connector, "OSS")
            cloud_spec: str = await self._get_connector_spec(built_connector, "CLOUD")
        except InvalidSpecOutputError as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e))

        specs_to_uploads: List[Tuple[str, File]] = [(self.oss_spec_key, await self._get_spec_as_file(oss_spec))]

        if oss_spec != cloud_spec:
            specs_to_uploads.append((self.cloud_spec_key, await self._get_spec_as_file(cloud_spec, "cloud_spec_to_cache.json")))

        for key, file in specs_to_uploads:
            exit_code, stdout, stderr = await upload_to_gcs(
                self.context.dagger_client,
                file,
                key,
                self.context.spec_cache_bucket_name,
                self.context.spec_cache_gcs_credentials,
                flags=['--cache-control="no-cache"'],
            )
            if exit_code != 0:
                return StepResult(step=self, status=StepStatus.FAILURE, stdout=stdout, stderr=stderr)
        return StepResult(step=self, status=StepStatus.SUCCESS, stdout="Uploaded connector spec to spec cache bucket.")


class UploadSbom(Step):
    context: PublishConnectorContext
    title = "Upload SBOM to metadata service bucket"
    SBOM_KEY_PREFIX = "sbom"
    SYFT_DOCKER_IMAGE = "anchore/syft:v1.6.0"
    SBOM_FORMAT = "spdx-json"
    IN_CONTAINER_SBOM_PATH = "sbom.json"
    SBOM_EXTENSION = "spdx.json"

    def get_syft_container(self) -> Container:
        home_dir = os.path.expanduser("~")
        config_path = os.path.join(home_dir, ".docker", "config.json")
        config_file = self.dagger_client.host().file(config_path)
        return (
            self.dagger_client.container()
            .from_(self.SYFT_DOCKER_IMAGE)
            .with_mounted_file("/config/config.json", config_file)
            .with_env_variable("DOCKER_CONFIG", "/config")
            # Syft requires access to the docker daemon. We share the host's docker socket with the Syft container.
            .with_unix_socket("/var/run/docker.sock", self.dagger_client.host().unix_socket("/var/run/docker.sock"))
        )

    async def _run(self) -> StepResult:
        try:
            syft_container = self.get_syft_container()
            sbom_file = await syft_container.with_exec(
                [self.context.docker_image, "-o", f"{self.SBOM_FORMAT}={self.IN_CONTAINER_SBOM_PATH}"], use_entrypoint=True
            ).file(self.IN_CONTAINER_SBOM_PATH)
        except ExecError as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e), exc_info=e)

        # This will lead to a key like: sbom/airbyte/source-faker/0.1.0.json
        key = f"{self.SBOM_KEY_PREFIX}/{self.context.docker_image.replace(':', '/')}.{self.SBOM_EXTENSION}"
        exit_code, stdout, stderr = await upload_to_gcs(
            self.context.dagger_client,
            sbom_file,
            key,
            self.context.metadata_bucket_name,
            self.context.metadata_service_gcs_credentials,
            flags=['--cache-control="no-cache"', "--content-type=application/json"],
        )
        if exit_code != 0:
            return StepResult(step=self, status=StepStatus.FAILURE, stdout=stdout, stderr=stderr)
        return StepResult(step=self, status=StepStatus.SUCCESS, stdout="Uploaded SBOM to metadata service bucket.")


class SetPromotedVersion(SetConnectorVersion):
    context: PublishConnectorContext
    title = "Promote release candidate"

    @property
    def current_semver_version(self) -> semver.Version:
        return semver.Version.parse(self.context.connector.version)

    @property
    def promoted_semver_version(self) -> semver.Version:
        return self.current_semver_version.replace(prerelease=None)

    @property
    def promoted_version(self) -> str:
        return str(self.promoted_semver_version)

    @property
    def current_version_is_rc(self) -> bool:
        return bool(self.current_semver_version.prerelease and "rc" in self.current_semver_version.prerelease)

    def __init__(self, context: PublishConnectorContext, connector_directory: Directory) -> None:
        self.context = context
        super().__init__(context, connector_directory, self.promoted_version)

    async def _run(self) -> StepResult:
        if not self.current_version_is_rc:
            return StepResult(step=self, status=StepStatus.SKIPPED, stdout="The connector version has no rc suffix.")
        return await super()._run()


class DisableProgressiveRollout(StepModifyingFiles):
    context: PublishConnectorContext
    title = "Disable progressive rollout in metadata file"

    async def _run(self) -> StepResult:
        raw_metadata = await dagger_read_file(await self.context.get_connector_dir(include=METADATA_FILE_NAME), METADATA_FILE_NAME)
        current_metadata = yaml.safe_load(raw_metadata)
        enable_progressive_rollout = (
            current_metadata.get("data", {}).get("releases", {}).get("rolloutConfiguration", {}).get("enableProgressiveRollout", False)
        )
        if not enable_progressive_rollout:
            return StepResult(step=self, status=StepStatus.SKIPPED, stdout="Progressive rollout is already disabled.")
        # We do an in-place replacement instead of serializing back to yaml to preserve comments and formatting.
        new_raw_metadata = raw_metadata.replace("enableProgressiveRollout: true", "enableProgressiveRollout: false")
        self.modified_directory = dagger_write_file(self.modified_directory, METADATA_FILE_NAME, new_raw_metadata)
        self.modified_files.append(METADATA_FILE_NAME)
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout="Set enableProgressiveRollout to false in connector metadata.",
            output=self.modified_directory,
        )


# Helpers
def create_connector_report(results: List[StepResult], context: PublishConnectorContext) -> ConnectorReport:
    """Generate a connector report from results and assign it to the context.

    Args:
        results (List[StepResult]): List of step results.
        context (PublishConnectorContext): The connector context to assign the report to.

    Returns:
        ConnectorReport: The connector report.
    """
    report = ConnectorReport(context, results, name="PUBLISH RESULTS")
    context.report = report
    return report


# Pipeline
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

    assert context.rollout_mode == RolloutMode.PUBLISH, "This pipeline can only run in publish mode."

    metadata_upload_step = MetadataUpload(
        context=context,
        metadata_service_gcs_credentials=context.metadata_service_gcs_credentials,
        docker_hub_username=context.docker_hub_username,
        docker_hub_password=context.docker_hub_password,
        metadata_bucket_name=context.metadata_bucket_name,
        pre_release=context.pre_release,
        pre_release_tag=context.docker_image_tag,
    )

    upload_spec_to_cache_step = UploadSpecToCache(context)

    upload_sbom_step = UploadSbom(context)

    async with semaphore:
        async with context:
            results = []

            metadata_validation_results = await MetadataValidation(context).run()
            results.append(metadata_validation_results)

            # Exit early if the metadata file is invalid.
            if metadata_validation_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results, context)

            check_connector_image_results = await CheckConnectorImageDoesNotExist(context).run()
            results.append(check_connector_image_results)
            python_registry_steps, terminate_early = await _run_python_registry_publish_pipeline(context)
            results.extend(python_registry_steps)
            if terminate_early:
                return create_connector_report(results, context)

            # If the connector image already exists, we don't need to build it, but we still need to upload the metadata file.
            # We also need to upload the spec to the spec cache bucket.
            if check_connector_image_results.status is StepStatus.SKIPPED:
                context.logger.info(
                    "The connector version is already published. Let's upload metadata.yaml and spec to GCS even if no version bump happened."
                )
                already_published_connector = context.dagger_client.container().from_(context.docker_image)
                upload_to_spec_cache_results = await upload_spec_to_cache_step.run(already_published_connector)
                results.append(upload_to_spec_cache_results)
                if upload_to_spec_cache_results.status is not StepStatus.SUCCESS:
                    return create_connector_report(results, context)

                upload_sbom_results = await upload_sbom_step.run()
                results.append(upload_sbom_results)
                if upload_sbom_results.status is not StepStatus.SUCCESS:
                    return create_connector_report(results, context)

                metadata_upload_results = await metadata_upload_step.run()
                results.append(metadata_upload_results)

            # Exit early if the connector image already exists or has failed to build
            if check_connector_image_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results, context)

            build_connector_results = await steps.run_connector_build(context)
            results.append(build_connector_results)

            # Exit early if the connector image failed to build
            if build_connector_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results, context)

            if context.connector.language in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
                upload_dependencies_step = await UploadDependenciesToMetadataService(context).run(build_connector_results.output)
                results.append(upload_dependencies_step)

            built_connector_platform_variants = list(build_connector_results.output.values())
            push_connector_image_results = await PushConnectorImageToRegistry(context).run(built_connector_platform_variants)
            results.append(push_connector_image_results)

            # Exit early if the connector image failed to push
            if push_connector_image_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results, context)

            # Make sure the image published is healthy by pulling it and running SPEC on it.
            # See https://github.com/airbytehq/airbyte/issues/26085
            pull_connector_image_results = await PullConnectorImageFromRegistry(context).run()
            results.append(pull_connector_image_results)

            # Exit early if the connector image failed to pull
            if pull_connector_image_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results, context)

            upload_to_spec_cache_results = await upload_spec_to_cache_step.run(built_connector_platform_variants[0])
            results.append(upload_to_spec_cache_results)
            if upload_to_spec_cache_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results, context)

            upload_sbom_results = await upload_sbom_step.run()
            results.append(upload_sbom_results)
            if upload_sbom_results.status is not StepStatus.SUCCESS:
                return create_connector_report(results, context)

            metadata_upload_results = await metadata_upload_step.run()
            results.append(metadata_upload_results)
            connector_report = create_connector_report(results, context)
    return connector_report


async def _run_python_registry_publish_pipeline(context: PublishConnectorContext) -> Tuple[List[StepResult], bool]:
    """
    Run the python registry publish pipeline for a single connector.
    Return the results of the steps and a boolean indicating whether there was an error and the pipeline should be stopped.
    """
    results: List[StepResult] = []
    # Try to convert the context to a PythonRegistryPublishContext. If it returns None, it means we don't need to publish to a python registry.
    python_registry_context = await PythonRegistryPublishContext.from_publish_connector_context(context)
    if not python_registry_context:
        return results, False

    if not context.python_registry_token or not context.python_registry_url:
        # If the python registry token or url are not set, we can't publish to the python registry - stop the pipeline.
        return [
            StepResult(
                step=PublishToPythonRegistry(python_registry_context),
                status=StepStatus.FAILURE,
                stderr="Pypi publishing is enabled, but python registry token or url are not set.",
            )
        ], True

    check_python_registry_package_exists_results = await CheckPythonRegistryPackageDoesNotExist(python_registry_context).run()
    results.append(check_python_registry_package_exists_results)
    if check_python_registry_package_exists_results.status is StepStatus.SKIPPED:
        context.logger.info("The connector version is already published on python registry.")
    elif check_python_registry_package_exists_results.status is StepStatus.SUCCESS:
        context.logger.info("The connector version is not published on python registry. Let's build and publish it.")
        publish_to_python_registry_results = await PublishToPythonRegistry(python_registry_context).run()
        results.append(publish_to_python_registry_results)
        if publish_to_python_registry_results.status is StepStatus.FAILURE:
            return results, True
    elif check_python_registry_package_exists_results.status is StepStatus.FAILURE:
        return results, True

    return results, False


def get_rollback_pr_creation_arguments(
    modified_files: Iterable[Path],
    context: PublishConnectorContext,
    step_results: Iterable[StepResult],
    release_candidate_version: str,
) -> Tuple[Tuple, Dict]:
    return (modified_files,), {
        "branch_id": f"{context.connector.technical_name}/rollback-{release_candidate_version}",
        "commit_message": "\n".join(step_result.step.title for step_result in step_results if step_result.success),
        "pr_title": f"🐙 {context.connector.technical_name}: Stop progressive rollout for {release_candidate_version}",
        "pr_body": f"The release candidate version {release_candidate_version} has been deemed unstable. This PR stops its progressive rollout.",
    }


async def run_connector_rollback_pipeline(context: PublishConnectorContext, semaphore: anyio.Semaphore) -> ConnectorReport:
    """Run a rollback pipeline for a single connector.

    1. Disable progressive rollout in metadata file.
    2. Open a PR with the updated metadata, set the auto-merge label.

    Returns:
        ConnectorReport: The reports holding promote results.
    """

    results = []
    current_version = context.connector.version
    all_modified_files = set()
    async with semaphore:
        async with context:
            assert context.rollout_mode == RolloutMode.ROLLBACK, "This pipeline can only run in rollback mode."
            original_connector_directory = await context.get_connector_dir()

            # Disable progressive rollout in metadata file
            reset_release_candidate = DisableProgressiveRollout(context, original_connector_directory)
            reset_release_candidate_results = await reset_release_candidate.run()
            results.append(reset_release_candidate_results)
            if reset_release_candidate_results.success:
                all_modified_files.update(await reset_release_candidate.export_modified_files(context.connector.code_directory))

            if not all([result.success for result in results]):
                context.logger.error("The metadata update failed. Skipping PR creation.")
                connector_report = create_connector_report(results, context)
                return connector_report

            # Open PR when all previous steps are successful
            initial_pr_creation = CreateOrUpdatePullRequest(context, skip_ci=False, labels=["auto-merge"])
            pr_creation_args, pr_creation_kwargs = get_rollback_pr_creation_arguments(all_modified_files, context, results, current_version)
            initial_pr_creation_result = await initial_pr_creation.run(*pr_creation_args, **pr_creation_kwargs)
            results.append(initial_pr_creation_result)

            connector_report = create_connector_report(results, context)
    return connector_report


def get_promotion_pr_creation_arguments(
    modified_files: Iterable[Path],
    context: PublishConnectorContext,
    step_results: Iterable[StepResult],
    release_candidate_version: str,
    promoted_version: str,
) -> Tuple[Tuple, Dict]:
    return (modified_files,), {
        "branch_id": f"{context.connector.technical_name}/{promoted_version}",
        "commit_message": "\n".join(step_result.step.title for step_result in step_results if step_result.success),
        "pr_title": f"🐙 {context.connector.technical_name}: release {promoted_version}",
        "pr_body": f"The release candidate version {release_candidate_version} has been deemed stable and is now ready to be promoted to an official release ({promoted_version}).",
    }


async def run_connector_promote_pipeline(context: PublishConnectorContext, semaphore: anyio.Semaphore) -> ConnectorReport:
    """Run a promote pipeline for a single connector.

    1. Update connector metadata to:
        * Remove the RC suffix from the version.
        * Disable progressive rollout.
    2. Open a PR with the updated metadata.
    3. Add a changelog entry to the documentation.
    4. Update the PR with the updated changelog, set the auto-merge label.

    Returns:
        ConnectorReport: The reports holding promote results.
    """

    results = []
    current_version = context.connector.version
    all_modified_files = set()
    async with semaphore:
        async with context:
            assert context.rollout_mode == RolloutMode.PROMOTE, "This pipeline can only run in promote mode."
            original_connector_directory = await context.get_connector_dir()
            # Remove RC suffix
            set_promoted_version = SetPromotedVersion(context, original_connector_directory)
            set_promoted_version_results = await set_promoted_version.run()
            results.append(set_promoted_version_results)
            if set_promoted_version_results.success:
                all_modified_files.update(await set_promoted_version.export_modified_files(context.connector.code_directory))

            # Disable progressive rollout in metadata file
            reset_release_candidate = DisableProgressiveRollout(context, set_promoted_version_results.output)
            reset_release_candidate_results = await reset_release_candidate.run()
            results.append(reset_release_candidate_results)
            if reset_release_candidate_results.success:
                all_modified_files.update(await reset_release_candidate.export_modified_files(context.connector.code_directory))

            if not all([result.success for result in results]):
                context.logger.error("The metadata update failed. Skipping PR creation.")
                connector_report = create_connector_report(results, context)
                return connector_report

            # Open PR when all previous steps are successful
            promoted_version = set_promoted_version.promoted_version
            initial_pr_creation = CreateOrUpdatePullRequest(context, skip_ci=True)
            pr_creation_args, pr_creation_kwargs = get_promotion_pr_creation_arguments(
                all_modified_files, context, results, current_version, promoted_version
            )
            initial_pr_creation_result = await initial_pr_creation.run(*pr_creation_args, **pr_creation_kwargs)
            results.append(initial_pr_creation_result)
            # Update changelog and update PR
            if initial_pr_creation_result.success:
                created_pr = initial_pr_creation_result.output
                documentation_directory = await context.get_repo_dir(
                    include=[str(context.connector.local_connector_documentation_directory)]
                ).directory(str(context.connector.local_connector_documentation_directory))
                add_changelog_entry = AddChangelogEntry(
                    context,
                    documentation_directory,
                    promoted_version,
                    f"Promoting release candidate {current_version} to a main version.",
                    created_pr.number,
                )
                add_changelog_entry_result = await add_changelog_entry.run()
                results.append(add_changelog_entry_result)
                if add_changelog_entry_result.success:
                    all_modified_files.update(
                        await add_changelog_entry.export_modified_files(context.connector.local_connector_documentation_directory)
                    )
                post_changelog_pr_update = CreateOrUpdatePullRequest(context, skip_ci=False, labels=["auto-merge"])
                pr_creation_args, pr_creation_kwargs = get_promotion_pr_creation_arguments(
                    all_modified_files, context, results, current_version, promoted_version
                )
                post_changelog_pr_update_result = await post_changelog_pr_update.run(*pr_creation_args, **pr_creation_kwargs)
                results.append(post_changelog_pr_update_result)

            connector_report = create_connector_report(results, context)
    return connector_report


def reorder_contexts(contexts: List[PublishConnectorContext]) -> List[PublishConnectorContext]:
    """Reorder contexts so that the ones that are for strict-encrypt/secure connectors come first.
    The metadata upload on publish checks if the the connectors referenced in the metadata file are already published to DockerHub.
    Non strict-encrypt variant reference the strict-encrypt variant in their metadata file for cloud.
    So if we publish the non strict-encrypt variant first, the metadata upload will fail if the strict-encrypt variant is not published yet.
    As strict-encrypt variant are often modified in the same PR as the non strict-encrypt variant, we want to publish them first.
    """

    def is_secure_variant(context: PublishConnectorContext) -> bool:
        SECURE_VARIANT_KEYS = ["secure", "strict-encrypt"]
        return any(key in context.connector.technical_name for key in SECURE_VARIANT_KEYS)

    return sorted(contexts, key=lambda context: (is_secure_variant(context), context.connector.technical_name), reverse=True)
