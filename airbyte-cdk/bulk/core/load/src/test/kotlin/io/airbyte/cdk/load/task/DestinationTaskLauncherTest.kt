/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import com.google.common.collect.Range
import com.google.common.collect.TreeRangeSet
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.file.DefaultLocalFile
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.implementor.CloseStreamTask
import io.airbyte.cdk.load.task.implementor.CloseStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.DefaultCloseStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.DefaultOpenStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.DefaultProcessBatchTaskFactory
import io.airbyte.cdk.load.task.implementor.DefaultProcessRecordsTaskFactory
import io.airbyte.cdk.load.task.implementor.DefaultSetupTaskFactory
import io.airbyte.cdk.load.task.implementor.DefaultTeardownTaskFactory
import io.airbyte.cdk.load.task.implementor.OpenStreamTask
import io.airbyte.cdk.load.task.implementor.OpenStreamTaskFactory
import io.airbyte.cdk.load.task.implementor.ProcessBatchTask
import io.airbyte.cdk.load.task.implementor.ProcessBatchTaskFactory
import io.airbyte.cdk.load.task.implementor.ProcessRecordsTask
import io.airbyte.cdk.load.task.implementor.ProcessRecordsTaskFactory
import io.airbyte.cdk.load.task.implementor.SetupTask
import io.airbyte.cdk.load.task.implementor.SetupTaskFactory
import io.airbyte.cdk.load.task.implementor.TeardownTask
import io.airbyte.cdk.load.task.implementor.TeardownTaskFactory
import io.airbyte.cdk.load.task.internal.DefaultSpillToDiskTaskFactory
import io.airbyte.cdk.load.task.internal.FlushCheckpointsTask
import io.airbyte.cdk.load.task.internal.FlushCheckpointsTaskFactory
import io.airbyte.cdk.load.task.internal.InputConsumerTask
import io.airbyte.cdk.load.task.internal.SpillToDiskTask
import io.airbyte.cdk.load.task.internal.SpillToDiskTaskFactory
import io.airbyte.cdk.load.task.internal.SpilledRawMessagesLocalFile
import io.airbyte.cdk.load.task.internal.TimedForcedCheckpointFlushTask
import io.airbyte.cdk.load.task.internal.UpdateCheckpointsTask
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import kotlin.io.path.Path
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.channels.toList
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
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
class DestinationTaskLauncherTest<T> where T : LeveledTask, T : ScopedTask {
    @Inject lateinit var mockScopeProvider: MockScopeProvider
    @Inject lateinit var taskLauncher: DestinationTaskLauncher
    @Inject lateinit var syncManager: SyncManager
    @Inject lateinit var mockExceptionHandler: MockExceptionHandler<T>

    @Inject lateinit var mockInputConsumerTask: MockInputConsumerTask
    @Inject lateinit var mockSetupTaskFactory: MockSetupTaskFactory
    @Inject lateinit var mockSpillToDiskTaskFactory: MockSpillToDiskTaskFactory
    @Inject lateinit var mockOpenStreamTaskFactory: MockOpenStreamTaskFactory
    @Inject lateinit var processRecordsTaskFactory: MockProcessRecordsTaskFactory
    @Inject lateinit var processBatchTaskFactory: MockProcessBatchTaskFactory
    @Inject lateinit var closeStreamTaskFactory: MockCloseStreamTaskFactory
    @Inject lateinit var teardownTaskFactory: MockTeardownTaskFactory
    @Inject lateinit var flushCheckpointsTaskFactory: MockFlushCheckpointsTaskFactory
    @Inject lateinit var mockForceFlushTask: MockForceFlushTask
    @Inject lateinit var updateCheckpointsTask: MockUpdateCheckpointsTask

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockInputConsumerTask : InputConsumerTask {
        val hasRun: Channel<Boolean> = Channel(Channel.UNLIMITED)

        override suspend fun execute() {
            hasRun.send(true)
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

        init {
            catalog.streams.forEach { streamHasRun[it.descriptor] = Channel(Channel.UNLIMITED) }
        }

        override fun make(
            taskLauncher: DestinationTaskLauncher,
            stream: DestinationStream
        ): SpillToDiskTask {
            return object : SpillToDiskTask {
                override val stream: DestinationStream = stream
                override suspend fun execute() {
                    streamHasRun[stream.descriptor]?.send(Unit)
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
                override val stream: DestinationStream = stream
                override suspend fun execute() {
                    streamHasRun[stream]?.send(Unit)
                }
            }
        }
    }

    @Singleton
    @Replaces(DefaultProcessRecordsTaskFactory::class)
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockProcessRecordsTaskFactory : ProcessRecordsTaskFactory {
        val hasRun: Channel<Unit> = Channel(Channel.UNLIMITED)

        override fun make(
            taskLauncher: DestinationTaskLauncher,
            stream: DestinationStream,
            file: SpilledRawMessagesLocalFile
        ): ProcessRecordsTask {
            return object : ProcessRecordsTask {
                override val stream: DestinationStream = stream
                override suspend fun execute() {
                    hasRun.send(Unit)
                }
            }
        }
    }

    @Singleton
    @Replaces(DefaultProcessBatchTaskFactory::class)
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockProcessBatchTaskFactory : ProcessBatchTaskFactory {
        val hasRun: Channel<BatchEnvelope<*>> = Channel(Channel.UNLIMITED)

        override fun make(
            taskLauncher: DestinationTaskLauncher,
            stream: DestinationStream,
            batchEnvelope: BatchEnvelope<*>
        ): ProcessBatchTask {
            return object : ProcessBatchTask {
                override val stream: DestinationStream = stream
                override suspend fun execute() {
                    hasRun.send(batchEnvelope)
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
            stream: DestinationStream,
        ): CloseStreamTask {
            return object : CloseStreamTask {
                override val stream: DestinationStream = stream
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

    class MockBatch(override val state: Batch.State) : Batch

    @Singleton
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockExceptionHandler<T> : TaskExceptionHandler<T, WrappedTask<ScopedTask>> where
    T : LeveledTask,
    T : ScopedTask {
        val wrappedTasks = Channel<LeveledTask>(Channel.UNLIMITED)
        val callbacks = Channel<suspend () -> Unit>(Channel.UNLIMITED)

        inner class IdentityWrapper(override val innerTask: ScopedTask) : WrappedTask<ScopedTask> {
            override suspend fun execute() {
                innerTask.execute()
            }
        }

        override suspend fun withExceptionHandling(task: T): WrappedTask<ScopedTask> {
            runBlocking { wrappedTasks.send(task) }
            val innerTask =
                object : InternalScope {
                    override suspend fun execute() {
                        task.execute()
                    }
                }
            return IdentityWrapper(innerTask)
        }

        override suspend fun setCallback(callback: suspend () -> Unit) {
            callbacks.send(callback)
        }
    }

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

        // Verify that we kicked off the timed force flush w/o a specific delay
        Assertions.assertTrue(mockForceFlushTask.didRun.receive())

        Assertions.assertTrue(
            updateCheckpointsTask.didRun.receive(),
            "update checkpoints task was started"
        )

        // Collect the tasks wrapped by the exception handler: expect one Setup and [nStreams]
        // SpillToDisk
        mockExceptionHandler.wrappedTasks.close()
        val taskList = mockExceptionHandler.wrappedTasks.toList()
        Assertions.assertEquals(1, taskList.filterIsInstance<SetupTask>().size)
        Assertions.assertEquals(
            mockSpillToDiskTaskFactory.streamHasRun.size,
            taskList.filterIsInstance<SpillToDiskTask>().size
        )
        job.cancel()
    }

    @Test
    fun testHandleSetupComplete() = runTest {
        // Verify that open stream ran for each stream
        taskLauncher.handleSetupComplete()
        mockOpenStreamTaskFactory.streamHasRun.values.forEach { it.receive() }

        // Collect the tasks wrapped by the exception handler: expect [nStreams] OpenStream
        mockExceptionHandler.wrappedTasks.close()
        val taskList = mockExceptionHandler.wrappedTasks.toList()
        Assertions.assertEquals(
            mockOpenStreamTaskFactory.streamHasRun.size,
            taskList.filterIsInstance<OpenStreamTask>().size
        )
    }

    @Test
    fun testHandleSpilledFileCompleteNotEndOfStream() = runTest {
        taskLauncher.handleNewSpilledFile(
            MockDestinationCatalogFactory.stream1,
            SpilledRawMessagesLocalFile(
                DefaultLocalFile(Path("not/a/real/file")),
                100L,
                Range.singleton(0)
            )
        )

        processRecordsTaskFactory.hasRun.receive()
        mockSpillToDiskTaskFactory.streamHasRun[MockDestinationCatalogFactory.stream1.descriptor]
            ?.receive()
            ?: Assertions.fail("SpillToDiskTask not run")
    }

    @Test
    fun testHandleSpilledFileCompleteEndOfStream() = runTest {
        launch {
            taskLauncher.handleNewSpilledFile(
                MockDestinationCatalogFactory.stream1,
                SpilledRawMessagesLocalFile(
                    DefaultLocalFile(Path("not/a/real/file")),
                    100L,
                    Range.singleton(0),
                    true
                )
            )
        }

        processRecordsTaskFactory.hasRun.receive()
        delay(500)
        Assertions.assertTrue(
            mockSpillToDiskTaskFactory.streamHasRun[
                    MockDestinationCatalogFactory.stream1.descriptor]
                ?.tryReceive()
                ?.isFailure != false
        )
    }

    @Test
    fun testHandleNewBatch() = runTest {
        val range = TreeRangeSet.create(listOf(Range.closed(0L, 100L)))
        val streamManager =
            syncManager.getStreamManager(MockDestinationCatalogFactory.stream1.descriptor)
        repeat(100) { streamManager.countRecordIn() }

        streamManager.markEndOfStream()

        // Verify incomplete batch triggers process batch
        val incompleteBatch = BatchEnvelope(MockBatch(Batch.State.LOCAL), range)
        taskLauncher.handleNewBatch(MockDestinationCatalogFactory.stream1, incompleteBatch)
        Assertions.assertFalse(streamManager.areRecordsPersistedUntil(100L))

        val batchReceived = processBatchTaskFactory.hasRun.receive()
        Assertions.assertEquals(incompleteBatch, batchReceived)
        delay(500)
        Assertions.assertTrue(flushCheckpointsTaskFactory.hasRun.tryReceive().isFailure)

        val persistedBatch = BatchEnvelope(MockBatch(Batch.State.PERSISTED), range)
        taskLauncher.handleNewBatch(MockDestinationCatalogFactory.stream1, persistedBatch)
        Assertions.assertTrue(streamManager.areRecordsPersistedUntil(100L))
        Assertions.assertTrue(flushCheckpointsTaskFactory.hasRun.receive())

        // Verify complete batch w/o batch processing complete does nothing
        val halfRange = TreeRangeSet.create(listOf(Range.closed(0L, 50L)))
        val completeBatchHalf = BatchEnvelope(MockBatch(Batch.State.COMPLETE), halfRange)
        taskLauncher.handleNewBatch(MockDestinationCatalogFactory.stream1, completeBatchHalf)
        delay(1000)
        Assertions.assertTrue(closeStreamTaskFactory.hasRun.tryReceive().isFailure)

        // Verify complete batch w/ batch processing complete triggers close stream
        val secondHalf = TreeRangeSet.create(listOf(Range.closed(51L, 100L)))
        val completingBatch = BatchEnvelope(MockBatch(Batch.State.COMPLETE), secondHalf)
        taskLauncher.handleNewBatch(MockDestinationCatalogFactory.stream1, completingBatch)
        closeStreamTaskFactory.hasRun.receive()
        Assertions.assertTrue(true)
    }

    @Test
    fun testHandleStreamClosed() = runTest {
        // This should run teardown unconditionally.
        launch { taskLauncher.handleStreamClosed(MockDestinationCatalogFactory.stream1) }
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
        mockExceptionHandler.callbacks.receive().invoke()
    }
}
