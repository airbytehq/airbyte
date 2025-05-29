/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.read.DebeziumEventConverter
import io.airbyte.cdk.read.DebeziumRecord
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.time.Instant

@Singleton
@Primary
class MySqlDebeziumEventConverter : DebeziumEventConverter {
    override fun toAirbyteMessage(record: DebeziumRecord): AirbyteMessage {
        val before: JsonNode = record.before()
        val after: JsonNode = record.after()
        val source: JsonNode = record.source()

        // Value of before and after may be a null or a NullNode object,
        // representing a "null" in json
        val baseNode: ObjectNode
        if (after.isNull) {
            baseNode = before as ObjectNode
        } else {
            baseNode = after as ObjectNode
        }

        val data: JsonNode =
            DebeziumEventConverter.Companion.addCdcMetadata(baseNode, source, after.isNull == true)
        return DebeziumEventConverter.Companion.buildAirbyteMessage(
            source,
            Instant.now(), // TODO: change this
            data
        )
    }
}
