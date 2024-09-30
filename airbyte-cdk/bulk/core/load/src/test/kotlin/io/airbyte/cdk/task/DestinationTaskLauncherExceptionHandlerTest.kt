/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.MockDestinationCatalogFactory.Companion.stream1
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(
    rebuildContext = true,
    environments =
        [
            "DestinationTaskLauncherExceptionHandlerTest",
            "MockDestinationCatalog",
        ]
)
class DestinationTaskLauncherExceptionHandlerTest {
    @Inject lateinit var taskRunner: TaskRunner
    @Inject lateinit var exceptionHandler: DestinationTaskLauncherExceptionHandler

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherExceptionHandlerTest"])
    class MockFailStreamTaskFactory : FailStreamTaskFactory {
        val didRunFor = Channel<Pair<DestinationStream, Exception>>()

        override fun make(
            exceptionHandler: DestinationTaskLauncherExceptionHandler,
            exception: Exception,
            stream: DestinationStream
        ): FailStreamTask {
            return object : FailStreamTask {
                override suspend fun execute() {
                    didRunFor.send(Pair(stream, exception))
                }
            }
        }
    }

    @Singleton
    @Primary
    @Requires(env = ["DestinationTaskLauncherExceptionHandlerTest"])
    class MockFailSyncTaskFactory : FailSyncTaskFactory {
        val didRunWith = Channel<Exception>()

        override fun make(
            exceptionHandler: DestinationTaskLauncherExceptionHandler,
            exception: Exception
        ): FailSyncTask {
            return object : FailSyncTask {
                override suspend fun execute() {
                    didRunWith.send(exception)
                }
            }
        }
    }

    /**
     * test surface: validate that the wrapper directs failures in
     * - StreamTask(s) to handleStreamFailure (and to an injected Mock FailStreamTask)
     * - SyncTask(s) to handleSyncFailure (and to an injected Mock FailSyncTask)
     */
    @Test
    fun testHandleStreamFailure(mockFailStreamTaskFactory: MockFailStreamTaskFactory) = runTest {
        launch { taskRunner.run() }

        val mockTask =
            object : StreamTask {
                override val stream: DestinationStream = stream1

                override suspend fun execute() {
                    throw RuntimeException("StreamTask failure")
                }
            }

        val wrappedTask = exceptionHandler.withExceptionHandling(mockTask)
        launch { wrappedTask.execute() }
        val (stream, exception) = mockFailStreamTaskFactory.didRunFor.receive()
        Assertions.assertEquals(stream1, stream)
        Assertions.assertTrue(exception is RuntimeException)

        taskRunner.close()
    }

    @Test
    fun testHandleSyncFailure(mockFailSyncTaskFactory: MockFailSyncTaskFactory) = runTest {
        launch { taskRunner.run() }

        val mockTask =
            object : SyncTask {
                override suspend fun execute() {
                    throw RuntimeException("SyncTask failure")
                }
            }

        val wrappedTask = exceptionHandler.withExceptionHandling(mockTask)
        launch { wrappedTask.execute() }
        val exception = mockFailSyncTaskFactory.didRunWith.receive()
        Assertions.assertTrue(exception is RuntimeException)

        taskRunner.close()
    }
}
