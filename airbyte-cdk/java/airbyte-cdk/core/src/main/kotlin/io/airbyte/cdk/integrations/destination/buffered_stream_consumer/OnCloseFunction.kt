/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.buffered_stream_consumer

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.commons.functional.CheckedBiConsumer
import io.airbyte.protocol.models.v0.StreamDescriptor

/**
 * Interface allowing destination to specify clean up logic that must be executed after all
 * record-related logic has finished.
 *
 * The map of StreamSyncSummaries MUST be non-null, but MAY be empty. Streams not present in the map
 * will be treated as equivalent to [StreamSyncSummary.DEFAULT].
 *
 * The @JvmSuppressWildcards is here so that the 2nd parameter of accept stays a java
 * Map<StreamDescriptor, StreamSyncSummary> rather than becoming a Map<StreamDescriptor, ? extends
 * StreamSyncSummary>
 */
fun interface OnCloseFunction :
    CheckedBiConsumer<
        Boolean, @JvmSuppressWildcards Map<StreamDescriptor, StreamSyncSummary>, Exception>
