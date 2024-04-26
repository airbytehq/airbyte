/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.sync

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.protocol.models.v0.StreamDescriptor

/** Connector sync operations */
interface SyncOperations {
    fun initializeStreams()
    fun flushStreams()
    fun finalizeStreams(streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>)
}
