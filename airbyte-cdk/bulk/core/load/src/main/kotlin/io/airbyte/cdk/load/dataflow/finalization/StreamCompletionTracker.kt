/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.finalization

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicInteger

@Singleton
class StreamCompletionTracker(
    catalog: DestinationCatalog,
) {
    private val expectedCount = catalog.size()

    private val receivedCount = AtomicInteger()

    @Suppress("UNUSED_PARAMETER")
    fun accept(msg: DestinationRecordStreamComplete) {
        receivedCount.incrementAndGet()
    }

    fun allStreamsComplete() = receivedCount.get() == expectedCount
}
