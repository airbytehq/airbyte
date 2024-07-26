#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any
import git
import logging
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun, run_steps
from pipelines.models.steps import StepResult, StepStatus, Step
from connector_ops.utils import ConnectorLanguage  # type: ignore
from anyio import Semaphore

## GLOBAL VARIABLES

VALID_FILES = [
  "manifest.yaml",
  "run.py",
  "__init__.py",
  "source.py"
]
FILES_TO_LEAVE = [
  "__init__.py"
  "manifest.yaml",
  "metadata.yaml",
  "icon.svg",
  "run.py",
  "source.py",
  "acceptance-test-config.json"
]


class CheckIsManifestMigrationCandidate(Step):
    context: ConnectorContext

    title: str = "Check if the connector is a candidate for migration to poetry."
    airbyte_repo: git.Repo = git.Repo(search_parent_directories=True)
    invalid_files: list = []

    async def _run(self) -> StepResult:
      connector_dir_entries = await (await self.context.get_connector_dir()).entries()
      
      if self.context.connector.language != ConnectorLanguage.LOW_CODE:
        return StepResult(
          step=self,
          status=StepStatus.SKIPPED,
          stderr=f"The connector is not a low-code connector.",
        )
      
      if self.context.connector.language == ConnectorLanguage.MANIFEST_ONLY:
        return StepResult(
          step=self,
          status=StepStatus.SKIPPED,
          stderr="The connector is already in manifest-only format.",
        )
      
      # Detect sus python files in the connector source directory
      connector_source_code_dir = self.context.connector.code_directory / self.context.connector.technical_name.replace("-", "_")
      self.logger.info(f"Checking the connector source code directory: {connector_source_code_dir}")
      for file in connector_source_code_dir.iterdir():
        if file.name not in VALID_FILES:
          self.invalid_files.append(file.name)
      if self.invalid_files:
        self.logger.info(f"Unrecognized files in the connector source code directory: {self.invalid_files}")
        return StepResult(
          step=self,
          status=StepStatus.SKIPPED,
          stdout=f"The connector has unrecognized source files: {self.invalid_files}",
        )
      
      # TODO: Detect connector class name to make sure it's inherited from source declarative manifest 
      # and does not override `streams`

      connector_source_py = (connector_source_code_dir / "source.py").read_text()
      self.logger.info(f"Checking the connector source code: {connector_source_py}")

      if "YamlDeclarativeSource" not in connector_source_py:
        return StepResult(
          step=self,
          status=StepStatus.SKIPPED,
          stdout="The connector does not use the YamlDeclarativeSource class.",
        )
      
      if "def streams" in connector_source_py:
        return StepResult(
          step=self,
          status=StepStatus.SKIPPED,
          stdout="The connector overrides the streams method.",
        )

      return StepResult(
        step=self, 
        status=StepStatus.SUCCESS, 
        stdout=f"{self.context.connector.technical_name} is a valid candidate for migration.")

class StripConnector(Step):
    context: ConnectorContext

    title = "Strip the connector to manifest-only."

    async def _run(self) -> StepResult:
       
      # TODO
      # 1. Move manifest.yaml to the root level of the directory
      connector_source_code_dir = self.context.connector.code_directory / self.context.connector.technical_name.replace("-", "_")
      manifest_file = connector_source_code_dir / "manifest.yaml"
      manifest_file.rename(self.context.connector.code_directory / "manifest.yaml")
      self.logger.info(f"Moved manifest to the root level of the directory")

      # 2. Delete everything that is not in an allow-list of files
      for file in self.context.connector.code_directory.iterdir():
        if file.name not in FILES_TO_LEAVE:
          file.unlink()
          self.logger.info(f"Deleted {file.name}")

      # 3. Write metadata.yaml
      metadata_file = self.context.connector.code_directory / "metadata.yaml"
      metadata = metadata_file.read_text()
      self.logger.info(f"Read metadata.yaml: {metadata}")

      # 4. Pray that the changes are saved automatically
      for file in self.context.connector.code_directory.iterdir():
        if file.name not in FILES_TO_LEAVE:
          return StepResult(
            step=self,
            status=StepStatus.FAILURE,
            stdout="Your prayers were not answered. Please save the changes manually."
          )

      return StepResult(
        step=self,
        status=StepStatus.SUCCESS,
        stdout="The connector has been successfully stripped to manifest-only."
      )

## MAIN FUNCTION
async def run_connectors_strip_pipeline(
    context: ConnectorContext,
    semaphore: "Semaphore",
    *args: Any
  ) -> ConnectorReport:
  
  steps_to_run: STEP_TREE = []
  steps_to_run.append(
    [StepToRun(
      id=CONNECTOR_TEST_STEP_ID.STRIP_CHECK_CANDIDATE,
      step=CheckIsManifestMigrationCandidate(context)
    )]
  )
  
  steps_to_run.append(
    [StepToRun(
      id=CONNECTOR_TEST_STEP_ID.STRIP_MIGRATION,
      step=StripConnector(context),
      depends_on=[CONNECTOR_TEST_STEP_ID.STRIP_CHECK_CANDIDATE]
    )]
  )
  
  async with semaphore:
      async with context:
        result_dict = await run_steps(
            runnables=steps_to_run,
            options=context.run_step_options,
        )
        results = list(result_dict.values())
        # TODO: What do you mean we have to restore shit if things failed?
        # if any(step_result.status is StepStatus.FAILURE for step_result in results):
          # restore code.

        

        report = ConnectorReport(context, steps_results=results, name="STRIP MIGRATION RESULTS")
        context.report = report

  return report

  # TODO: validate_connector:

    # is the connector a low-code connector?
      # if yes, continue. if no, return false

    # does it use our base image?
      # if yes, continue, if no, return false

    # does the connector have custom components?
      # if yes, return false. if no, continue

    # does the source class have any methods other than __init__?
      # if yes, return false. if no, return true
    
  # TODO: strip_connector:

  # for each file in the directory:
  # if the file is named "manifest.yaml", "metadata.yaml", "icon.svg" (acceptance-test-config and samplefiles?)
    # continue
  # else
    # into the dustbin!

  # Update metadata.yaml

  # Move manifest.yaml to the root level of the directory

  # Return the updated directory
