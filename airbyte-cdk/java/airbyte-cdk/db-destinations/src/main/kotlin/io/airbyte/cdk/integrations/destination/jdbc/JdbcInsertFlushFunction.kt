/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.partial_messages.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.RecordWriter
import io.airbyte.cdk.integrations.destination.jdbc.constants.GlobalDataSizeConstants
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.stream.Stream

class JdbcInsertFlushFunction(private val recordWriter: RecordWriter<PartialAirbyteMessage>) :
    DestinationFlushFunction {
    @Throws(Exception::class)
    override fun flush(desc: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        recordWriter.accept(
            AirbyteStreamNameNamespacePair(desc.name, desc.namespace),
            stream.toList()
        )
    }

    override val optimalBatchSizeBytes: Long
        get() = // TODO tune this value - currently SqlOperationUtils partitions 10K records per
            // insert statement,
            // but we'd like to stop doing that and instead control sql insert statement size via
            // batch size.
            GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES.toLong()
}
