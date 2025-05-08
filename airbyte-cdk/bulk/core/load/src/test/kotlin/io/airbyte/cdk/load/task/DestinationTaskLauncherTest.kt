/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationConfiguration
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.FileTransferQueueMessage
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.InputPartitioner
import io.airbyte.cdk.load.pipeline.LoadPipeline
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
import io.airbyte.cdk.load.task.implementor.SetupTask
import io.airbyte.cdk.load.task.implementor.SetupTaskFactory
import io.airbyte.cdk.load.task.implementor.TeardownTask
import io.airbyte.cdk.load.task.implementor.TeardownTaskFactory
import io.airbyte.cdk.load.task.internal.InputConsumerTask
import io.airbyte.cdk.load.task.internal.InputConsumerTaskFactory
import io.airbyte.cdk.load.task.internal.ReservingDeserializingInputFlow
import io.airbyte.cdk.load.task.internal.UpdateCheckpointsTask
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import io.mockk.mockk
import jakarta.inject.Inject
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.channels.toList
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
        ]
)
class DestinationTaskLauncherTest {
    @Inject lateinit var taskScopeProvider: TaskScopeProvider
    @Inject lateinit var taskLauncher: DestinationTaskLauncher
    @Inject lateinit var syncManager: SyncManager

    @Inject lateinit var mockInputConsumerTask: MockInputConsumerTaskFactory
    @Inject lateinit var mockSetupTaskFactory: MockSetupTaskFactory
    @Inject lateinit var closeStreamTaskFactory: MockCloseStreamTaskFactory
    @Inject lateinit var teardownTaskFactory: MockTeardownTaskFactory
    @Inject lateinit var updateCheckpointsTask: MockUpdateCheckpointsTask
    @Inject lateinit var inputFlow: ReservingDeserializingInputFlow
    @Inject lateinit var queueWriter: MockQueueWriter
    @Inject lateinit var mockFailStreamTaskFactory: MockFailStreamTaskFactory
    @Inject lateinit var mockFailSyncTaskFactory: MockFailSyncTaskFactory
    @Inject lateinit var config: MockDestinationConfiguration

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockLoadPipeline : LoadPipeline(listOf())

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    fun inputFlow(): ReservingDeserializingInputFlow = mockk(relaxed = true)

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
    class MockInputConsumerTaskFactory : InputConsumerTaskFactory {
        val hasRun: Channel<Boolean> = Channel(Channel.UNLIMITED)

        override fun make(
            catalog: DestinationCatalog,
            inputFlow: ReservingDeserializingInputFlow,
            checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>,
            destinationTaskLauncher: DestinationTaskLauncher,
            fileTransferQueue: MessageQueue<FileTransferQueueMessage>,
            pipelineInputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
            partitioner: InputPartitioner,
            openStreamQueue: QueueWriter<DestinationStream>,
        ): InputConsumerTask {
            return object : InputConsumerTask {
                override val terminalCondition: TerminalCondition = SelfTerminating

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

        override fun make(taskLauncher: DestinationTaskLauncher): SetupTask {
            return object : SetupTask {
                override val terminalCondition: TerminalCondition = SelfTerminating

                override suspend fun execute() {
                    hasRun.send(Unit)
                }
            }
        }
    }

    @Singleton
    @Replaces(DefaultOpenStreamTaskFactory::class)
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockOpenStreamTaskFactory : OpenStreamTaskFactory {
        override fun make(): OpenStreamTask {
            return object : OpenStreamTask {
                override val terminalCondition: TerminalCondition = SelfTerminating

                override suspend fun execute() {
                    // Do nothing
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
                override val terminalCondition: TerminalCondition = SelfTerminating

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
                override val terminalCondition: TerminalCondition = SelfTerminating

                override suspend fun execute() {
                    hasRun.send(Unit)
                }
            }
        }
    }

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherTest"])
    class MockUpdateCheckpointsTask : UpdateCheckpointsTask {
        override val terminalCondition: TerminalCondition = SelfTerminating

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
            stream: DestinationStream.Descriptor,
            shouldRunStreamLoaderClose: Boolean,
        ): FailStreamTask {
            return object : FailStreamTask {
                override val terminalCondition: TerminalCondition = SelfTerminating

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
                override val terminalCondition: TerminalCondition = SelfTerminating

                override suspend fun execute() {
                    didRun.send(true)
                }
            }
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

        Assertions.assertTrue(
            updateCheckpointsTask.didRun.receive(),
            "update checkpoints task was started"
        )

        job.cancel()
    }

    @Test
    fun testHandleStreamClosed() = runTest {
        // This should run teardown unconditionally.
        launch { taskLauncher.handleStreamClosed() }
        teardownTaskFactory.hasRun.receive()
    }

    @Test
    fun `test sync failure after stream failure`() = runTest {
        val job = launch { taskLauncher.run() }
        taskLauncher.handleFailStreamComplete(Exception())
        taskLauncher.handleFailStreamComplete(Exception())
        taskLauncher.handleTeardownComplete()
        job.join()
        mockFailSyncTaskFactory.didRun.close()
        val runs = mockFailSyncTaskFactory.didRun.toList()
        Assertions.assertTrue(runs.all { it }, "FailSyncTask was run")
        Assertions.assertTrue(runs.size == 1, "FailSyncTask was run exactly once")
    }
}
