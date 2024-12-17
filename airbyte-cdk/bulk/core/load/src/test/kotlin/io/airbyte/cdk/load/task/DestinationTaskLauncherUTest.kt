/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationStreamEvent
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.implementor.CloseStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.FailStreamTask
import io.airbyte.cdk.load.task.implementor.FailStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.FailSyncTaskFactory
import io.airbyte.cdk.load.task.implementor.OpenStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.ProcessBatchTaskFactory
import io.airbyte.cdk.load.task.implementor.ProcessFileTask
import io.airbyte.cdk.load.task.implementor.ProcessFileTaskFactory
import io.airbyte.cdk.load.task.implementor.ProcessRecordsTaskFactory
import io.airbyte.cdk.load.task.implementor.SetupTaskFactory
import io.airbyte.cdk.load.task.implementor.TeardownTaskFactory
import io.airbyte.cdk.load.task.internal.FlushCheckpointsTaskFactory
import io.airbyte.cdk.load.task.internal.FlushTickTask
import io.airbyte.cdk.load.task.internal.InputConsumerTaskFactory
import io.airbyte.cdk.load.task.internal.SizedInputFlow
import io.airbyte.cdk.load.task.internal.SpillToDiskTask
import io.airbyte.cdk.load.task.internal.SpillToDiskTaskFactory
import io.airbyte.cdk.load.task.internal.TimedForcedCheckpointFlushTask
import io.airbyte.cdk.load.task.internal.UpdateCheckpointsTask
import io.mockk.Called
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class DestinationTaskLauncherUTest {
    private val taskScopeProvider: TaskScopeProvider<WrappedTask<ScopedTask>> =
        mockk(relaxed = true)
    private val catalog: DestinationCatalog = mockk(relaxed = true)
    private val syncManager: SyncManager = mockk(relaxed = true)

    // Internal Tasks
    private val inputConsumerTaskFactory: InputConsumerTaskFactory = mockk(relaxed = true)
    private val spillToDiskTaskFactory: SpillToDiskTaskFactory = mockk(relaxed = true)
    private val flushTickTask: FlushTickTask = mockk(relaxed = true)

    // Implementor Tasks
    private val setupTaskFactory: SetupTaskFactory = mockk(relaxed = true)
    private val openStreamTaskFactory: OpenStreamTaskFactory = mockk(relaxed = true)
    private val processRecordsTaskFactory: ProcessRecordsTaskFactory = mockk(relaxed = true)
    private val processFileTaskFactory: ProcessFileTaskFactory = mockk(relaxed = true)
    private val processBatchTaskFactory: ProcessBatchTaskFactory = mockk(relaxed = true)
    private val closeStreamTaskFactory: CloseStreamTaskFactory = mockk(relaxed = true)
    private val teardownTaskFactory: TeardownTaskFactory = mockk(relaxed = true)

    // Checkpoint Tasks
    private val flushCheckpointsTaskFactory: FlushCheckpointsTaskFactory = mockk(relaxed = true)
    private val timedFlushTask: TimedForcedCheckpointFlushTask = mockk(relaxed = true)
    private val updateCheckpointsTask: UpdateCheckpointsTask = mockk(relaxed = true)
    private val config: DestinationConfiguration = mockk(relaxed = true)

    // Exception tasks
    private val failStreamTaskFactory: FailStreamTaskFactory = mockk(relaxed = true)
    private val failSyncTaskFactory: FailSyncTaskFactory = mockk(relaxed = true)

    // Input Comsumer requirements
    private val inputFlow: SizedInputFlow<Reserved<DestinationMessage>> = mockk(relaxed = true)
    private val recordQueueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>> =
        mockk(relaxed = true)
    private val checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>> =
        mockk(relaxed = true)
    private fun getDefaultDestinationTaskLauncher(
        useFileTranfer: Boolean
    ): DefaultDestinationTaskLauncher {
        return DefaultDestinationTaskLauncher(
            taskScopeProvider,
            catalog,
            config,
            syncManager,
            inputConsumerTaskFactory,
            spillToDiskTaskFactory,
            flushTickTask,
            setupTaskFactory,
            openStreamTaskFactory,
            processRecordsTaskFactory,
            processFileTaskFactory,
            processBatchTaskFactory,
            closeStreamTaskFactory,
            teardownTaskFactory,
            flushCheckpointsTaskFactory,
            timedFlushTask,
            updateCheckpointsTask,
            failStreamTaskFactory,
            failSyncTaskFactory,
            useFileTranfer,
            inputFlow,
            recordQueueSupplier,
            checkpointQueue,
        )
    }

    @BeforeEach
    fun init() {
        coEvery { taskScopeProvider.launch(any()) } returns Unit

        val stream = mockk<DestinationStream>(relaxed = true)
        val streamDescriptor = DestinationStream.Descriptor("namespace", "name")
        every { stream.descriptor } returns streamDescriptor
        coEvery { catalog.streams } returns listOf(stream)
    }

    @Test
    fun `test that we don't start the spill-to-disk task when file transfer is enabled`() =
        runTest {
            val destinationTaskLauncher = getDefaultDestinationTaskLauncher(true)
            // This is needed to let the run method to complete
            destinationTaskLauncher.handleTeardownComplete()
            destinationTaskLauncher.run()

            coVerify { spillToDiskTaskFactory wasNot Called }
        }

    @Test
    fun `test that we start the spill-to-disk task when file transfer is disabled`() = runTest {
        val spillToDiskTask = mockk<SpillToDiskTask>(relaxed = true)
        coEvery { spillToDiskTaskFactory.make(any(), any()) } returns spillToDiskTask

        val destinationTaskLauncher = getDefaultDestinationTaskLauncher(false)
        // This is needed to let the run method to complete
        destinationTaskLauncher.handleTeardownComplete()
        destinationTaskLauncher.run()

        coVerify { spillToDiskTaskFactory.make(any(), any()) }
    }

    class MockedTaskWrapper(override val innerTask: ScopedTask) : WrappedTask<ScopedTask> {
        override suspend fun execute() {}
    }

    @Test
    fun `test handle file`() = runTest {
        val processFileTask = mockk<ProcessFileTask>(relaxed = true)
        every { processFileTaskFactory.make(any(), any(), any(), any()) } returns processFileTask

        val destinationTaskLauncher = getDefaultDestinationTaskLauncher(true)
        destinationTaskLauncher.handleFile(mockk(), mockk(), 1L)

        coVerify { taskScopeProvider.launch(match { it.innerTask is ProcessFileTask }) }
    }

    @Test
    fun `test handle exception`() = runTest {
        val destinationTaskLauncher = getDefaultDestinationTaskLauncher(true)
        launch { destinationTaskLauncher.run() }
        val e = Exception("e")
        destinationTaskLauncher.handleException(e)
        destinationTaskLauncher.handleTeardownComplete()

        coVerify { failStreamTaskFactory.make(any(), e, any()) }
        coVerify { taskScopeProvider.launch(match { it.innerTask is FailStreamTask }) }
    }
}
