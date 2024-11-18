package io.airbyte.cdk.load.task

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.DestinationRecordWrapped
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.StreamFlushTickMessage
import io.airbyte.cdk.load.state.Reserved
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton

@Singleton
class FlushTickTask(
    @Value("\${airbyte.flush.interval-ms}") private val tickIntervalMs: Long,
    private val timeUtils: TimeProvider,
    private val catalog: DestinationCatalog,
    private val recordQueueSupplier: MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationRecordWrapped>>,
): SyncLevel {
    override suspend fun execute() {
        while (true) {
            timeUtils.delay(tickIntervalMs)

            catalog.streams.forEach {
                val queue = recordQueueSupplier.get(it.descriptor)
                queue.publish(Reserved(value = StreamFlushTickMessage(timeUtils.currentTimeMillis())))
            }
        }
    }
}
