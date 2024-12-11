/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.task.KillableScope
import io.airbyte.cdk.load.util.use
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface TimedForcedCheckpointFlushTask : KillableScope

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
