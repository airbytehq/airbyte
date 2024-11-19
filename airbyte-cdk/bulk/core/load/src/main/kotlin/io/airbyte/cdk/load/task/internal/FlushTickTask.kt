/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.DestinationRecordWrapped
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.StreamFlushTickMessage
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.task.KillableScope
import io.airbyte.cdk.load.task.SyncLevel
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.time.Clock

@Singleton
class FlushTickTask(
    @Value("\${airbyte.flush.rate-ms}") private val tickIntervalMs: Long,
    private val clock: Clock,
    private val coroutineTimeUtils: TimeProvider,
    private val catalog: DestinationCatalog,
    private val recordQueueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationRecordWrapped>>,
) : SyncLevel, KillableScope {
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
            queue.publish(Reserved(value = StreamFlushTickMessage(clock.millis())))
        }
    }
}
