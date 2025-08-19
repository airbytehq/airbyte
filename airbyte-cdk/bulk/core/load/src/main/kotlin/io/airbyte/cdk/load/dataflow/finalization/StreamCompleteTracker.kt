package io.airbyte.cdk.load.dataflow.finalization

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicInteger

@Singleton
class StreamCompleteTracker(
    catalog: DestinationCatalog,
) {
    private val expectedCount = catalog.streams.size

    private val receivedCount = AtomicInteger()

    fun accept(msg: DestinationRecordStreamComplete) {
        receivedCount.incrementAndGet()
    }

    fun allStreamsComplete() = receivedCount.get() == expectedCount
}
