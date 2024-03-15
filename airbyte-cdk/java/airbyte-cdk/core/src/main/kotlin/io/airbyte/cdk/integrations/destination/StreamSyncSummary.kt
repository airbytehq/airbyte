/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination

import java.util.*

/**
 * @param recordsWritten The number of records written to the stream, or empty if the caller does
 * not track this information. (this is primarily for backwards-compatibility with the legacy
 * destinations framework; new implementations should always provide this information). If
 * this value is empty, consumers should assume that the sync wrote nonzero records for this
 * stream.
 */
class StreamSyncSummary(recordsWritten: Optional<Long>) {
    val recordsWritten: Optional<Long>

    init {
        this.sessionHeartbeatInterval = sessionHeartbeatInterval
        this.globalHeartbeatInterval = globalHeartbeatInterval
        this.idleTimeout = idleTimeout
        this.stream = stream
        this.consumer = consumer
        this.recordsWritten = recordsWritten
    }

    companion object {
        @JvmField
        val DEFAULT: StreamSyncSummary = StreamSyncSummary(Optional.empty())
    }
}
