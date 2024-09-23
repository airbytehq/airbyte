/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import com.google.common.collect.Range
import com.google.common.collect.TreeRangeSet
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream1
import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream2
import io.airbyte.cdk.file.DefaultLocalFile
import io.airbyte.cdk.message.Batch
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.CheckpointMessage
import io.airbyte.cdk.message.DestinationRecord
import io.airbyte.cdk.message.SimpleBatch
import io.airbyte.cdk.message.SpilledRawMessagesLocalFile
import io.airbyte.cdk.state.CheckpointManager
import io.airbyte.cdk.state.MockStreamManager
import io.airbyte.cdk.state.MockStreamsManager
import io.airbyte.cdk.state.StreamsManager
import io.airbyte.cdk.write.DestinationWriteOperation
import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import kotlin.io.path.Path
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(rebuildContext = true, environments = ["DestinationTaskLauncherTest"])
class DestinationTaskLauncherTest {
    @Inject lateinit var taskRunner: TaskRunner
    @Inject lateinit var taskLauncherFactory: DestinationTaskLauncherFactory
    @Inject lateinit var streamsManager: StreamsManager
    @Inject lateinit var checkpointManager: MockCheckpointManager

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

        override fun make(taskLauncher: DestinationTaskLauncher): SetupTask {
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
        val streamHasRun = mutableMapOf<DestinationStream, Channel<Unit>>()

        init {
            catalog.streams.forEach { streamHasRun[it] = Channel(Channel.UNLIMITED) }
        }

        override fun make(
            taskLauncher: DestinationTaskLauncher,
            stream: DestinationStream
        ): SpillToDiskTask {
            return object : SpillToDiskTask {
                override suspend fun execute() {
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
    @Replaces(DefaultProcessRecordsTaskFactory::class)
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockProcessRecordsTaskFactory : ProcessRecordsTaskFactory {
        val hasRun: Channel<Unit> = Channel(Channel.UNLIMITED)

        override fun make(
            taskLauncher: DestinationTaskLauncher,
            streamLoader: StreamLoader,
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
            streamLoader: StreamLoader,
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
            streamLoader: StreamLoader
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

    @Factory
    class MockStreamsManagerFactory {
        @Singleton
        @Primary
        @Requires(env = ["DestinationTaskLauncherTest"])
        fun make(catalog: DestinationCatalog): MockStreamsManager {
            return MockStreamsManager(catalog)
        }
    }

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockCheckpointManager : CheckpointManager<DestinationStream, CheckpointMessage> {
        val hasBeenFlushed = Channel<Unit>()

        override fun addStreamCheckpoint(
            key: DestinationStream,
            index: Long,
            checkpointMessage: CheckpointMessage
        ) {
            TODO("Not needed")
        }

        override fun addGlobalCheckpoint(
            keyIndexes: List<Pair<DestinationStream, Long>>,
            checkpointMessage: CheckpointMessage
        ) {
            TODO("Not needed")
        }

        override suspend fun flushReadyCheckpointMessages() {
            hasBeenFlushed.send(Unit)
        }
    }

    class MockDestinationWrite : DestinationWriteOperation {
        override fun getStreamLoader(stream: DestinationStream): StreamLoader {
            return object : StreamLoader {
                override val stream: DestinationStream = stream

                override suspend fun processRecords(
                    records: Iterator<DestinationRecord>,
                    totalSizeBytes: Long
                ): Batch {
                    return SimpleBatch(state = Batch.State.COMPLETE)
                }
            }
        }
    }

    class MockBatch(override val state: Batch.State) : Batch

    @Test
    fun testStart() = runTest {
        val launcher = taskLauncherFactory.get()
        launch { taskRunner.run() }
        launcher.start()
        mockSetupTaskFactory.hasRun.receive()
        mockSpillToDiskTaskFactory.streamHasRun.values.forEach { it.receive() }
        launcher.stop()
    }

    @Test
    fun testHandleSetupComplete() = runTest {
        val launcher = taskLauncherFactory.get()
        launch { taskRunner.run() }
        launcher.handleSetupComplete()
        mockOpenStreamTaskFactory.streamHasRun.values.forEach { it.receive() }
        launcher.stop()
    }

    @Test
    fun testHandleJoinStreamOpenSpilledFileComplete() = runTest {
        val launcher = taskLauncherFactory.get()
        launch { taskRunner.run() }

        // This will block until the stream is done opening.
        launch {
            launcher.handleNewSpilledFile(
                stream1,
                BatchEnvelope(
                    SpilledRawMessagesLocalFile(DefaultLocalFile(Path("not/a/real/file")), 100L)
                )
            )
        }

        // So, it should not have run yet.

        delay(1000)
        val processRecordsHasRun = processRecordsTaskFactory.hasRun.tryReceive()
        Assertions.assertTrue(processRecordsHasRun.isFailure)

        // This should unblock the processRecords task.
        val destination = MockDestinationWrite()
        launcher.handleStreamOpen(destination.getStreamLoader(stream1))
        processRecordsTaskFactory.hasRun.receive()
        Assertions.assertTrue(true)

        launcher.stop()
    }

    @Test
    fun testHandleNewBatch() = runTest {
        val launcher = taskLauncherFactory.get()
        launch { taskRunner.run() }

        val range = TreeRangeSet.create(listOf(Range.closed(0L, 100L)))

        val destination = MockDestinationWrite()
        val streamLoader = destination.getStreamLoader(stream1)
        launcher.handleStreamOpen(streamLoader)

        // Verify incomplete batch triggers process batch
        val incompleteBatch = BatchEnvelope(MockBatch(Batch.State.PERSISTED), range)
        launcher.handleNewBatch(streamLoader, incompleteBatch)
        Assertions.assertTrue(streamsManager.getManager(stream1).areRecordsPersistedUntil(100L))
        val batchReceived = processBatchTaskFactory.hasRun.receive()
        Assertions.assertEquals(incompleteBatch, batchReceived)

        // Verify complete batch w/o batch processing complete does nothing
        val completeBatch = BatchEnvelope(MockBatch(Batch.State.COMPLETE))
        launcher.handleNewBatch(streamLoader, completeBatch)
        delay(1000)
        Assertions.assertTrue(closeStreamTaskFactory.hasRun.tryReceive().isFailure)
        (streamsManager.getManager(stream1) as MockStreamManager).mockBatchProcessingComplete(true)

        // Verify complete batch w/ batch processing complete triggers close stream
        launcher.handleNewBatch(streamLoader, completeBatch)
        closeStreamTaskFactory.hasRun.receive()
        Assertions.assertTrue(true)

        launcher.stop()
    }

    @Test
    fun testHandleStreamClosed() = runTest {
        val launcher = taskLauncherFactory.get()
        launch { taskRunner.run() }

        // This should not run teardown until all streams are closed.
        launch { launcher.handleStreamClosed(stream1) }
        delay(1000)
        val hasRun = teardownTaskFactory.hasRun.tryReceive()
        Assertions.assertTrue(hasRun.isFailure)
        checkpointManager.hasBeenFlushed.receive() // Stream1 close triggered flush
        streamsManager.getManager(stream1).markClosed()
        delay(1000)
        val hasRun2 = teardownTaskFactory.hasRun.tryReceive()
        Assertions.assertTrue(hasRun2.isFailure)
        streamsManager.getManager(stream2).markClosed()
        teardownTaskFactory.hasRun.receive()
        Assertions.assertTrue(true)

        // This should do nothing, since the teardown task has already run.
        launch { launcher.handleStreamClosed(stream2) }
        delay(1000)
        val hasRun3 = teardownTaskFactory.hasRun.tryReceive()
        Assertions.assertTrue(hasRun3.isFailure)
        checkpointManager.hasBeenFlushed.receive() // Stream2 close triggered flush

        launcher.stop()
    }
}
