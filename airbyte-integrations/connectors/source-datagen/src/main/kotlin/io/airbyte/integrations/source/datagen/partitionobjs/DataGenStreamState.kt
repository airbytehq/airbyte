package io.airbyte.integrations.source.datagen.partitionobjs

import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap

class DataGenStreamState(
    val sharedState: DataGenSharedState, val streamFeedBootstrap: StreamFeedBootstrap) {
    val stream: Stream
        get() = streamFeedBootstrap.feed
}
