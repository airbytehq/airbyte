/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationConfiguration
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.file.TimeProvider
import io.airbyte.cdk.message.ChannelMessageQueue
import io.airbyte.cdk.message.QueueWriter
import io.airbyte.cdk.state.CheckpointManager
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface TimedForcedCheckpointFlushTask : SyncTask

class DefaultTimedForcedCheckpointFlushTask(
    private val delayMs: Long,
    private val cadenceMs: Long,
    private val checkpointManager: CheckpointManager<DestinationStream.Descriptor, *>,
    private val eventQueue: QueueWriter<ForceFlushEvent>,
    private val timeProvider: TimeProvider,
    private val taskLauncher: DestinationTaskLauncher
) : TimedForcedCheckpointFlushTask {

    override suspend fun execute() {
        // Wait for the configured time
        timeProvider.delay(delayMs)

        // Flush whatever is handy
        checkpointManager.flushReadyCheckpointMessages()

        // Compare the time since the last successful flush to the configured interval
        val lastFlushTimeMs = checkpointManager.getLastSuccessfulFlushTimeMs()
        val nowMs = timeProvider.currentTimeMillis()
        val timeSinceLastFlushMs = nowMs - lastFlushTimeMs

        if (timeSinceLastFlushMs >= cadenceMs) {
            // If the max time has elapsed, emit a force flush event with provided next checkpoint
            // indexes
            val nextIndexes = checkpointManager.getNextCheckpointIndexes()
            eventQueue.publish(ForceFlushEvent(nextIndexes))
            taskLauncher.scheduleNextForceFlushAttempt(cadenceMs)
        } else {
            // Otherwise schedule the next attempt to run at {time of last flush + configured
            // interval}
            taskLauncher.scheduleNextForceFlushAttempt(cadenceMs - timeSinceLastFlushMs)
        }
    }
}

interface TimedForcedCheckpointFlushTaskFactory {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        delayMs: Long? = null
    ): TimedForcedCheckpointFlushTask
}

@Singleton
@Secondary
class DefaultTimedForcedCheckpointFlushTaskFactory(
    private val config: DestinationConfiguration,
    private val checkpointManager: CheckpointManager<DestinationStream.Descriptor, *>,
    private val eventQueue: QueueWriter<ForceFlushEvent>,
    private val timeProvider: TimeProvider
) : TimedForcedCheckpointFlushTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        delayMs: Long?
    ): TimedForcedCheckpointFlushTask {
        return DefaultTimedForcedCheckpointFlushTask(
            delayMs ?: config.maxCheckpointFlushTimeMs,
            config.maxCheckpointFlushTimeMs,
            checkpointManager,
            eventQueue,
            timeProvider,
            taskLauncher
        )
    }
}

data class ForceFlushEvent(val indexes: Map<DestinationStream.Descriptor, Long>)

@Singleton
@Secondary
class DefaultForceFlushEventMessageQueue : ChannelMessageQueue<ForceFlushEvent>()
