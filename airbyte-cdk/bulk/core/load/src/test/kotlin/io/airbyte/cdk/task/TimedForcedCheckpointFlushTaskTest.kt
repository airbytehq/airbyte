/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationConfiguration
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.file.MockTimeProvider
import io.airbyte.cdk.message.QueueReader
import io.airbyte.cdk.state.MockCheckpointManager
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
    @Inject lateinit var flushTaskFactory: DefaultTimedForcedCheckpointFlushTaskFactory
    @Inject lateinit var taskLauncher: MockTaskLauncher
    @Inject lateinit var timeProvider: MockTimeProvider
    @Inject lateinit var checkpointManager: MockCheckpointManager
    @Inject lateinit var config: DestinationConfiguration
    @Inject lateinit var queueReader: QueueReader<ForceFlushEvent>

    @Test
    fun testTaskWillNotFlushIfTimeNotElapsed() = runTest {
        val delayMs = 100L
        val task = flushTaskFactory.make(taskLauncher, delayMs)
        timeProvider.setCurrentTime(0L)
        val mockLastFlushTime = delayMs + config.maxCheckpointFlushTimeMs - 1L
        checkpointManager.mockLastFlushTimeMs = mockLastFlushTime
        task.execute()
        Assertions.assertEquals(
            delayMs,
            timeProvider.currentTimeMillis(),
            "task delayed the specified time"
        )
        Assertions.assertEquals(
            mutableListOf(delayMs),
            checkpointManager.flushedAtMs,
            "task tried to flush"
        )
        Assertions.assertNull(queueReader.poll(), "task did not produce a force flush event")
        val mockTimeSinceLastFlush = timeProvider.currentTimeMillis() - mockLastFlushTime
        val nextRun = config.maxCheckpointFlushTimeMs - mockTimeSinceLastFlush
        Assertions.assertEquals(
            listOf(nextRun),
            taskLauncher.scheduledForcedFlushes,
            "task scheduled next flush for remaining interval"
        )
    }

    @Test
    fun testTaskWillFlushIfTimeElapsed() = runTest {
        val delayMs =
            config.maxCheckpointFlushTimeMs // task uses flush interval as delay by default
        val task = flushTaskFactory.make(taskLauncher)
        timeProvider.setCurrentTime(0L)
        checkpointManager.mockLastFlushTimeMs = 0L
        val expectedMap =
            mutableMapOf(DestinationStream.Descriptor(name = "test", namespace = "testing") to 999L)
        checkpointManager.mockCheckpointIndexes = expectedMap
        task.execute()
        Assertions.assertEquals(
            delayMs,
            timeProvider.currentTimeMillis(),
            "task delayed for the configured interval"
        )
        Assertions.assertEquals(
            listOf(delayMs),
            checkpointManager.flushedAtMs,
            "task tried to flush"
        )
        val flushEvent = queueReader.poll()
        Assertions.assertEquals(
            expectedMap,
            flushEvent?.indexes,
            "task produced a force flush event with indexes provided by the checkpoint manager"
        )
        Assertions.assertEquals(
            listOf(config.maxCheckpointFlushTimeMs),
            taskLauncher.scheduledForcedFlushes,
            "task scheduled next flush for full interval"
        )
    }
}
