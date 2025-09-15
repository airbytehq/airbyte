/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.debezium.CdcMetadataInjector
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.time.Instant

interface DebeziumEventConverter {
    fun toAirbyteMessage(event: ChangeEventWithMetadata): AirbyteMessage

    companion object {
        @JvmStatic
        fun buildAirbyteMessage(
            source: JsonNode?,
            cdcMetadataInjector: CdcMetadataInjector<*>,
            emittedAt: Instant,
            data: JsonNode?
        ): AirbyteMessage {
            val streamNamespace = cdcMetadataInjector.namespace(source)
            val streamName = cdcMetadataInjector.name(source)

            val airbyteRecordMessage =
                AirbyteRecordMessage()
                    .withStream(streamName)
                    .withNamespace(streamNamespace)
                    .withEmittedAt(emittedAt.toEpochMilli())
                    .withData(data)

            return AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(airbyteRecordMessage)
        }

        @JvmStatic
        fun addCdcMetadata(
            baseNode: ObjectNode,
            source: JsonNode,
            cdcMetadataInjector: CdcMetadataInjector<*>,
            isDelete: Boolean
        ): JsonNode {
            val transactionMillis = source["ts_ms"].asLong()
            val transactionTimestamp = Instant.ofEpochMilli(transactionMillis).toString()

            baseNode.put(CDC_UPDATED_AT, transactionTimestamp)
            cdcMetadataInjector.addMetaData(baseNode, source)

            if (isDelete) {
                baseNode.put(CDC_DELETED_AT, transactionTimestamp)
            } else {
                baseNode.put(CDC_DELETED_AT, null as String?)
            }

            return baseNode
        }

        const val CDC_LSN: String = "_ab_cdc_lsn"
        const val CDC_UPDATED_AT: String = "_ab_cdc_updated_at"
        const val CDC_DELETED_AT: String = "_ab_cdc_deleted_at"
        const val AFTER_EVENT: String = "after"
        const val BEFORE_EVENT: String = "before"
        const val OPERATION_FIELD: String = "op"
        const val SOURCE_EVENT: String = "source"
    }
}
