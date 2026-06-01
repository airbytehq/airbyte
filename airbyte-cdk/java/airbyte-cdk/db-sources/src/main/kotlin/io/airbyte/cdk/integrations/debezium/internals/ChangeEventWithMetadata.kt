/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.core.exc.StreamConstraintsException
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
                ?.let { parseDebeziumPayload(it, "key") }
                .also { it ?: LOGGER.warn { "Event key is null $event" } }
    val eventValueAsJson: JsonNode?
        get() =
            event
                .value()
                ?.let { parseDebeziumPayload(it, "value") }
                .also { it ?: LOGGER.warn { "Event value is null $event" } }

    val snapshotMetadata: SnapshotMetadata?
        get() {
            val metadataKey = eventValueAsJson?.get("source")?.get("snapshot")?.asText()
            return metadataKey?.let { SnapshotMetadata.fromString(metadataKey) }
        }

    val isSnapshotEvent: Boolean
        get() = SnapshotMetadata.isSnapshotEventMetadata(snapshotMetadata)

    companion object {
        /**
         * Deserialize a Debezium change event payload (key or value), translating Jackson
         * stream-constraint failures into a runtime exception with an actionable message that does
         * not leak Jackson internals. The wrapping is defensive: the global [Jsons] mapper already
         * allows arbitrarily large strings, so this branch should not fire under normal operation.
         * Other Jackson parse failures bubble up unchanged.
         *
         * @param parser exposed for unit tests so the wrapping behavior can be exercised without
         * producing a multi-gigabyte input.
         */
        @JvmStatic
        internal fun parseDebeziumPayload(
            raw: String,
            payloadPart: String,
            parser: (String) -> JsonNode = Jsons::deserialize,
        ): JsonNode {
            try {
                return parser(raw)
            } catch (e: Exception) {
                if (hasStreamConstraintsCause(e)) {
                    throw RuntimeException(
                        "A CDC event payload exceeds the connector's per-row deserialization " +
                            "limit. Reduce the column size in the source row or exclude the row " +
                            "from CDC replication. " +
                            "Debezium event part: $payloadPart, raw size: ${raw.length} bytes.",
                        e,
                    )
                }
                throw e
            }
        }

        private fun hasStreamConstraintsCause(t: Throwable): Boolean {
            var current: Throwable? = t
            val seen = HashSet<Throwable>()
            while (current != null && seen.add(current)) {
                if (current is StreamConstraintsException) {
                    return true
                }
                current = current.cause
            }
            return false
        }
    }
}
