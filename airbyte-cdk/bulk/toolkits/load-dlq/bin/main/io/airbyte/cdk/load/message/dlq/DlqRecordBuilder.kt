/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message.dlq

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueToProtobuf
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordSource
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.UUID

/**
 * A helper method to modify a existing DestinationRecordRaw for a dead letter queue.
 *
 * If [keepOriginalFields] is true, the data will be appended to the data blob. Otherwise, the data
 * will replace the entire data blob of the record.
 *
 * This method ensures we still track the correct metadata against the original record when it comes
 * to stats and checkpointing while allowing a different content to be persisted to the dead letter
 * queue.
 */
fun DestinationRecordRaw.toDlqRecord(
    data: Map<String, Any>,
    keepOriginalFields: Boolean = true,
): DestinationRecordRaw =
    // We want to preserve everything from the original record and only override the content.
    // The rationale is that we should still be reporting original byte size and adhere to the
    // original checkpoint.
    copy(
        rawData =
            if (keepOriginalFields) merge(this.rawData, data)
            else DestinationRecordJsonSource(data.toAirbyteRecordMessage()),
    )

private fun merge(raw: DestinationRecordSource, data: Map<String, Any>): DestinationRecordSource {
    when (raw) {
        is DestinationRecordJsonSource -> {
            val objectNode = raw.source.record.data as ObjectNode
            data.forEach { (k, v) ->
                objectNode.set<JsonNode>(k, Jsons.convertValue(v, JsonNode::class.java))
            }
        }
        is DestinationRecordProtobufSource -> {
            data.forEach { (_, v) ->
                val airbyteVal = AirbyteValue.from(v)
                raw.source.record.dataList.add(
                    AirbyteValueToProtobuf().toProtobuf(airbyteVal, airbyteVal.airbyteType)
                )
            }
        }
    }
    return raw
}

/**
 * A helper method to generate a new DestinationRecordRaw for a dead letter queue.
 *
 * This method will generate the rawData from [data] and fill in reasonable defaults.
 */
fun DestinationStream.newDlqRecord(data: Map<String, Any>): DestinationRecordRaw =
    DestinationRecordRaw(
        stream = this,
        rawData = DestinationRecordJsonSource(data.toAirbyteRecordMessage()),
        // We should be reporting the original record so in this flow, do not fill in anything.
        serializedSizeBytes = 0,
        checkpointId = null,
        airbyteRawId = UUID.randomUUID(),
    )

private fun Map<String, Any>.toAirbyteRecordMessage() =
    AirbyteMessage()
        .withRecord(
            AirbyteRecordMessage()
                .withData(Jsons.convertValue(this, JsonNode::class.java))
                .withEmittedAt(System.currentTimeMillis())
        )
        .withType(AirbyteMessage.Type.RECORD)
