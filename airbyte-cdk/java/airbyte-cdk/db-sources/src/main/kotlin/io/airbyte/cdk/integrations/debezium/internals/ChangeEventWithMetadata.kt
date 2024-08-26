/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import io.debezium.engine.ChangeEvent
import io.github.oshai.kotlinlogging.KotlinLogging

private val LOGGER = KotlinLogging.logger {}

class ChangeEventWithMetadata(private val event: ChangeEvent<String?, String?>) {
    val eventKeyAsJson: JsonNode?
        get() {
            if (event.key() == null) {
                LOGGER.warn { "Event key is null $event" }
                return null
            }
            return Jsons.deserialize(event.key())
        }
    val eventValueAsJson: JsonNode?
        get() {
            if (event.value() == null) {
                LOGGER.warn { "Event value is null $event" }
                return null
            }
            return Jsons.deserialize(event.value())
        }
    val snapshotMetadata: SnapshotMetadata?
        get() {
            val metadataKey = eventValueAsJson?.get("source")?.get("snapshot")?.asText()
            return metadataKey?.let { return SnapshotMetadata.fromString(metadataKey) }
        }

    fun event(): ChangeEvent<String?, String?> {
        return event
    }


    val isSnapshotEvent: Boolean
        get() = SnapshotMetadata.isSnapshotEventMetadata(snapshotMetadata)
}
