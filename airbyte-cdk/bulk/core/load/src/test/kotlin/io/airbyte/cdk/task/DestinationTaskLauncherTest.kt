/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import com.google.common.collect.Range
import com.google.common.collect.TreeRangeSet
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.MockDestinationCatalogFactory.Companion.stream1
import io.airbyte.cdk.file.DefaultLocalFile
import io.airbyte.cdk.message.Batch
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.SpilledRawMessagesLocalFile
import io.airbyte.cdk.state.MockStreamManager
import io.airbyte.cdk.state.MockSyncManager
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicLong
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
            "MockDestinationCatalog",
            "MockSyncManager",
        ]
)
class DestinationTaskLauncherTest {
    @Inject lateinit var taskRunner: TaskRunner
    @Inject lateinit var taskLauncher: DestinationTaskLauncher
    @Inject lateinit var syncManager: MockSyncManager
    @Inject lateinit var mockExceptionHandler: MockExceptionHandler

    @Inject lateinit var mockSetupTaskFactory: MockSetupTaskFactory
    @Inject lateinit var mockSpillToDiskTaskFactory: MockSpillToDiskTaskFactory
    @Inject lateinit var mockOpenStreamTaskFactory: MockOpenStreamTaskFactory
    @Inject lateinit var processRecordsTaskFactory: MockProcessRecordsTaskFactory
    @Inject lateinit var processBatchTaskFactory: MockProcessBatchTaskFactory
    @Inject lateinit var closeStreamTaskFactory: MockCloseStreamTaskFactory
    @Inject lateinit var teardownTaskFactory: MockTeardownTaskFactory

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
            fileEnvelope: BatchEnvelope<SpilledRawMessagesLocalFile>
        ): ProcessRecordsTask {
            return object : ProcessRecordsTask {
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

    class MockBatch(override val state: Batch.State) : Batch

    @Singleton
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockExceptionHandler : TaskLauncherExceptionHandler<DestinationWriteTask> {
        val wrappedTasks = Channel<DestinationWriteTask>(Channel.UNLIMITED)
        val wrappedTaskCount = AtomicLong(0)

        override fun withExceptionHandling(task: DestinationWriteTask): Task {
            runBlocking { wrappedTasks.send(task) }
            wrappedTaskCount.incrementAndGet()
            return task
        }
    }

    @Test
    fun testStart() = runTest {
        launch { taskRunner.run() }

        // Verify that setup has run
        taskLauncher.start()
        mockSetupTaskFactory.hasRun.receive()

        // Verify that spill to disk ran for each stream
        mockSpillToDiskTaskFactory.streamHasRun.values.forEach { it.receive() }

        // Collect the tasks wrapped by the exception handler: expect one Setup and [nStreams]
        // SpillToDisk
        mockExceptionHandler.wrappedTasks.close()
        val taskList = mockExceptionHandler.wrappedTasks.toList()
        Assertions.assertEquals(1, taskList.filterIsInstance<SetupTask>().size)
        Assertions.assertEquals(
            mockSpillToDiskTaskFactory.streamHasRun.size,
            taskList.filterIsInstance<SpillToDiskTask>().size
        )

        taskLauncher.stop()
    }

    @Test
    fun testHandleSetupComplete() = runTest {
        launch { taskRunner.run() }

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

        taskLauncher.stop()
    }

    @Test
    fun testHandleSpilledFileComplete() = runTest {
        launch { taskRunner.run() }

        launch {
            taskLauncher.handleNewSpilledFile(
                stream1,
                BatchEnvelope(
                    SpilledRawMessagesLocalFile(DefaultLocalFile(Path("not/a/real/file")), 100L)
                )
            )
        }

        processRecordsTaskFactory.hasRun.receive()
        taskLauncher.stop()
    }

    @Test
    fun testHandleNewBatch() = runTest {
        launch { taskRunner.run() }

        val range = TreeRangeSet.create(listOf(Range.closed(0L, 100L)))

        taskLauncher.handleStreamStarted(stream1)

        // Verify incomplete batch triggers process batch
        val incompleteBatch = BatchEnvelope(MockBatch(Batch.State.PERSISTED), range)
        taskLauncher.handleNewBatch(stream1, incompleteBatch)
        Assertions.assertTrue(
            syncManager.getStreamManager(stream1.descriptor).areRecordsPersistedUntil(100L)
        )
        val batchReceived = processBatchTaskFactory.hasRun.receive()
        Assertions.assertEquals(incompleteBatch, batchReceived)

        // Verify complete batch w/o batch processing complete does nothing
        val completeBatch = BatchEnvelope(MockBatch(Batch.State.COMPLETE))
        taskLauncher.handleNewBatch(stream1, completeBatch)
        delay(1000)
        Assertions.assertTrue(closeStreamTaskFactory.hasRun.tryReceive().isFailure)
        (syncManager.getStreamManager(stream1.descriptor) as MockStreamManager)
            .mockBatchProcessingComplete(true)

        // Verify complete batch w/ batch processing complete triggers close stream
        taskLauncher.handleNewBatch(stream1, completeBatch)
        closeStreamTaskFactory.hasRun.receive()
        Assertions.assertTrue(true)

        taskLauncher.stop()
    }

    @Test
    fun testHandleStreamClosed() = runTest {
        launch { taskRunner.run() }

        // This should run teardown unconditionally.
        launch { taskLauncher.handleStreamClosed(stream1) }
        teardownTaskFactory.hasRun.receive()

        taskLauncher.stop()
    }
}
