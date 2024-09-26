/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.write

import io.airbyte.cdk.Operation
import io.airbyte.cdk.task.Task
import io.airbyte.cdk.task.TaskLauncher
import io.airbyte.cdk.task.TaskRunner
import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.withContext
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["WriteOperationTest"])
@Property(name = Operation.PROPERTY, value = "write")
class WriteOperationTest {
    @Inject lateinit var writeOperation: WriteOperation

    @Singleton
    @Requires(env = ["WriteOperationTest"])
    class NoopInputConsumer : InputConsumer<String> {
        override suspend fun run() {
            // Do nothing
        }
    }

    @Singleton
    @Requires(env = ["WriteOperationTest"])
    class SimpleTaskLauncher(override val taskRunner: TaskRunner) : TaskLauncher {
        val handledException = CompletableDeferred<Boolean>()

        override suspend fun start() {
            taskRunner.enqueue(
                object : Task {
                    override suspend fun execute() {
                        throw RuntimeException("Task failed.")
                    }
                }
            )
        }

        override suspend fun handleException(t: Throwable) {
            // Do this with a task to verify that the
            // exception workflow can still run tasks.
            taskRunner.enqueue(
                object : Task {
                    override suspend fun execute() {
                        handledException.complete(true)
                    }
                }
            )
        }
    }

    @Test
    fun testExceptionHandling(simpleTaskLauncher: SimpleTaskLauncher) = runTest {
        /**
         * Normally `runTest` is sufficient, but because [WriteOperation] uses `runBlocking` we need
         * to wrap the test in `withContext(Dispatchers.IO)` to prevent it from blocking. (Ie,
         * because [WriteOperation] is our "main" function we should treat it like a blocking IO
         * operation.)
         */
        withContext(Dispatchers.IO) {
            launch { writeOperation.execute() }
            Assertions.assertTrue(simpleTaskLauncher.handledException.await())
            simpleTaskLauncher.stop()
        }
    }
}
