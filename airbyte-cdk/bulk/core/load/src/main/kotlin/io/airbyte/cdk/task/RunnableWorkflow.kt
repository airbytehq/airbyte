package io.airbyte.cdk.task


import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch

interface RunnableWorkflow<T: Workflow> {
    val taskRunner: TaskQueue
    val workflowFactory: WorkflowFactory<T>

    suspend fun run() = coroutineScope {
        launch { taskRunner.start() }
        launch { workflowFactory.make(taskRunner).start() }
    }
}

@Singleton
@Secondary
class DestinationWriterWorkflowRunnable(
    override val taskRunner: TaskQueue,
    override val workflowFactory: DestinationWriterWorkflowFactory
) : RunnableWorkflow<DestinationWriterWorkflow>

@Singleton
@Secondary
class DestinationWriterCleanupWorkflowRunnable(
    override val taskRunner: TaskQueue,
    override val workflowFactory: DestinationWriterCleanupWorkflowFactory
) : RunnableWorkflow<DestinationWriterCleanupWorkflow>
