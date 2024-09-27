package io.airbyte.cdk.task

import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

class DestinationWriterCleanupWorkflow(
    override val taskRunner: TaskQueue
): Workflow {
    override suspend fun start() {
        throw NotImplementedError()
    }
}

@Singleton
@Secondary
class DestinationWriterCleanupWorkflowFactory: WorkflowFactory<DestinationWriterCleanupWorkflow> {
    override fun make(taskRunner: TaskQueue): DestinationWriterCleanupWorkflow {
        return DestinationWriterCleanupWorkflow(taskRunner)
    }
}
