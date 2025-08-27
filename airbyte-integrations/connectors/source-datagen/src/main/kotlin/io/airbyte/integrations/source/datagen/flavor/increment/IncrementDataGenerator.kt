package io.airbyte.integrations.source.datagen.flavor.increment

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.datagen.flavor.DataGenerator
import io.airbyte.protocol.models.v0.AirbyteRecordMessage

class IncrementDataGenerator: DataGenerator {
    private var currentID = 0

    override fun generateData(tableName: String): AirbyteRecordMessage {
        val incrementedID = ++currentID
        val recordData = mapOf("id" to incrementedID)

        return AirbyteRecordMessage()
            .withStream(tableName)
            .withData(Jsons.convertValue(recordData, JsonNode::class.java))
            .withEmittedAt(System.currentTimeMillis()) // TODO: fix this
    }
}
