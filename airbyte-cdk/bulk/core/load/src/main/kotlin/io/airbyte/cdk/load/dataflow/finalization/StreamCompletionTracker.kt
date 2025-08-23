/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.finalization

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicInteger

/**
 * Simply tracks whether we've received the number of stream complete messages we expect.
 *
 * It does not do any stream name / namespace matching as the platform currently emit all the
 * completes at once at the end of the sync. Nonetheless, the interface is designed to allow that
 * functionality to be added later.
 */
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
