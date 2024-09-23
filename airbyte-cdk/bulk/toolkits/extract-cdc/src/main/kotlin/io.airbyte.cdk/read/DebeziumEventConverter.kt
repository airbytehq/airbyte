/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.time.Instant

/*
 * Encapsulates logic for converting a debezium record into an Airbyte message.
 */
interface DebeziumEventConverter {
    fun toAirbyteMessage(record: DebeziumRecord): AirbyteMessage

    companion object {
        @JvmStatic
        fun buildAirbyteMessage(
            source: JsonNode?,
            emittedAt: Instant,
            data: JsonNode?
        ): AirbyteMessage {
            val streamNamespace = source?.get("db")?.asText()
            val streamName = source?.get("table")?.asText()

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
        fun addCdcMetadata(baseNode: ObjectNode, source: JsonNode, isDelete: Boolean): JsonNode {
            val transactionMillis = source["ts_ms"].asLong()
            val transactionTimestamp = Instant.ofEpochMilli(transactionMillis).toString()

            baseNode.put(CDC_UPDATED_AT, transactionTimestamp)

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

@Singleton
@Secondary
class NoOpDebeziumEventConverted : DebeziumEventConverter {
    override fun toAirbyteMessage(record: DebeziumRecord): AirbyteMessage {
        TODO("Not yet implemented")
    }
}
