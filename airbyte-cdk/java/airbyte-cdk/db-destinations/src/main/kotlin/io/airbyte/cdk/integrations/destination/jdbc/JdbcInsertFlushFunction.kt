/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.RecordWriter
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.stream.Stream

class JdbcInsertFlushFunction(
    private val recordWriter: RecordWriter<PartialAirbyteMessage>,
    override val optimalBatchSizeBytes: Long
) : DestinationFlushFunction {
    @Throws(Exception::class)
    override fun flush(streamDescriptor: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        recordWriter.accept(
            AirbyteStreamNameNamespacePair(streamDescriptor.name, streamDescriptor.namespace),
            stream.toList()
        )
    }
}
