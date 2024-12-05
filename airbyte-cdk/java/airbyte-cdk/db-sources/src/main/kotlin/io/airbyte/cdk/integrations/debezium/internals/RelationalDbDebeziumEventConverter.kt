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
        val debeziumEvent = event.eventValueAsJson
        val before: JsonNode? = debeziumEvent?.get(DebeziumEventConverter.Companion.BEFORE_EVENT)
        val after: JsonNode? = debeziumEvent?.get(DebeziumEventConverter.Companion.AFTER_EVENT)
        val source: JsonNode =
            checkNotNull(debeziumEvent?.get(DebeziumEventConverter.Companion.SOURCE_EVENT)) {
                "ChangeEvent contains no source record $debeziumEvent"
            }

        if (listOf(before, after).all { it == null }) {
            throw IllegalStateException(
                "ChangeEvent contains no before or after records $debeziumEvent"
            )
        }
        // Value of before and after may be a null or a NullNode object,
        // representing a "null" in json
        val baseNode =
            when (after?.isNull == true) {
                true -> before
                false -> after
            }
                as ObjectNode

        val data: JsonNode =
            DebeziumEventConverter.Companion.addCdcMetadata(
                baseNode,
                source,
                cdcMetadataInjector,
                after?.isNull == true
            )
        return DebeziumEventConverter.Companion.buildAirbyteMessage(
            source,
            cdcMetadataInjector,
            emittedAt,
            data
        )
    }
}
