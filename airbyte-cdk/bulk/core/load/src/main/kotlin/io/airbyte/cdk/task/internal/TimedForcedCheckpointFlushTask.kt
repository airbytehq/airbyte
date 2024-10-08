/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task.internal

import io.airbyte.cdk.command.DestinationConfiguration
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.file.TimeProvider
import io.airbyte.cdk.message.ChannelMessageQueue
import io.airbyte.cdk.message.QueueWriter
import io.airbyte.cdk.state.CheckpointManager
import io.airbyte.cdk.task.SyncTask
import io.airbyte.cdk.util.use
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface TimedForcedCheckpointFlushTask : SyncTask

@Singleton
@Secondary
class DefaultTimedForcedCheckpointFlushTask(
    private val config: DestinationConfiguration,
    private val checkpointManager: CheckpointManager<DestinationStream.Descriptor, *>,
    private val eventQueue: QueueWriter<ForceFlushEvent>,
    private val timeProvider: TimeProvider,
) : TimedForcedCheckpointFlushTask {
    private val log = KotlinLogging.logger {}

    override suspend fun execute() {
        val cadenceMs = config.maxCheckpointFlushTimeMs
        // Wait for the configured time
        log.info { "Sleeping for ${cadenceMs}ms" }
        timeProvider.delay(cadenceMs)

        eventQueue.use {
            while (true) {
                // Flush whatever is handy
                checkpointManager.flushReadyCheckpointMessages()

                // Compare the time since the last successful flush to the configured interval
                val lastFlushTimeMs = checkpointManager.getLastSuccessfulFlushTimeMs()
                val nowMs = timeProvider.currentTimeMillis()
                val timeSinceLastFlushMs = nowMs - lastFlushTimeMs

                if (timeSinceLastFlushMs >= cadenceMs) {
                    val nextIndexes = checkpointManager.getNextCheckpointIndexes()
                    log.info {
                        "${timeSinceLastFlushMs}ms since last flush, forcing flush at $nextIndexes"
                    }
                    it.publish(ForceFlushEvent(nextIndexes))
                    timeProvider.delay(cadenceMs)
                    log.info { "Flush event published; sleeping for ${cadenceMs}ms" }
                } else {
                    val timeUntilNextAttempt = cadenceMs - timeSinceLastFlushMs
                    log.info {
                        "$timeSinceLastFlushMs < $cadenceMs ms elapsed, sleeping for $timeUntilNextAttempt"
                    }
                    timeProvider.delay(timeUntilNextAttempt)
                }
            }
        }
    }
}

data class ForceFlushEvent(val indexes: Map<DestinationStream.Descriptor, Long>)

@Singleton
@Secondary
class DefaultForceFlushEventMessageQueue : ChannelMessageQueue<ForceFlushEvent>()
