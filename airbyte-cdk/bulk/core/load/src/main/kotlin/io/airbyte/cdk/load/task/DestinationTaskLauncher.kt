/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.implementor.CloseStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.FailStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.FailSyncTaskFactory
import io.airbyte.cdk.load.task.implementor.OpenStreamTask
import io.airbyte.cdk.load.task.implementor.SetupTaskFactory
import io.airbyte.cdk.load.task.implementor.TeardownTaskFactory
import io.airbyte.cdk.load.task.internal.HeartbeatTask
import io.airbyte.cdk.load.task.internal.InputConsumerTask
import io.airbyte.cdk.load.task.internal.StatsEmitter
import io.airbyte.cdk.load.task.internal.UpdateBatchStateTaskFactory
import io.airbyte.cdk.load.task.internal.UpdateCheckpointsTask
import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.channels.Channel

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
@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "arguments are guaranteed to be non-null by Kotlin's type system"
)
class DestinationTaskLauncher(
    private val taskScopeProvider: TaskScopeProvider,
    private val catalog: DestinationCatalog,
    private val config: DestinationConfiguration,
    private val syncManager: SyncManager,

    // Internal Tasks
    private val inputConsumerTask: InputConsumerTask? = null,
    private val heartbeatTask: HeartbeatTask? = null,
    private val updateBatchTask: UpdateBatchStateTaskFactory,
    private val statsEmitter: StatsEmitter? = null,

    // Implementor Tasks
    private val setupTaskFactory: SetupTaskFactory,
    private val openStreamTask: OpenStreamTask,
    private val closeStreamTaskFactory: CloseStreamTaskFactory,
    private val teardownTaskFactory: TeardownTaskFactory,
    private val loadPipeline: LoadPipeline?,

    // Checkpoint Tasks
    private val updateCheckpointsTask: UpdateCheckpointsTask,

    // Exception handling
    private val failStreamTaskFactory: FailStreamTaskFactory,
    private val failSyncTaskFactory: FailSyncTaskFactory,

    // Async queues
    @Named("openStreamQueue") private val openStreamQueue: MessageQueue<DestinationStream>,
    @Named("defaultDestinationTaskLauncherHasThrown") private val hasThrown: AtomicBoolean,
) {
    init {
        if (loadPipeline == null) {
            throw IllegalStateException(
                "A legal sync requires a declared @Singleton of a type that implements LoadStrategy"
            )
        }
    }

    private val log = KotlinLogging.logger {}

    private val succeeded = Channel<Boolean>(Channel.UNLIMITED)

    private val teardownIsEnqueued = AtomicBoolean(false)
    private val failSyncIsEnqueued = AtomicBoolean(false)

    val closeStreamHasRun = ConcurrentHashMap<DestinationStream.Descriptor, AtomicBoolean>()

    inner class WrappedTask(
        private val innerTask: Task,
    ) : Task {
        override val terminalCondition: TerminalCondition = innerTask.terminalCondition

        override suspend fun execute() {
            try {
                innerTask.execute()
            } catch (e: CancellationException) {
                log.info { "Task $innerTask was cancelled." }
                throw e
            } catch (e: Exception) {
                log.error(e) { "Caught exception in task $innerTask" }
                if (hasThrown.setOnce()) {
                    handleException(e)
                } else {
                    log.info { "Skipping exception handling, because it has already run." }
                }
            } catch (t: Throwable) {
                log.error(t) { "Critical error in task $innerTask" }
                if (hasThrown.setOnce()) {
                    handleException(SystemErrorException(t.message, t))
                } else {
                    log.info { "Skipping exception handling, because it has already run." }
                }
            }
        }

        override fun toString(): String {
            return "TaskWrapper($innerTask)"
        }
    }

    private suspend fun launch(task: Task, withExceptionHandling: Boolean = true) {
        val wrapped = if (withExceptionHandling) WrappedTask(task) else task
        taskScopeProvider.launch(wrapped)
    }

    suspend fun run() {
        // Start the input consumer ASAP if/a
        inputConsumerTask?.let {
            log.info { "Starting input consumer task" }
            launch(it)
        }

        // Launch the client interface setup task
        log.info { "Starting startup task" }
        launch(setupTaskFactory.make(this))

        repeat(config.numOpenStreamWorkers) {
            log.info { "Launching open stream task $it" }
            launch(openStreamTask)
        }

        log.info { "Setting up load pipeline" }
        loadPipeline!!.start { launch(it) }
        log.info { "Launching update batch task" }
        launch(updateBatchTask.make(this))
        heartbeatTask?.let {
            log.info { "Launching heartbeat task" }
            launch(it)
        }

        statsEmitter?.let {
            log.info { "Launching Stats emtiter task" }
            launch(it)
        }

        log.info { "Starting checkpoint update task" }
        launch(updateCheckpointsTask)

        // Await completion
        val result = succeeded.receive()
        openStreamQueue.close()
        if (result) {
            taskScopeProvider.close()
        } else {
            taskScopeProvider.kill()
        }
    }

    suspend fun handleSetupComplete() {
        syncManager.markSetupComplete()
    }

    suspend fun handleStreamComplete(stream: DestinationStream.Descriptor) {
        log.info { "Processing complete for $stream" }
        if (closeStreamHasRun.getOrPut(stream) { AtomicBoolean(false) }.setOnce()) {
            if (syncManager.getStreamManager(stream).setClosed()) {
                log.info { "Batch processing complete: Starting close stream task for $stream" }
                val task = closeStreamTaskFactory.make(this, stream)
                launch(task)
            } else {
                log.warn {
                    "Close stream task was already initiated for $stream. This is probably undesired; skipping it."
                }
            }
        } else {
            log.info { "Close stream task has already run, skipping." }
        }
    }

    /** Called when a stream is closed. */
    suspend fun handleStreamClosed() {
        if (teardownIsEnqueued.setOnce()) {
            launch(teardownTaskFactory.make(this))
        } else {
            log.info { "Teardown task already enqueued, not enqueuing another one" }
        }
    }

    suspend fun handleException(e: Exception) {
        openStreamQueue.close()
        catalog.streams
            .map {
                val shouldRunStreamLoaderClose =
                    syncManager.getStreamManager(it.descriptor).setClosed()
                failStreamTaskFactory.make(
                    this,
                    e,
                    it.descriptor,
                    shouldRunStreamLoaderClose = shouldRunStreamLoaderClose,
                )
            }
            .forEach { launch(it, withExceptionHandling = false) }
    }

    suspend fun handleFailStreamComplete(e: Exception) {
        if (failSyncIsEnqueued.setOnce()) {
            launch(failSyncTaskFactory.make(this, e))
        } else {
            log.info { "Teardown task already enqueued, not enqueuing another one" }
        }
    }

    /** Called exactly once when all streams are closed. */
    suspend fun handleTeardownComplete(success: Boolean = true) {
        succeeded.send(success)
    }
}
