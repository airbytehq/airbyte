/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.snapshot

import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.integrations.source.mongodbv3.read.record.MongoDbSharedState

/** Per-stream read state: ties a [Stream] feed to the shared client and configuration. */
class MongoDbStreamState(
    val sharedState: MongoDbSharedState,
    val streamFeedBootstrap: StreamFeedBootstrap,
) {
    val stream: Stream
        get() = streamFeedBootstrap.feed

    val isFullRefresh: Boolean
        get() = stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH

    /** Terminal snapshot status for this stream: full-refresh streams never become `COMPLETE`. */
    val terminalStatus: MongoDbSnapshotStatus
        get() =
            if (isFullRefresh) MongoDbSnapshotStatus.FULL_REFRESH
            else MongoDbSnapshotStatus.COMPLETE
}
