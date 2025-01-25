/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.DestinationStreamEvent
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.StreamFlushEvent
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.time.Clock
import kotlinx.coroutines.channels.ClosedSendChannelException

@Singleton
@Secondary
class FlushTickTask(
    @Value("\${airbyte.destination.core.flush.rate-ms}") private val tickIntervalMs: Long,
    private val clock: Clock,
    private val coroutineTimeUtils: TimeProvider,
    private val catalog: DestinationCatalog,
    private val recordQueueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>,
) : Task {
    private val log = KotlinLogging.logger {}

    override val terminalCondition: TerminalCondition = OnEndOfSync

    override suspend fun execute() {
        while (true) {
            waitAndPublishFlushTick()
        }
    }

    @VisibleForTesting
    suspend fun waitAndPublishFlushTick() {
        coroutineTimeUtils.delay(tickIntervalMs)

        catalog.streams.forEach {
            val queue = recordQueueSupplier.get(it.descriptor)
            if (queue.isClosedForPublish()) {
                return@forEach
            }
            try {
                queue.publish(Reserved(value = StreamFlushEvent(clock.millis())))
            } catch (e: ClosedSendChannelException) {
                log.info { "Attempted to flush closed queue for ${it.descriptor}. Ignoring..." }
            }
        }
    }
}
