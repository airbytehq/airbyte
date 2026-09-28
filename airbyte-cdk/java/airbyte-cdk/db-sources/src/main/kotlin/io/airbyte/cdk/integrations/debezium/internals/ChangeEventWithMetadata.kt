/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import io.debezium.engine.ChangeEvent
import io.github.oshai.kotlinlogging.KotlinLogging

private val LOGGER = KotlinLogging.logger {}

class ChangeEventWithMetadata(private val event: ChangeEvent<String?, String?>) {
    // Parsed lazily and then cached. These were previously uncached `get()` accessors, which meant
    // the value was re-deserialized on every read - six times per event on the MongoDB path
    // (isEventTypeHandled, isSnapshotEvent, CdcTargetPosition.reachedTargetPosition's three reads,
    // and the event converter). For multi-hundred-KB documents that is several MB of throwaway
    // JsonNode tree per read. Caching does not raise peak memory: DebeziumRecordIterator produces
    // exactly one ChangeEventWithMetadata per computeNext() and nothing downstream retains it, so
    // at most one parsed tree is live either way - it just allocates one instead of six.
    val eventKeyAsJson: JsonNode? by lazy {
        event
            .key()
            ?.let { Jsons.deserialize(it) }
            .also { it ?: LOGGER.warn { "Event key is null $event" } }
    }

    val eventValueAsJson: JsonNode? by lazy {
        event
            .value()
            ?.let { Jsons.deserialize(it) }
            .also { it ?: LOGGER.warn { "Event value is null $event" } }
    }

    val snapshotMetadata: SnapshotMetadata?
        get() {
            val metadataKey = eventValueAsJson?.get("source")?.get("snapshot")?.asText()
            return metadataKey?.let { SnapshotMetadata.fromString(metadataKey) }
        }

    val isSnapshotEvent: Boolean
        get() = SnapshotMetadata.isSnapshotEventMetadata(snapshotMetadata)
}
