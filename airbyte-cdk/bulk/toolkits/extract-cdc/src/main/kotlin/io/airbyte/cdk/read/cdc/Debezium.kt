/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import io.debezium.relational.history.HistoryRecord

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

    /** True if this is a Debezium heartbeat event. These aren't passed to [DebeziumConsumer]. */
    val isHeartbeat: Boolean
        get() = source.isNull

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
