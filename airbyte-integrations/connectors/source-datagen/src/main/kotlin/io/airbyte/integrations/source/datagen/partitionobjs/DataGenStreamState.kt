package io.airbyte.integrations.source.datagen.partitionobjs

import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap

class DataGenStreamState(
    val sharedState: DataGenSharedState, val streamFeedBootstrap: StreamFeedBootstrap) {
    val stream: Stream
        get() = streamFeedBootstrap.feed

    companion object {
        var completeState: OpaqueStateValue = TextNode("done")
    }
}
