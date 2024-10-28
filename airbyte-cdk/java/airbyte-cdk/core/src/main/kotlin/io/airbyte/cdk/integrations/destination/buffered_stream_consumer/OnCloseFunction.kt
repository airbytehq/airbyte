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
    @JvmSuppressWildcards
    @Throws(Exception::class)
    fun accept(
        hasFailed: Boolean,
        streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>,
    )
}
