#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, List

from connector_ops.utils import ConnectorLanguage  # type: ignore
from pipelines import main_logger
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.connectors.reports import Report
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.helpers.connectors.command import run_connector_steps
from pipelines.helpers.connectors.format import format_prettier
from pipelines.helpers.connectors.yaml import read_yaml, write_yaml
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore

SCHEMAS_DIR_NAME = "schemas"


class CheckIsInlineCandidate(Step):
    """Check if the connector is a candidate to get inline schemas.
    Candidate conditions:
    - The connector is a Python connector.
    - The connector is a source connector.
    - The connector has a manifest file.
    - The connector has schemas directory.
    """

    context: ConnectorContext

    title = "Check if the connector is a candidate for inline schema migration."

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)

    async def _run(self) -> StepResult:
        connector = self.context.connector
        manifest_path = connector.manifest_path
        python_path = connector.python_source_dir_path
        if connector.language not in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector is not a Python connector.",
            )
        if connector.connector_type != "source":
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector is not a source connector.",
            )

        if not manifest_path.is_file():
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector does not have a manifest file.",
            )

        schemas_dir = python_path / SCHEMAS_DIR_NAME
        if not schemas_dir.is_dir():
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector does not have a schemas directory.",
            )

        # TODO: does this help or not?
        # if _has_subdirectory(schemas_dir):
        #     return StepResult(step=self, status=StepStatus.SKIPPED, stderr="This has subdirectories. It's probably complicated.")

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )


def copy_directory(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


class RestoreInlineState(Step):
    context: ConnectorContext

    title = "Restore original state"

    def __init__(self, context: ConnectorContext) -> None:
        super().__init__(context)
        self.manifest_path = context.connector.manifest_path
        self.original_manifest = None
        if self.manifest_path.is_file():
            self.original_manifest = self.manifest_path.read_text()

        self.schemas_path = context.connector.python_source_dir_path / SCHEMAS_DIR_NAME
        self.backup_schema_path = None
        if self.schemas_path.is_dir():
            self.backup_schema_path = Path(tempfile.mkdtemp())
            copy_directory(self.schemas_path, self.backup_schema_path)

    async def _run(self) -> StepResult:
        if self.original_manifest:
            self.manifest_path.write_text(self.original_manifest)

        if self.backup_schema_path:
            copy_directory(self.backup_schema_path, self.schemas_path)

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )

    async def _cleanup(self) -> StepResult:
        if self.backup_schema_path:
            shutil.rmtree(self.backup_schema_path)
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )


class InlineSchemas(Step):
    context: ConnectorContext

    title = "Migrate connector to inline schemas."

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)

    async def _run(self) -> StepResult:
        connector = self.context.connector
        connector_path = connector.code_directory
        manifest_path = connector.manifest_path
        python_path = connector.python_source_dir_path
        logger = self.logger

        json_streams = _parse_json_streams(python_path)
        if len(json_streams) == 0:
            return StepResult(step=self, status=StepStatus.SKIPPED, stderr="No JSON streams found.")

        data = read_yaml(manifest_path)
        if "streams" not in data:
            return StepResult(step=self, status=StepStatus.SKIPPED, stderr="No manifest streams found.")

        # find the explit ones and remove or udpate
        json_loaders = _find_json_loaders(data, [])
        for loader in json_loaders:
            logger.info(f"     JSON loader ref: {loader.ref} -> {loader.file_path}")

        _update_json_loaders(connector_path, data, json_streams, json_loaders)

        # go through the declared streams and update the inline schemas
        for stream in data["streams"]:
            if isinstance(stream, str):
                # see if reference
                if stream.startswith("#"):
                    yaml_stream = _load_reference(data, stream)
                    if not yaml_stream:
                        logger.info(f"    Stream reference not found: {stream}")
                        continue
                    if not _get_stream_name(yaml_stream):
                        logger.info(f"    Stream reference name not found: {stream}")
                        continue
                else:
                    logger.info(f"    Stream reference unknown: {stream}")
                    continue
            else:
                yaml_stream = stream

            if not yaml_stream:
                logger.info(f"    !! Yaml stream not found: {stream}")
                continue

            stream_name = _get_stream_name(yaml_stream)
            if not stream_name:
                logger.info(f"    !! Stream name not found: {stream}")
                continue
            if yaml_stream.get("schema_loader") and yaml_stream["schema_loader"].get("type") == "InlineSchemaLoader":
                continue

            yaml_stream["schema_loader"] = {}
            schema_loader = yaml_stream["schema_loader"]
            _update_inline_schema(schema_loader, json_streams, stream_name)

        write_yaml(data, manifest_path)
        await format_prettier([manifest_path])

        for json_stream in json_streams.values():
            logger.info(f"     !! JSON schema not found: {json_stream.name}")

        return StepResult(step=self, status=StepStatus.SUCCESS)


@dataclass
class JsonStream:
    name: str
    schema: dict
    file_path: Path


@dataclass
class JsonLoaderNode:
    ref: str
    file_path: str


def _has_subdirectory(directory: Path) -> bool:
    # Iterate through all items in the directory
    for entry in directory.iterdir():
        # Check if this entry is a directory
        if entry.is_dir():
            return True

    return False


def _get_stream_name(yaml_stream: dict) -> str | None:
    if "name" in yaml_stream:
        return yaml_stream["name"]
    if "$parameters" in yaml_stream and "name" in yaml_stream["$parameters"]:
        return yaml_stream["$parameters"]["name"]
    return None


def _update_json_loaders(
    connector_path: Path,
    data: dict,
    streams: dict[str, JsonStream],
    loaders: List[JsonLoaderNode],
) -> None:
    logger = main_logger
    for loader in loaders:
        if "{{" in loader.file_path:
            # remove templated paths and their references
            (f"    Removing reference: {loader.ref}")
            _remove_reference(data, None, loader, [])
            continue
        else:
            # direct pointer to a file. update.
            file_path = Path(os.path.abspath(os.path.join(connector_path, loader.file_path)))
            if not file_path.is_file():
                logger.info(f"    JsonFileSchemaLoader not found: {file_path}")
                continue
            schema_loader = _load_reference(data, loader.ref)
            if not schema_loader:
                logger.info(f"    JsonFileSchemaLoader reference not found: {loader.ref}")
                continue
            _update_inline_schema(schema_loader, streams, file_path.stem)


def _update_inline_schema(schema_loader: dict, json_streams: dict[str, JsonStream], file_name: str) -> None:
    logger = main_logger
    if file_name not in json_streams:
        logger.info(f"    Stream {file_name} not found in JSON schemas.")
        return

    json_stream = json_streams[file_name]
    schema_loader["type"] = "InlineSchemaLoader"
    schema_loader["schema"] = json_stream.schema

    json_stream.file_path.unlink()
    json_streams.pop(file_name)


def _remove_reference(parent: Any, key: str | int | None, loader: JsonLoaderNode, path: List[str]) -> bool:  # noqa: ANN401
    logger = main_logger
    if key is None:
        data = parent
    else:
        data = parent[key]

    if isinstance(data, dict):
        ref = f"#/{'/'.join(path)}"
        if ref == loader.ref:
            logger.info(f"        Removing reference: {ref}")
            return True
        elif "$ref" in data and data["$ref"] == loader.ref:
            logger.info(f"        Found reference: {ref}")
            return True
        else:
            todelete = []
            for key, value in data.items():
                if _remove_reference(data, key, loader, path + [str(key)]):
                    todelete.append(key)
            for key in todelete:
                del data[key]
    elif isinstance(data, list):
        for i, value in enumerate(data):
            ref = f"Array[{str(i)}]"
            _remove_reference(data, i, loader, path + [ref])

    return False


def _load_reference(data: dict, ref: str) -> dict | None:
    yaml_stream = data
    path = ref.split("/")
    for p in path:
        if p == "#":
            continue
        if p.startswith("Array["):
            i = int(p[6:-1])
            if not isinstance(yaml_stream, list) or len(yaml_stream) <= i:
                return None
            yaml_stream = yaml_stream[i]
            continue
        if p not in yaml_stream:
            return None
        yaml_stream = yaml_stream[p]
    return yaml_stream


def _find_json_loaders(data: Any, path: List[str]) -> List[JsonLoaderNode]:  # noqa: ANN401
    logger = main_logger
    loaders: List[JsonLoaderNode] = []
    if isinstance(data, dict):
        if "type" in data and data["type"] == "JsonFileSchemaLoader":
            ref = f"#/{'/'.join(path)}"
            if "file_path" in data:
                loaders.append(JsonLoaderNode(ref, data["file_path"]))
            else:
                logger.info(f"    !! JsonFileSchemaLoader missing file_path: {ref}")
        else:
            for key, value in data.items():
                loaders += _find_json_loaders(value, path + [key])
    elif isinstance(data, list):
        for i, value in enumerate(data):
            loaders += _find_json_loaders(value, path + [f"Array[{str(i)}]"])
    return loaders


def _parse_json_streams(python_path: Path) -> dict[str, JsonStream]:
    streams: dict[str, JsonStream] = {}
    schemas_path = python_path / SCHEMAS_DIR_NAME
    if not schemas_path.is_dir():
        return streams

    for schema_file in schemas_path.iterdir():
        if schema_file.is_file() and schema_file.suffix == ".json":
            stream_name = schema_file.stem
            with schema_file.open("r") as file:
                # read json
                schema = json.load(file)
                streams[stream_name] = JsonStream(
                    name=stream_name,
                    schema=schema,
                    file_path=schema_file,
                )

    return streams


async def run_connector_migrate_to_inline_schemas_pipeline(context: ConnectorContext, semaphore: "Semaphore") -> Report:
    restore_original_state = RestoreInlineState(context)

    context.targeted_platforms = [LOCAL_BUILD_PLATFORM]

    steps_to_run: STEP_TREE = []

    steps_to_run.append([StepToRun(id=CONNECTOR_TEST_STEP_ID.INLINE_CANDIDATE, step=CheckIsInlineCandidate(context))])

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.INLINE_MIGRATION,
                step=InlineSchemas(context),
                depends_on=[CONNECTOR_TEST_STEP_ID.INLINE_CANDIDATE],
            )
        ]
    )

    return await run_connector_steps(context, semaphore, steps_to_run, restore_original_state=restore_original_state)
