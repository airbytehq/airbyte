package io.airbyte.integrations.destination.databricks.staging

import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.stream.Stream

class DatabricksFlushFunction(override val optimalBatchSizeBytes: Long) : DestinationFlushFunction {
    override fun flush(decs: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        TODO("Not yet implemented")
    }
}
