/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.MockTimeProvider
import io.airbyte.cdk.load.message.QueueReader
import io.airbyte.cdk.load.state.MockCheckpointManager
import io.airbyte.cdk.load.task.MockTaskLauncher
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(
    rebuildContext = true,
    environments =
        [
            "TimedForcedCheckpointFlushTaskTest",
            "MockDestinationConfiguration",
            "MockCheckpointManager",
            "MockTaskLauncher",
            "MockTimeProvider"
        ]
)
class TimedForcedCheckpointFlushTaskTest {
    @Inject lateinit var flushTask: DefaultTimedForcedCheckpointFlushTask
    @Inject lateinit var taskLauncher: MockTaskLauncher
    @Inject lateinit var timeProvider: MockTimeProvider
    @Inject lateinit var checkpointManager: MockCheckpointManager
    @Inject lateinit var config: DestinationConfiguration
    @Inject lateinit var queueReader: QueueReader<ForceFlushEvent>

    @Test
    fun testTaskWillNotFlushIfTimeNotElapsed() = runTest {
        checkpointManager.maxNumFlushAttempts = 1 // One loop at most

        val delayMs = config.maxCheckpointFlushTimeMs
        timeProvider.setCurrentTime(0L)
        val mockLastFlushTime = 1L
        checkpointManager.mockLastFlushTimeMs = mockLastFlushTime
        try {
            flushTask.execute()
        } catch (e: IllegalStateException) {
            // do nothing
        }
        Assertions.assertEquals(
            mutableListOf(delayMs),
            checkpointManager.flushedAtMs,
            "task tried to flush at delay time"
        )
        Assertions.assertNull(queueReader.poll(), "task did not produce a force flush event")
        Assertions.assertEquals(delayMs + mockLastFlushTime, timeProvider.currentTimeMillis())
    }

    @Test
    fun testTaskWillFlushIfTimeElapsed() = runTest {
        checkpointManager.maxNumFlushAttempts = 1
        val delayMs = config.maxCheckpointFlushTimeMs
        timeProvider.setCurrentTime(0L)
        checkpointManager.mockLastFlushTimeMs = 0L
        val expectedMap =
            mutableMapOf(DestinationStream.Descriptor(name = "test", namespace = "testing") to 999L)
        checkpointManager.mockCheckpointIndexes = expectedMap
        try {
            flushTask.execute()
        } catch (e: IllegalStateException) {
            // do nothing
        }
        Assertions.assertEquals(
            delayMs * 2,
            timeProvider.currentTimeMillis(),
            "task delayed for the configured interval twice (once at the beginning, once after successfully flushing)"
        )
        Assertions.assertEquals(
            listOf(delayMs),
            checkpointManager.flushedAtMs,
            "task tried to flush immediately"
        )
        val flushEvent = queueReader.poll()
        Assertions.assertEquals(
            expectedMap,
            flushEvent?.indexes,
            "task produced a force flush event with indexes provided by the checkpoint manager"
        )
    }
}
