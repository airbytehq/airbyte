/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory.Companion.stream1
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.state.StreamManager
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.implementor.CloseStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.FailStreamTask
import io.airbyte.cdk.load.task.implementor.FailStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.FailSyncTaskFactory
import io.airbyte.cdk.load.task.implementor.OpenStreamTask
import io.airbyte.cdk.load.task.implementor.SetupTaskFactory
import io.airbyte.cdk.load.task.implementor.TeardownTaskFactory
import io.airbyte.cdk.load.task.internal.InputConsumerTask
import io.airbyte.cdk.load.task.internal.UpdateCheckpointsTask
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow

class DestinationTaskLauncherUTest {
    private val taskScopeProvider: TaskScopeProvider = mockk(relaxed = true)
    private val catalog: DestinationCatalog = mockk(relaxed = true)
    private val syncManager: SyncManager = mockk(relaxed = true)

    // Internal Tasks
    private val inputConsumerTask: InputConsumerTask = mockk(relaxed = true)

    // Implementor Tasks
    private val setupTaskFactory: SetupTaskFactory = mockk(relaxed = true)
    private val openStreamTask: OpenStreamTask = mockk(relaxed = true)
    private val closeStreamTaskFactory: CloseStreamTaskFactory = mockk(relaxed = true)
    private val teardownTaskFactory: TeardownTaskFactory = mockk(relaxed = true)

    // Checkpoint Tasks
    private val updateCheckpointsTask: UpdateCheckpointsTask = mockk(relaxed = true)
    private val config: DestinationConfiguration = mockk(relaxed = true)

    // Exception tasks
    private val failStreamTaskFactory: FailStreamTaskFactory = mockk(relaxed = true)
    private val failSyncTaskFactory: FailSyncTaskFactory = mockk(relaxed = true)

    // Queues
    private val openStreamQueue: MessageQueue<DestinationStream> = mockk(relaxed = true)
    private val batchUpdateQueue: ChannelMessageQueue<BatchUpdate> = mockk(relaxed = true)

    private val loadPipeline: LoadPipeline = mockk(relaxed = true)

    private fun getDefaultDestinationTaskLauncher(): DestinationTaskLauncher {
        return DestinationTaskLauncher(
            taskScopeProvider,
            catalog,
            config,
            syncManager,
            inputConsumerTask,
            heartbeatTask = mockk(relaxed = true),
            updateBatchTask = mockk(relaxed = true),
            statsEmitter = mockk(relaxed = true),
            setupTaskFactory,
            openStreamTask,
            closeStreamTaskFactory,
            teardownTaskFactory,
            loadPipeline,
            updateCheckpointsTask,
            failStreamTaskFactory,
            failSyncTaskFactory,
            openStreamQueue,
            hasThrown = AtomicBoolean(false),
        )
    }

    @BeforeEach
    fun init() {
        coEvery { taskScopeProvider.launch(any()) } coAnswers
            {
                val task = firstArg<Task>()
                task.execute()
            }

        val stream = mockk<DestinationStream>(relaxed = true)
        val streamDescriptor = DestinationStream.Descriptor("namespace", "name")
        every { stream.descriptor } returns streamDescriptor
        coEvery { catalog.streams } returns listOf(stream)
    }

    @Test
    fun `handle exception`() = runTest {
        val destinationTaskLauncher = getDefaultDestinationTaskLauncher()
        launch { destinationTaskLauncher.run() }
        val e = Exception("e")
        destinationTaskLauncher.handleException(e)
        destinationTaskLauncher.handleTeardownComplete()

        // mock stream manager always returns `false` from `setClosed()`, so we set
        // shouldRunStreamLoaderClose = false.
        coVerify { failStreamTaskFactory.make(any(), e, any(), shouldRunStreamLoaderClose = false) }
        coVerify { taskScopeProvider.launch(match { it is FailStreamTask }) }
    }

    @Test
    fun `run close stream no more than once per stream`() = runTest {
        val destinationTaskLauncher = getDefaultDestinationTaskLauncher()
        val streamManager = StreamManager(stream1)
        val stream1 = catalog.streams[0]
        every { syncManager.getStreamManager(any()) } returns streamManager
        destinationTaskLauncher.handleStreamComplete(stream1.descriptor)
        coVerify(exactly = 1) { closeStreamTaskFactory.make(any(), any()) }
    }

    @Test
    fun `successful completion triggers scope close`() = runTest {
        // This should close the scope provider.
        val taskLauncher = getDefaultDestinationTaskLauncher()
        launch {
            taskLauncher.run()
            coVerify { taskScopeProvider.close() }
        }
        taskLauncher.handleTeardownComplete()
    }

    @Test
    fun `completion with failure triggers scope kill`() = runTest {
        val taskLauncher = getDefaultDestinationTaskLauncher()
        launch {
            taskLauncher.run()
            coVerify { taskScopeProvider.kill() }
        }
        taskLauncher.handleTeardownComplete(success = false)
    }

    @Test
    fun `exceptions in tasks throw`() = runTest {
        coEvery { taskScopeProvider.launch(any()) } coAnswers
            {
                val task = firstArg<Task>()
                task.execute()
            }

        val taskLauncher = getDefaultDestinationTaskLauncher()
        coEvery { updateCheckpointsTask.execute() } throws Exception("oh no")
        val job = launch { taskLauncher.run() }
        taskLauncher.handleTeardownComplete()
        job.join()
        coVerify {
            failStreamTaskFactory.make(
                any(),
                any(),
                match { it.namespace == "namespace" && it.name == "name" },
                // mock stream manager always returns `false` from `setClosed()`, so we set
                // shouldRunStreamLoaderClose = false.
                shouldRunStreamLoaderClose = false,
            )
        }
    }

    @Test
    fun `numOpenStreamWorkers open stream tasks are launched`() = runTest {
        val numOpenStreamWorkers = 3
        val destinationTaskLauncher = getDefaultDestinationTaskLauncher()

        coEvery { config.numOpenStreamWorkers } returns numOpenStreamWorkers

        val job = launch { destinationTaskLauncher.run() }
        destinationTaskLauncher.handleTeardownComplete()
        job.join()

        coVerify(exactly = numOpenStreamWorkers) { openStreamTask.execute() }

        coVerify(exactly = 0) { openStreamQueue.publish(any()) }
    }

    @Test
    fun `don't start the load pipeline if not provided, do start old tasks`() = runTest {
        val launcher = getDefaultDestinationTaskLauncher()
        coEvery { config.numProcessRecordsWorkers } returns 1
        val job = assertDoesNotThrow { launch { launcher.run() } }
        launcher.handleTeardownComplete(true)
        job.join()
        job.cancel()
    }

    @Test
    fun `start the load pipeline if provided`() = runTest {
        val launcher = getDefaultDestinationTaskLauncher()
        val job = launch { launcher.run() }
        launcher.handleTeardownComplete(true)
        job.join()
        coVerify { loadPipeline.start(any()) }
        job.cancel()
    }

    @Test
    fun testRun() = runTest {
        val taskLauncher = getDefaultDestinationTaskLauncher()
        val job = launch { taskLauncher.run() }
        taskLauncher.handleTeardownComplete()
        job.join()

        coVerify(exactly = 1) { inputConsumerTask.execute() }
        coVerify(exactly = 1) { setupTaskFactory.make(any()) }
        coVerify(exactly = 1) { updateCheckpointsTask.execute() }

        job.cancel()
    }

    @Test
    fun testHandleStreamClosed() = runTest {
        val taskLauncher = getDefaultDestinationTaskLauncher()
        // This should run teardown unconditionally.
        taskLauncher.handleStreamClosed()
        coVerify(exactly = 1) { teardownTaskFactory.make(any()) }
    }

    @Test
    fun `test sync failure after stream failure`() = runTest {
        val taskLauncher = getDefaultDestinationTaskLauncher()
        val job = launch { taskLauncher.run() }
        taskLauncher.handleFailStreamComplete(Exception())
        taskLauncher.handleFailStreamComplete(Exception())
        taskLauncher.handleTeardownComplete()
        job.join()

        coVerify(exactly = 1) { failSyncTaskFactory.make(any(), any()) }
    }
}
