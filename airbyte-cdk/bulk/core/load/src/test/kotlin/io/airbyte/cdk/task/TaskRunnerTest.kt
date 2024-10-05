/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.channels.ClosedSendChannelException
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class TaskRunnerTest {
    @Test
    fun testTasksCompleteAfterClose() = runTest {
        val task1Completed = AtomicBoolean(false)
        val task2Completed = AtomicBoolean(false)
        val task3Completed = AtomicBoolean(false)

        val innerTaskCompleted = AtomicBoolean(false)
        val innerTaskEnqueueFailed = AtomicBoolean(false)

        val task1ReportingChannel = Channel<Unit>()
        val task2ReportingChannel = Channel<Unit>()
        val task3ReportingChannel = Channel<Unit>()

        val task2BlockingChannel = Channel<Unit>()

        // Make 3 tasks.
        // - the first one should complete right away
        // - the second one will block until we send a message to it
        // - BUT the third one will not be blocked by the second
        // - AND the second one should still run after we close the runner
        // - BUT the second one tried to enqueue another after close, which throws
        val runner = TaskRunner()
        val task1 =
            object : Task {
                override suspend fun execute() {
                    task1Completed.set(true)
                    task1ReportingChannel.send(Unit)
                }
            }
        val task2 =
            object : Task {
                override suspend fun execute() {
                    task2BlockingChannel.receive()
                    task2Completed.set(true)
                    try {
                        runner.enqueue(
                            object : Task {
                                override suspend fun execute() {
                                    innerTaskCompleted.set(true)
                                }
                            }
                        )
                    } catch (e: ClosedSendChannelException) {
                        innerTaskEnqueueFailed.set(true)
                    }
                    task2ReportingChannel.send(Unit)
                }
            }
        val task3 =
            object : Task {
                override suspend fun execute() {
                    task3Completed.set(true)
                    task3ReportingChannel.send(Unit)
                }
            }

        runner.enqueue(task1)
        runner.enqueue(task2)
        runner.enqueue(task3)

        launch { runner.run() }

        task1ReportingChannel.receive() // wait for task1 to complete
        Assertions.assertTrue(task1Completed.get())
        Assertions.assertFalse(task2Completed.get())

        task3ReportingChannel.receive() // wait for task3 to complete
        Assertions.assertTrue(task3Completed.get())
        Assertions.assertFalse(task2Completed.get())

        runner.close()
        task2BlockingChannel.send(Unit)
        task2ReportingChannel.receive() // wait for task2 to complete
        Assertions.assertTrue(task2Completed.get())

        Assertions.assertTrue(innerTaskEnqueueFailed.get())
        Assertions.assertFalse(innerTaskCompleted.get())
    }
}
