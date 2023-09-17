#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import anyio
from pipelines.autocommit import base_image, common
from pipelines.bases import ConnectorReport, StepStatus
from pipelines.contexts import ConnectorContext


async def run_connector_autocommit_pipeline(context: ConnectorContext, semaphore: anyio.Semaphore) -> ConnectorReport:
    """Run a autocommit pipeline for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        ConnectorReport: The reports holding autocommit results.
    """
    steps_results = []
    async with context:
        update_base_image_in_metadata = base_image.UpdateBaseImageInMetadata(context)
        update_base_image_in_metadata_result = await update_base_image_in_metadata.run()
        steps_results.append(update_base_image_in_metadata_result)
        if all([result.status is StepStatus.SUCCESS for result in steps_results]):
            git_push_changes_results = await common.GitPushChanges(
                context, container_with_airbyte_repo=update_base_image_in_metadata_result.output_artifact
            ).run()
            steps_results.append(git_push_changes_results)
        context.report = ConnectorReport(context, steps_results, name="AUTOCOMMIT RESULTS")
    return context.report
