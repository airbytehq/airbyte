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
        get() =
            event
                .key()
                ?.let { Jsons.deserialize(it) }
                .also { it ?: LOGGER.warn { "Event key is null $event" } }
    val eventValueAsJson: JsonNode?
        get() =
            event
                .value()
                ?.let { Jsons.deserialize(it) }
                .also { it ?: LOGGER.warn { "Event value is null $event" } }

    val snapshotMetadata: SnapshotMetadata?
        get() {
            val metadataKey = eventValueAsJson?.get("source")?.get("snapshot")?.asText()
            return metadataKey?.let { SnapshotMetadata.fromString(metadataKey) }
        }

    val isSnapshotEvent: Boolean
        get() = SnapshotMetadata.isSnapshotEventMetadata(snapshotMetadata)
}
