package io.airbyte.integrations.source.datagen.flavor.increment

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.datagen.flavor.DataGenerator
import io.airbyte.integrations.source.datagen.flavor.increment.IncrementFlavor.incrementTableName
import io.airbyte.protocol.models.v0.AirbyteRecordMessage

class IncrementDataGenerator: DataGenerator {
    private var currentID = 0

    override fun generateData(): AirbyteRecordMessage {
        val incrementedID = ++currentID
        val recordData = ObjectMapper().createObjectNode().put("id", incrementedID)

        return AirbyteRecordMessage()
            .withStream(incrementTableName)
            .withData(recordData)
            .withEmittedAt(System.currentTimeMillis()) // TODO: fix this
    }
}
