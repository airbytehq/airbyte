/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.debezium.CdcMetadataInjector
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.time.Instant

class RelationalDbDebeziumEventConverter(
    private val cdcMetadataInjector: CdcMetadataInjector<*>,
    private val emittedAt: Instant
) : DebeziumEventConverter {
    override fun toAirbyteMessage(event: ChangeEventWithMetadata): AirbyteMessage {
        val debeziumEvent = event.eventValueAsJson()
        val before: JsonNode = debeziumEvent.get(DebeziumEventConverter.Companion.BEFORE_EVENT)
        val after: JsonNode = debeziumEvent.get(DebeziumEventConverter.Companion.AFTER_EVENT)
        val source: JsonNode = debeziumEvent.get(DebeziumEventConverter.Companion.SOURCE_EVENT)

        val baseNode = (if (after.isNull) before else after) as ObjectNode
        val data: JsonNode =
            DebeziumEventConverter.Companion.addCdcMetadata(
                baseNode,
                source,
                cdcMetadataInjector,
                after.isNull
            )
        return DebeziumEventConverter.Companion.buildAirbyteMessage(
            source,
            cdcMetadataInjector,
            emittedAt,
            data
        )
    }
}
