/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base.spec_modification

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConnectorSpecification
import java.util.function.Consumer

abstract class SpecModifyingDestination(private val destination: Destination) : Destination {
    override val isV2Destination: Boolean = destination.isV2Destination

    @Throws(Exception::class)
    abstract fun modifySpec(originalSpec: ConnectorSpecification): ConnectorSpecification

    @Throws(Exception::class)
    override fun spec(): ConnectorSpecification {
        return modifySpec(destination.spec())
    }

    @Throws(Exception::class)
    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        return destination.check(config)
    }

    @Throws(Exception::class)
    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        return destination.getConsumer(config, catalog, outputRecordCollector)
    }

    @Throws(Exception::class)
    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer? {
        return destination.getSerializedMessageConsumer(config, catalog, outputRecordCollector)
    }
}
