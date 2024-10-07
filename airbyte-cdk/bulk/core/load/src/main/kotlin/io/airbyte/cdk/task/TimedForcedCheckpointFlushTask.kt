/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationConfiguration
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.file.TimeProvider
import io.airbyte.cdk.state.CheckpointManager
import io.airbyte.cdk.state.EventConsumer
import io.airbyte.cdk.state.EventProducer
import io.micronaut.context.annotation.Prototype
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import kotlinx.coroutines.delay

interface TimedForcedCheckpointFlushTask : SyncTask

class DefaultTimedForcedCheckpointFlushTask(
    private val delayMs: Long,
    private val cadenceMs: Long,
    private val checkpointManager: CheckpointManager<DestinationStream.Descriptor, *>,
    private val eventProducer: EventProducer<ForceFlushEvent>,
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
            eventProducer.produce(ForceFlushEvent(nextIndexes))
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
    private val eventProducer: EventProducer<ForceFlushEvent>,
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
            eventProducer,
            timeProvider,
            taskLauncher
        )
    }
}

data class ForceFlushEvent(val indexes: Map<DestinationStream.Descriptor, Long>)

@Singleton @Secondary class DefaultForceFlushEventProducer : EventProducer<ForceFlushEvent>()

@Prototype
@Secondary
class DefaultForceFlushEventConsumer(private val eventProducer: EventProducer<ForceFlushEvent>) :
    EventConsumer<ForceFlushEvent>(eventProducer)
