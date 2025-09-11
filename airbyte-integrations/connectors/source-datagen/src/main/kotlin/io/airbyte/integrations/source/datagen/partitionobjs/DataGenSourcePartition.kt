package io.airbyte.integrations.source.datagen.partitionobjs

import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Stream

class DataGenSourcePartition(val streamState: DataGenStreamState) {
    val stream: Stream = streamState.stream
    // val from = From(stream.name, stream.namespace)
}
