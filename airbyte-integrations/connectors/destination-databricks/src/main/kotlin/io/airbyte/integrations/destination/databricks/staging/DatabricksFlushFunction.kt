/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.staging

import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.integrations.destination.databricks.sync.DatabricksSyncOperations
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.*
import java.util.stream.Stream

class DatabricksFlushFunction(
    override val optimalBatchSizeBytes: Long,
    private val syncOperations: DatabricksSyncOperations
) : DestinationFlushFunction {

    override fun flush(decs: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        syncOperations.flushStream(decs, stream)
    }
}
