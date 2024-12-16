/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationStreamEvent
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.implementor.CloseStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.FailStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.FailSyncTaskFactory
import io.airbyte.cdk.load.task.implementor.OpenStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.ProcessBatchTaskFactory
import io.airbyte.cdk.load.task.implementor.ProcessFileTaskFactory
import io.airbyte.cdk.load.task.implementor.ProcessRecordsTaskFactory
import io.airbyte.cdk.load.task.implementor.SetupTaskFactory
import io.airbyte.cdk.load.task.implementor.TeardownTaskFactory
import io.airbyte.cdk.load.task.internal.FlushCheckpointsTaskFactory
import io.airbyte.cdk.load.task.internal.FlushTickTask
import io.airbyte.cdk.load.task.internal.InputConsumerTaskFactory
import io.airbyte.cdk.load.task.internal.SizedInputFlow
import io.airbyte.cdk.load.task.internal.SpillToDiskTaskFactory
import io.airbyte.cdk.load.task.internal.TimedForcedCheckpointFlushTask
import io.airbyte.cdk.load.task.internal.UpdateCheckpointsTask
import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

interface DestinationTaskLauncher : TaskLauncher {
    suspend fun handleSetupComplete()
    suspend fun handleStreamStarted(stream: DestinationStream.Descriptor)
    suspend fun handleNewBatch(stream: DestinationStream.Descriptor, wrapped: BatchEnvelope<*>)
    suspend fun handleStreamClosed(stream: DestinationStream.Descriptor)
    suspend fun handleTeardownComplete(success: Boolean = true)
    suspend fun handleFile(stream: DestinationStream.Descriptor, file: DestinationFile, index: Long)

    suspend fun handleException(e: Exception)
    suspend fun handleFailStreamComplete(stream: DestinationStream.Descriptor, e: Exception)
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
    private val config: DestinationConfiguration,
    private val syncManager: SyncManager,

    // Internal Tasks
    private val inputConsumerTaskFactory: InputConsumerTaskFactory,
    private val spillToDiskTaskFactory: SpillToDiskTaskFactory,
    private val flushTickTask: FlushTickTask,

    // Implementor Tasks
    private val setupTaskFactory: SetupTaskFactory,
    private val openStreamTaskFactory: OpenStreamTaskFactory,
    private val processRecordsTaskFactory: ProcessRecordsTaskFactory,
    private val processFileTaskFactory: ProcessFileTaskFactory,
    private val processBatchTaskFactory: ProcessBatchTaskFactory,
    private val closeStreamTaskFactory: CloseStreamTaskFactory,
    private val teardownTaskFactory: TeardownTaskFactory,

    // Checkpoint Tasks
    private val flushCheckpointsTaskFactory: FlushCheckpointsTaskFactory,
    private val timedCheckpointFlushTask: TimedForcedCheckpointFlushTask,
    private val updateCheckpointsTask: UpdateCheckpointsTask,

    // Exception handling
    private val failStreamTaskFactory: FailStreamTaskFactory,
    private val failSyncTaskFactory: FailSyncTaskFactory,

    // File transfer
    @Value("\${airbyte.file-transfer.enabled}") private val fileTransferEnabled: Boolean,

    // Input Consumer requirements
    private val inputFlow: SizedInputFlow<Reserved<DestinationMessage>>,
    private val recordQueueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>,
    private val checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>,
) : DestinationTaskLauncher {
    private val log = KotlinLogging.logger {}

    private val batchUpdateLock = Mutex()
    private val succeeded = Channel<Boolean>(Channel.UNLIMITED)

    private val teardownIsEnqueued = AtomicBoolean(false)
    private val failSyncIsEnqueued = AtomicBoolean(false)

    inner class TaskWrapper(
        override val innerTask: ScopedTask,
    ) : WrappedTask<ScopedTask> {
        override suspend fun execute() {
            try {
                innerTask.execute()
            } catch (e: CancellationException) {
                log.info { "Task $innerTask was cancelled." }
                throw e
            } catch (e: Exception) {
                log.error { "Caught exception in task $innerTask: $e" }
                handleException(e)
            }
        }

        override fun toString(): String {
            return "TaskWrapper($innerTask)"
        }
    }

    inner class NoopWrapper(
        override val innerTask: ScopedTask,
    ) : WrappedTask<ScopedTask> {
        override suspend fun execute() {
            innerTask.execute()
        }
    }

    private suspend fun enqueue(task: ScopedTask, withExceptionHandling: Boolean = true) {
        val wrapped = if (withExceptionHandling) TaskWrapper(task) else NoopWrapper(task)
        taskScopeProvider.launch(wrapped)
    }

    override suspend fun run() {
        // Start the input consumer ASAP
        log.info { "Starting input consumer task" }
        val inputConsumerTask =
            inputConsumerTaskFactory.make(
                catalog = catalog,
                inputFlow = inputFlow,
                recordQueueSupplier = recordQueueSupplier,
                checkpointQueue = checkpointQueue,
                this,
            )
        enqueue(inputConsumerTask)

        // Launch the client interface setup task
        log.info { "Starting startup task" }
        val setupTask = setupTaskFactory.make(this)
        enqueue(setupTask)

        if (!fileTransferEnabled) {
            // Start a spill-to-disk task for each record stream
            catalog.streams.forEach { stream ->
                log.info { "Starting spill-to-disk task for $stream" }
                val spillTask = spillToDiskTaskFactory.make(this, stream.descriptor)
                enqueue(spillTask)
            }

            repeat(config.numProcessRecordsWorkers) {
                log.info { "Launching process records task $it" }
                val task = processRecordsTaskFactory.make(this)
                enqueue(task)
            }

            repeat(config.numProcessBatchWorkers) {
                log.info { "Launching process batch task $it" }
                val task = processBatchTaskFactory.make(this)
                enqueue(task)
            }
        }

        // Start flush task
        log.info { "Starting timed file aggregate flush task " }
        enqueue(flushTickTask)

        // Start the checkpoint management tasks
        log.info { "Starting timed checkpoint flush task" }
        enqueue(timedCheckpointFlushTask)

        log.info { "Starting checkpoint update task" }
        enqueue(updateCheckpointsTask)

        // Await completion
        if (succeeded.receive()) {
            taskScopeProvider.close()
        } else {
            taskScopeProvider.kill()
        }
    }

    /** Called when the initial destination setup completes. */
    override suspend fun handleSetupComplete() {
        catalog.streams.forEach {
            log.info { "Starting open stream task for $it" }
            val task = openStreamTaskFactory.make(this, it)
            enqueue(task)
        }
    }

    /** Called when a stream is ready for loading. */
    override suspend fun handleStreamStarted(stream: DestinationStream.Descriptor) {
        // Nothing to do because the SpillToDiskTask will trigger the next calls
        log.info { "Stream $stream successfully opened for writing." }
    }

    /**
     * Called for each new batch. Enqueues processing for any incomplete batch, and enqueues closing
     * the stream if all batches are complete.
     */
    override suspend fun handleNewBatch(
        stream: DestinationStream.Descriptor,
        wrapped: BatchEnvelope<*>
    ) {
        batchUpdateLock.withLock {
            val streamManager = syncManager.getStreamManager(stream)
            streamManager.updateBatchState(wrapped)

            if (wrapped.batch.isPersisted()) {
                log.info {
                    "Batch $wrapped is persisted: Starting flush checkpoints task for $stream"
                }
                enqueue(flushCheckpointsTaskFactory.make())
            }

            if (streamManager.isBatchProcessingComplete()) {
                log.info {
                    "Batch $wrapped complete and batch processing complete: Starting close stream task for $stream"
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
    override suspend fun handleStreamClosed(stream: DestinationStream.Descriptor) {
        if (teardownIsEnqueued.setOnce()) {
            enqueue(teardownTaskFactory.make(this))
        } else {
            log.info { "Teardown task already enqueued, not enqueuing another one" }
        }
    }

    override suspend fun handleFile(
        stream: DestinationStream.Descriptor,
        file: DestinationFile,
        index: Long
    ) {
        enqueue(processFileTaskFactory.make(this, stream, file, index))
    }

    override suspend fun handleException(e: Exception) {
        catalog.streams
            .map { failStreamTaskFactory.make(this, e, it.descriptor) }
            .forEach { enqueue(it, withExceptionHandling = false) }
    }

    override suspend fun handleFailStreamComplete(
        stream: DestinationStream.Descriptor,
        e: Exception
    ) {
        if (failSyncIsEnqueued.setOnce()) {
            enqueue(failSyncTaskFactory.make(this, e))
        } else {
            log.info { "Teardown task already enqueued, not enqueuing another one" }
        }
    }

    /** Called exactly once when all streams are closed. */
    override suspend fun handleTeardownComplete(success: Boolean) {
        succeeded.send(success)
    }
}
