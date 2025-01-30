/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import io.airbyte.cdk.util.Jsons
import io.debezium.embedded.EmbeddedEngineChangeEvent
import io.debezium.engine.ChangeEvent
import io.debezium.relational.history.HistoryRecord
import org.apache.kafka.connect.source.SourceRecord

/** Convenience wrapper around [ChangeEvent]. */
class DebeziumEvent(event: ChangeEvent<String?, String?>) {

    /** This [SourceRecord] object is the preferred way to obtain the current position. */
    val sourceRecord: SourceRecord? = (event as? EmbeddedEngineChangeEvent<*, *, *>)?.sourceRecord()

    val key: DebeziumRecordKey? =
        event
            .key()
            ?.let { runCatching { Jsons.readTree(it) }.getOrNull() }
            ?.let(::DebeziumRecordKey)

    val value: DebeziumRecordValue? =
        event
            .value()
            ?.let { runCatching { Jsons.readTree(it) }.getOrNull() }
            ?.let(::DebeziumRecordValue)

    /**
     * Debezium can output a tombstone event that has a value of null. This is an artifact of how it
     * interacts with kafka. We want to ignore it. More on the tombstone:
     * https://debezium.io/documentation/reference/stable/transformations/event-flattening.html
     */
    val isTombstone: Boolean = event.value() == null

    /**
     * True if this is a Debezium heartbeat event, or the equivalent thereof. In any case, such
     * events are only used for their position value and for triggering timeouts.
     */
    val isHeartbeat: Boolean = value?.source?.isNull == true
}

/** [DebeziumRecordKey] wraps a Debezium change data event key. */
@JvmInline
value class DebeziumRecordKey(val wrapped: JsonNode) {

    /** Convenience function for accessing child object nodes of the debezium event root node. */
    fun element(fieldName: String): JsonNode {
        if (!wrapped.has(fieldName)) {
            return NullNode.getInstance()
        }
        return wrapped[fieldName]
    }
}

/** [DebeziumRecordValue] wraps a Debezium change data event value. */
@JvmInline
value class DebeziumRecordValue(val wrapped: JsonNode) {

    /** The datum prior to this event; null for insertions. */
    val before: JsonNode
        get() = element("before")

    /** The datum following this event; null for deletions. */
    val after: JsonNode
        get() = element("after")

    /** Metadata containing transaction IDs, LSNs, etc; null for heartbeats. */
    val source: JsonNode
        get() = element("source")

    val operation: String?
        get() = element("op").takeUnless { it.isNull }?.asText()

    /** Convenience function for accessing child object nodes of the debezium event root node. */
    fun element(fieldName: String): JsonNode {
        if (!wrapped.has(fieldName)) {
            return NullNode.getInstance()
        }
        return wrapped[fieldName]
    }
}

/** Debezium Engine input. */
data class DebeziumInput(
    val properties: Map<String, String>,
    val state: DebeziumState,
    val isSynthetic: Boolean,
)

/** Debezium Engine output, other than records of course. */
data class DebeziumState(
    val offset: DebeziumOffset,
    val schemaHistory: DebeziumSchemaHistory?,
)

/** [DebeziumOffset] wraps the contents of a Debezium offset file. */
@JvmInline value class DebeziumOffset(val wrapped: Map<JsonNode, JsonNode>)

/** [DebeziumSchemaHistory] wraps the contents of a Debezium schema history file. */
@JvmInline value class DebeziumSchemaHistory(val wrapped: List<HistoryRecord>)
