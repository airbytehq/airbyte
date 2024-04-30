/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.buffered_stream_consumer

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.protocol.models.v0.StreamDescriptor

/**
 * Interface allowing destination to specify clean up logic that must be executed after all
 * record-related logic has finished.
 *
 * The @JvmSuppressWildcards is here so that the 2nd parameter of accept stays a java
 * Map<StreamDescriptor, StreamSyncSummary> rather than becoming a Map<StreamDescriptor, ? extends
 * StreamSyncSummary>
 */
fun interface OnCloseFunction {
    /**
     * @param streamSyncSummaries This map MAY be missing some streams that happened during the sync.
     * Streams not in the map should be treated as equivalent to [StreamSyncSummary.DEFAULT].
     */
    @JvmSuppressWildcards
    @Throws(Exception::class)
    fun accept(
        hasFailed: Boolean,
        streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>,
        streamsWithSuccessStatus: Set<StreamDescriptor>?,
    )
}
