/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import com.google.common.collect.Range
import com.google.common.collect.TreeRangeSet
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.command.MockDestinationConfiguration
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationStreamEvent
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.implementor.CloseStreamTask
import io.airbyte.cdk.load.task.implementor.CloseStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.DefaultCloseStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.DefaultOpenStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.DefaultSetupTaskFactory
import io.airbyte.cdk.load.task.implementor.DefaultTeardownTaskFactory
import io.airbyte.cdk.load.task.implementor.FailStreamTask
import io.airbyte.cdk.load.task.implementor.FailStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.FailSyncTask
import io.airbyte.cdk.load.task.implementor.FailSyncTaskFactory
import io.airbyte.cdk.load.task.implementor.OpenStreamTask
import io.airbyte.cdk.load.task.implementor.OpenStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.ProcessBatchTaskFactory
import io.airbyte.cdk.load.task.implementor.ProcessRecordsTaskFactory
import io.airbyte.cdk.load.task.implementor.SetupTask
import io.airbyte.cdk.load.task.implementor.SetupTaskFactory
import io.airbyte.cdk.load.task.implementor.TeardownTask
import io.airbyte.cdk.load.task.implementor.TeardownTaskFactory
import io.airbyte.cdk.load.task.internal.DefaultSpillToDiskTaskFactory
import io.airbyte.cdk.load.task.internal.FlushCheckpointsTask
import io.airbyte.cdk.load.task.internal.FlushCheckpointsTaskFactory
import io.airbyte.cdk.load.task.internal.FlushTickTask
import io.airbyte.cdk.load.task.internal.InputConsumerTask
import io.airbyte.cdk.load.task.internal.InputConsumerTaskFactory
import io.airbyte.cdk.load.task.internal.SizedInputFlow
import io.airbyte.cdk.load.task.internal.SpillToDiskTask
import io.airbyte.cdk.load.task.internal.SpillToDiskTaskFactory
import io.airbyte.cdk.load.task.internal.TimedForcedCheckpointFlushTask
import io.airbyte.cdk.load.task.internal.UpdateCheckpointsTask
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import io.mockk.coVerify
import io.mockk.mockk
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.channels.toList
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.FlowCollector
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(
    rebuildContext = true,
    environments =
        [
            "DestinationTaskLauncherTest",
            "MockDestinationConfiguration",
            "MockDestinationCatalog",
            "MockScopeProvider",
        ]
)
class DestinationTaskLauncherTest<T : ScopedTask> {
    @Inject lateinit var mockScopeProvider: MockScopeProvider
    @Inject lateinit var taskLauncher: DestinationTaskLauncher
    @Inject lateinit var syncManager: SyncManager

    @Inject lateinit var mockInputConsumerTask: MockInputConsumerTaskFactory
    @Inject lateinit var mockSetupTaskFactory: MockSetupTaskFactory
    @Inject lateinit var mockSpillToDiskTaskFactory: MockSpillToDiskTaskFactory
    @Inject lateinit var mockOpenStreamTaskFactory: MockOpenStreamTaskFactory
    @Inject lateinit var processRecordsTaskFactory: ProcessRecordsTaskFactory
    @Inject lateinit var processBatchTaskFactory: ProcessBatchTaskFactory
    @Inject lateinit var closeStreamTaskFactory: MockCloseStreamTaskFactory
    @Inject lateinit var teardownTaskFactory: MockTeardownTaskFactory
    @Inject lateinit var flushCheckpointsTaskFactory: MockFlushCheckpointsTaskFactory
    @Inject lateinit var mockForceFlushTask: MockForceFlushTask
    @Inject lateinit var updateCheckpointsTask: MockUpdateCheckpointsTask
    @Inject lateinit var inputFlow: MockInputFlow
    @Inject lateinit var queueWriter: MockQueueWriter
    @Inject lateinit var messageQueueSupplier: MockMessageQueueSupplier
    @Inject lateinit var flushTickTask: FlushTickTask
    @Inject lateinit var mockFailStreamTaskFactory: MockFailStreamTaskFactory
    @Inject lateinit var mockFailSyncTaskFactory: MockFailSyncTaskFactory
    @Inject lateinit var config: MockDestinationConfiguration

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    fun flushTickTask(): FlushTickTask = mockk(relaxed = true)

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    fun processRecordsTaskFactory(): ProcessRecordsTaskFactory = mockk(relaxed = true)

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    fun processBatchTaskFactory(): ProcessBatchTaskFactory = mockk(relaxed = true)

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockInputFlow : SizedInputFlow<Reserved<DestinationMessage>> {
        override suspend fun collect(
            collector: FlowCollector<Pair<Long, Reserved<DestinationMessage>>>
        ) {}
    }

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockQueueWriter : QueueWriter<Reserved<CheckpointMessageWrapped>> {
        override suspend fun publish(message: Reserved<CheckpointMessageWrapped>) {}
        override fun isClosedForPublish(): Boolean = false
        override suspend fun close() {}
    }

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockMessageQueueSupplier :
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>> {
        override fun get(
            key: DestinationStream.Descriptor
        ): MessageQueue<Reserved<DestinationStreamEvent>> {
            return mockk()
        }
    }

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockInputConsumerTaskFactory : InputConsumerTaskFactory {
        val hasRun: Channel<Boolean> = Channel(Channel.UNLIMITED)

        override fun make(
            catalog: DestinationCatalog,
            inputFlow: SizedInputFlow<Reserved<DestinationMessage>>,
            recordQueueSupplier:
                MessageQueueSupplier<
                    DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>,
            checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>,
            destinationTaskLauncher: DestinationTaskLauncher
        ): InputConsumerTask {
            return object : InputConsumerTask {
                override suspend fun execute() {
                    hasRun.send(true)
                }
            }
        }
    }

    @Singleton
    @Replaces(DefaultSetupTaskFactory::class)
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockSetupTaskFactory : SetupTaskFactory {
        val hasRun: Channel<Unit> = Channel(Channel.UNLIMITED)

        override fun make(
            taskLauncher: DestinationTaskLauncher,
        ): SetupTask {
            return object : SetupTask {
                override suspend fun execute() {
                    hasRun.send(Unit)
                }
            }
        }
    }

    @Singleton
    @Replaces(DefaultSpillToDiskTaskFactory::class)
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockSpillToDiskTaskFactory(catalog: DestinationCatalog) : SpillToDiskTaskFactory {
        val streamHasRun = mutableMapOf<DestinationStream.Descriptor, Channel<Unit>>()
        val forceFailure = AtomicBoolean(false)

        init {
            catalog.streams.forEach { streamHasRun[it.descriptor] = Channel(Channel.UNLIMITED) }
        }

        override fun make(
            taskLauncher: DestinationTaskLauncher,
            stream: DestinationStream.Descriptor
        ): SpillToDiskTask {
            return object : SpillToDiskTask {
                override suspend fun execute() {
                    if (forceFailure.get()) {
                        throw Exception("Forced failure")
                    }
                    streamHasRun[stream]?.send(Unit)
                }
            }
        }
    }

    @Singleton
    @Replaces(DefaultOpenStreamTaskFactory::class)
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockOpenStreamTaskFactory(catalog: DestinationCatalog) : OpenStreamTaskFactory {
        val streamHasRun = mutableMapOf<DestinationStream, Channel<Unit>>()

        init {
            catalog.streams.forEach { streamHasRun[it] = Channel(Channel.UNLIMITED) }
        }

        override fun make(
            taskLauncher: DestinationTaskLauncher,
            stream: DestinationStream
        ): OpenStreamTask {
            return object : OpenStreamTask {
                override suspend fun execute() {
                    streamHasRun[stream]?.send(Unit)
                }
            }
        }
    }

    @Singleton
    @Replaces(DefaultCloseStreamTaskFactory::class)
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockCloseStreamTaskFactory : CloseStreamTaskFactory {
        val hasRun: Channel<Unit> = Channel(Channel.UNLIMITED)

        override fun make(
            taskLauncher: DestinationTaskLauncher,
            stream: DestinationStream.Descriptor,
        ): CloseStreamTask {
            return object : CloseStreamTask {
                override suspend fun execute() {
                    hasRun.send(Unit)
                }
            }
        }
    }

    @Singleton
    @Replaces(DefaultTeardownTaskFactory::class)
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockTeardownTaskFactory : TeardownTaskFactory {
        val hasRun: Channel<Unit> = Channel(Channel.UNLIMITED)

        override fun make(taskLauncher: DestinationTaskLauncher): TeardownTask {
            return object : TeardownTask {
                override suspend fun execute() {
                    hasRun.send(Unit)
                }
            }
        }
    }

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockFlushCheckpointsTaskFactory : FlushCheckpointsTaskFactory {
        val hasRun: Channel<Boolean> = Channel(Channel.UNLIMITED)

        override fun make(): FlushCheckpointsTask {
            return object : FlushCheckpointsTask {
                override suspend fun execute() {
                    hasRun.send(true)
                }
            }
        }
    }

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockForceFlushTask : TimedForcedCheckpointFlushTask {
        val didRun = Channel<Boolean>(Channel.UNLIMITED)

        override suspend fun execute() {
            didRun.send(true)
        }
    }

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockUpdateCheckpointsTask : UpdateCheckpointsTask {
        val didRun = Channel<Boolean>(Channel.UNLIMITED)
        override suspend fun execute() {
            didRun.send(true)
        }
    }

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockFailStreamTaskFactory : FailStreamTaskFactory {
        val didRunFor = Channel<DestinationStream.Descriptor>(Channel.UNLIMITED)
        override fun make(
            taskLauncher: DestinationTaskLauncher,
            exception: Exception,
            stream: DestinationStream.Descriptor
        ): FailStreamTask {
            return object : FailStreamTask {
                override suspend fun execute() {
                    didRunFor.send(stream)
                }
            }
        }
    }

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockFailSyncTaskFactory : FailSyncTaskFactory {
        val didRun = Channel<Boolean>(Channel.UNLIMITED)
        override fun make(
            taskLauncher: DestinationTaskLauncher,
            exception: Exception
        ): FailSyncTask {
            return object : FailSyncTask {
                override suspend fun execute() {
                    didRun.send(true)
                }
            }
        }
    }

    class MockBatch(override val state: Batch.State, override val groupId: String? = null) : Batch

    @Test
    fun testRun() = runTest {
        val job = launch { taskLauncher.run() }

        Assertions.assertTrue(
            mockInputConsumerTask.hasRun.receive(),
            "input consumer task was started"
        )

        // Verify that setup has run
        mockSetupTaskFactory.hasRun.receive()

        // Verify that spill to disk ran for each stream
        mockSpillToDiskTaskFactory.streamHasRun.values.forEach { it.receive() }

        coVerify(exactly = config.numProcessRecordsWorkers) {
            processRecordsTaskFactory.make(any())
        }

        coVerify(exactly = config.numProcessBatchWorkers) { processBatchTaskFactory.make(any()) }

        // Verify that we kicked off the timed force flush w/o a specific delay
        Assertions.assertTrue(mockForceFlushTask.didRun.receive())

        Assertions.assertTrue(
            updateCheckpointsTask.didRun.receive(),
            "update checkpoints task was started"
        )

        job.cancel()
    }

    @Test
    fun testHandleSetupComplete() = runTest {
        // Verify that open stream ran for each stream
        taskLauncher.handleSetupComplete()
        mockOpenStreamTaskFactory.streamHasRun.values.forEach { it.receive() }
    }

    @Test
    fun testHandleNewBatch() = runTest {
        val range = TreeRangeSet.create(listOf(Range.closed(0L, 100L)))
        val stream1 = MockDestinationCatalogFactory.stream1
        val streamManager = syncManager.getStreamManager(stream1.descriptor)
        repeat(100) { streamManager.countRecordIn() }

        streamManager.markEndOfStream(true)

        // Verify incomplete batch triggers process batch
        val incompleteBatch = BatchEnvelope(MockBatch(Batch.State.LOCAL), range, stream1.descriptor)
        taskLauncher.handleNewBatch(
            MockDestinationCatalogFactory.stream1.descriptor,
            incompleteBatch
        )
        Assertions.assertFalse(streamManager.areRecordsPersistedUntil(100L))

        delay(500)
        Assertions.assertTrue(flushCheckpointsTaskFactory.hasRun.tryReceive().isFailure)

        val persistedBatch =
            BatchEnvelope(MockBatch(Batch.State.PERSISTED), range, stream1.descriptor)
        taskLauncher.handleNewBatch(
            MockDestinationCatalogFactory.stream1.descriptor,
            persistedBatch
        )
        Assertions.assertTrue(streamManager.areRecordsPersistedUntil(100L))
        Assertions.assertTrue(flushCheckpointsTaskFactory.hasRun.receive())

        // Verify complete batch w/o batch processing complete does nothing
        val halfRange = TreeRangeSet.create(listOf(Range.closed(0L, 50L)))
        val completeBatchHalf =
            BatchEnvelope(MockBatch(Batch.State.COMPLETE), halfRange, stream1.descriptor)
        taskLauncher.handleNewBatch(
            MockDestinationCatalogFactory.stream1.descriptor,
            completeBatchHalf
        )
        delay(1000)
        Assertions.assertTrue(closeStreamTaskFactory.hasRun.tryReceive().isFailure)

        // Verify complete batch w/ batch processing complete triggers close stream
        val secondHalf = TreeRangeSet.create(listOf(Range.closed(51L, 100L)))
        val completingBatch =
            BatchEnvelope(MockBatch(Batch.State.COMPLETE), secondHalf, stream1.descriptor)
        taskLauncher.handleNewBatch(
            MockDestinationCatalogFactory.stream1.descriptor,
            completingBatch
        )
        closeStreamTaskFactory.hasRun.receive()
        Assertions.assertTrue(true)
    }

    @Test
    fun handleEmptyBatch() = runTest {
        val range = TreeRangeSet.create(listOf(Range.closed(0L, 0L)))
        val stream1 = MockDestinationCatalogFactory.stream1
        val streamManager = syncManager.getStreamManager(stream1.descriptor)
        streamManager.markEndOfStream(true)

        val emptyBatch = BatchEnvelope(MockBatch(Batch.State.COMPLETE), range, stream1.descriptor)
        taskLauncher.handleNewBatch(MockDestinationCatalogFactory.stream1.descriptor, emptyBatch)
        closeStreamTaskFactory.hasRun.receive()
    }

    @Test
    fun testHandleStreamClosed() = runTest {
        // This should run teardown unconditionally.
        launch { taskLauncher.handleStreamClosed(MockDestinationCatalogFactory.stream1.descriptor) }
        teardownTaskFactory.hasRun.receive()
    }

    @Test
    fun testHandleTeardownComplete() = runTest {
        // This should close the scope provider.
        launch {
            taskLauncher.run()
            Assertions.assertTrue(mockScopeProvider.didClose)
        }
        taskLauncher.handleTeardownComplete()
    }

    @Test
    fun testHandleCallbackWithFailure() = runTest {
        launch {
            taskLauncher.run()
            Assertions.assertTrue(mockScopeProvider.didKill)
        }
        taskLauncher.handleTeardownComplete(success = false)
    }

    @Test
    fun `test exceptions in tasks throw`(catalog: DestinationCatalog) = runTest {
        mockSpillToDiskTaskFactory.forceFailure.getAndSet(true)

        val job = launch { taskLauncher.run() }
        taskLauncher.handleTeardownComplete()
        job.join()

        mockFailStreamTaskFactory.didRunFor.close()

        Assertions.assertEquals(
            catalog.streams.map { it.descriptor }.toSet(),
            mockFailStreamTaskFactory.didRunFor.toList().toSet(),
            "FailStreamTask was run for each stream"
        )
    }

    @Test
    fun `test sync failure after stream failure`() = runTest {
        val job = launch { taskLauncher.run() }
        taskLauncher.handleFailStreamComplete(
            MockDestinationCatalogFactory.stream1.descriptor,
            Exception()
        )
        taskLauncher.handleFailStreamComplete(
            MockDestinationCatalogFactory.stream2.descriptor,
            Exception()
        )
        taskLauncher.handleTeardownComplete()
        job.join()
        mockFailSyncTaskFactory.didRun.close()
        val runs = mockFailSyncTaskFactory.didRun.toList()
        Assertions.assertTrue(runs.all { it }, "FailSyncTask was run")
        Assertions.assertTrue(runs.size == 1, "FailSyncTask was run exactly once")
    }
}
