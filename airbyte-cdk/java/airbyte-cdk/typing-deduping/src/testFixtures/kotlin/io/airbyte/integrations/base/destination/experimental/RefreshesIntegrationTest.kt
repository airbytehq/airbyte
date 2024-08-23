package io.airbyte.integrations.base.destination.experimental

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.Command
import io.airbyte.protocol.models.AirbyteRecordMessage
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.ConfiguredAirbyteStream
import org.junit.jupiter.api.Test

abstract class RefreshesIntegrationTest(
    override val destinationProcessFactory: RefreshableWarehouseDestinationProcessFactory,
    config: JsonNode,
) : IntegrationTest(
    destinationProcessFactory,
    config,
) {

    @Test
    open fun truncateRefresh() {
        // run two syncs, dump records, etc
    }
}

interface RefreshableWarehouseDestination: DestinationProcess {
    fun insertRawRecords(
        config: JsonNode,
        catalog: ConfiguredAirbyteStream,
        records: List<AirbyteRecordMessage>,
        suffix: String,
    )

    fun insertFinalRecords(
        config: JsonNode,
        catalog: ConfiguredAirbyteStream,
        records: List<AirbyteRecordMessage>,
        suffix: String,
    )
}


interface RefreshableWarehouseDestinationProcessFactory: DestinationProcessFactory {
    override fun runDestination(
        command: Command,
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
    ): RefreshableWarehouseDestination
}
