/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.SpilledRawMessagesLocalFile
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.implementor.CloseStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.OpenStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.ProcessBatchTaskFactory
import io.airbyte.cdk.load.task.implementor.ProcessRecordsTaskFactory
import io.airbyte.cdk.load.task.implementor.SetupTaskFactory
import io.airbyte.cdk.load.task.implementor.TeardownTaskFactory
import io.airbyte.cdk.load.task.internal.FlushCheckpointsTaskFactory
import io.airbyte.cdk.load.task.internal.InputConsumerTask
import io.airbyte.cdk.load.task.internal.SpillToDiskTaskFactory
import io.airbyte.cdk.load.task.internal.TimedForcedCheckpointFlushTask
import io.airbyte.cdk.load.task.internal.UpdateCheckpointsTask
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

interface DestinationTaskLauncher : TaskLauncher {
    suspend fun handleSetupComplete()
    suspend fun handleStreamStarted(stream: DestinationStream)
    suspend fun handleNewSpilledFile(
        stream: DestinationStream,
        wrapped: BatchEnvelope<SpilledRawMessagesLocalFile>,
        endOfStream: Boolean
    )
    suspend fun handleNewBatch(stream: DestinationStream, wrapped: BatchEnvelope<*>)
    suspend fun handleStreamClosed(stream: DestinationStream)
    suspend fun handleTeardownComplete()
}

/**
 * Governs the task workflow for the entire destination life-cycle.
 *
 * The domain is "decide what to do next given the reported results of the individual task."
 *
 * The workflow is as follows:
 *
 * 1. Start the destination setup task.
 * 2. Start the spill-to-disk task for each stream
 * 3. When setup completes, start the open stream task for each stream
 * 4. When each new spilled file is ready, start the process records task
 * ```
 *    (This task will wait if open stream is not yet complete for that stream.)
 * ```
 * 5. When each batch is ready
 * ```
 *    - update the batch state in the stream manager
 *    - if the batch is not complete, start the process batch task
 *    - if the batch is complete and all batches are complete, start the close stream task
 * ```
 * 6. When the stream is closed
 * ```
 *    - mark the stream as closed in the stream manager
 *    - start the teardown task
 *    (The teardown task will only run once, and only after all streams are closed.)
 * ```
 * 7. When the teardown task is complete, stop the task launcher
 *
 * // TODO: Capture failures, retry, and call into close(failure=true) if can't recover.
 */
@Singleton
@Secondary
@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "arguments are guaranteed to be non-null by Kotlin's type system"
)
class DefaultDestinationTaskLauncher(
    private val taskScopeProvider: TaskScopeProvider<WrappedTask<ScopedTask>>,
    private val catalog: DestinationCatalog,
    private val syncManager: SyncManager,

    // Internal Tasks
    private val inputConsumerTask: InputConsumerTask,
    private val spillToDiskTaskFactory: SpillToDiskTaskFactory,

    // Implementor Tasks
    private val setupTaskFactory: SetupTaskFactory,
    private val openStreamTaskFactory: OpenStreamTaskFactory,
    private val processRecordsTaskFactory: ProcessRecordsTaskFactory,
    private val processBatchTaskFactory: ProcessBatchTaskFactory,
    private val closeStreamTaskFactory: CloseStreamTaskFactory,
    private val teardownTaskFactory: TeardownTaskFactory,

    // Checkpoint Tasks
    private val flushCheckpointsTaskFactory: FlushCheckpointsTaskFactory,
    private val timedFlushTask: TimedForcedCheckpointFlushTask,
    private val updateCheckpointsTask: UpdateCheckpointsTask,

    // Exception handling
    private val exceptionHandler: TaskExceptionHandler<LeveledTask, WrappedTask<ScopedTask>>
) : DestinationTaskLauncher {
    private val log = KotlinLogging.logger {}

    private val batchUpdateLock = Mutex()

    private suspend fun enqueue(task: LeveledTask) {
        taskScopeProvider.launch(exceptionHandler.withExceptionHandling(task))
    }

    override suspend fun start() {
        // Start the input consumer ASAP
        log.info { "Starting input consumer task" }
        enqueue(inputConsumerTask)

        // Launch the client interface setup task
        log.info { "Starting startup task" }
        val setupTask = setupTaskFactory.make(this)
        enqueue(setupTask)

        // Start a spill-to-disk task for each record stream
        catalog.streams.forEach { stream ->
            log.info { "Starting spill-to-disk task for $stream" }
            val spillTask = spillToDiskTaskFactory.make(this, stream)
            enqueue(spillTask)
        }

        log.info { "Starting timed flush task" }
        enqueue(timedFlushTask)

        log.info { "Starting checkpoint update task" }
        enqueue(updateCheckpointsTask)
    }

    /** Called when the initial destination setup completes. */
    override suspend fun handleSetupComplete() {
        catalog.streams.forEach {
            log.info { "Starting open stream task for $it" }
            val openStreamTask = openStreamTaskFactory.make(this, it)
            enqueue(openStreamTask)
        }
    }

    /** Called when a stream is ready for loading. */
    override suspend fun handleStreamStarted(stream: DestinationStream) {
        // Nothing to do because the SpillToDiskTask will trigger the next calls
        log.info { "Stream ${stream.descriptor} successfully opened for writing." }
    }

    /** Called for each new spilled file. */
    override suspend fun handleNewSpilledFile(
        stream: DestinationStream,
        wrapped: BatchEnvelope<SpilledRawMessagesLocalFile>,
        endOfStream: Boolean
    ) {
        log.info { "Starting process records task for ${stream.descriptor}, file ${wrapped.batch}" }
        val task = processRecordsTaskFactory.make(this, stream, wrapped)
        enqueue(task)
        if (!endOfStream) {
            log.info { "End-of-stream not reached, restarting spill-to-disk task for $stream" }
            val spillTask = spillToDiskTaskFactory.make(this, stream)
            enqueue(spillTask)
        }
    }

    /**
     * Called for each new batch. Enqueues processing for any incomplete batch, and enqueues closing
     * the stream if all batches are complete.
     */
    override suspend fun handleNewBatch(stream: DestinationStream, wrapped: BatchEnvelope<*>) {
        batchUpdateLock.withLock {
            val streamManager = syncManager.getStreamManager(stream.descriptor)
            streamManager.updateBatchState(wrapped)

            if (wrapped.batch.isPersisted()) {
                enqueue(flushCheckpointsTaskFactory.make())
            }

            if (wrapped.batch.state != Batch.State.COMPLETE) {
                log.info {
                    "Batch not complete: Starting process batch task for ${stream.descriptor}, batch $wrapped"
                }

                val task = processBatchTaskFactory.make(this, stream, wrapped)
                enqueue(task)
            } else if (streamManager.isBatchProcessingComplete()) {
                log.info {
                    "Batch $wrapped complete and batch processing complete: Starting close stream task for ${stream.descriptor}"
                }

                val task = closeStreamTaskFactory.make(this, stream)
                enqueue(task)
            } else {
                log.info {
                    "Batch $wrapped complete, but batch processing not complete: nothing else to do."
                }
            }
        }
    }

    /** Called when a stream is closed. */
    override suspend fun handleStreamClosed(stream: DestinationStream) {
        enqueue(teardownTaskFactory.make(this))
    }

    /** Called exactly once when all streams are closed. */
    override suspend fun handleTeardownComplete() {
        taskScopeProvider.close()
    }
}
