package io.airbyte.integrations.destination.databricks

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.async.deser.AirbyteMessageDeserializer
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure
import io.airbyte.integrations.destination.databricks.staging.DatabricksFlushFunction
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.util.*
import java.util.concurrent.Executors
import java.util.function.Consumer

class DatabricksDestination : BaseConnector(), Destination {

    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        throw NotImplementedError("GetConsumer is not supported, use getSerializedMessageConsumer")
    }

    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        TODO()
    }

    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer {
        val defaultNamespace =
            if (config.has("schema") && config.get("schema").isTextual) Optional.of(config["schema"].asText()) else Optional.empty()
        // If config has schema and isTextual then return Optional
        // else return Optional.empty()

        return AsyncStreamConsumer(
            outputRecordCollector,
            { },
            { _, streamSyncSummaries -> },
            DatabricksFlushFunction(128*1024*1024L),
            catalog,
            BufferManager((Runtime.getRuntime().maxMemory() * BufferManager.MEMORY_LIMIT_RATIO).toLong()),
            defaultNamespace,
            FlushFailure(),
            Executors.newFixedThreadPool(10),
            AirbyteMessageDeserializer()
        )
    }

    override val isV2Destination: Boolean
        get() = true
}
