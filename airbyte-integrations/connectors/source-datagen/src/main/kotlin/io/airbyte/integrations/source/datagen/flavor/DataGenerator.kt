package io.airbyte.integrations.source.datagen.flavor

import io.airbyte.protocol.models.v0.AirbyteRecordMessage

interface DataGenerator {
    fun generateData(): AirbyteRecordMessage
    // TODO: add arguments, return statement
}
