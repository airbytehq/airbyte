/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode

/** [Record] wraps a Debezium change data event. */
data class DebeziumRecord(val debeziumEventValue: JsonNode) {

    /** True if this is a Debezium heartbeat event. These aren't passed to [DebeziumConsumer]. */
    val isHeartbeat: Boolean
        get() = source().isNull

    /** The datum prior to this event; null for insertions. */
    fun before(): JsonNode {
        return element("before")
    }

    /** The datum following this event; null for deletions. */
    fun after(): JsonNode {
        return element("after")
    }

    /** Metadata containing transaction IDs, LSNs, etc; null for heartbeats. */
    fun source(): JsonNode {
        return element("source")
    }

    /** Convenience function for accessing child object nodes of the debezium event root node. */
    fun element(fieldName: String?): JsonNode {
        if (!debeziumEventValue.has(fieldName)) {
            return NullNode.getInstance()
        }
        return debeziumEventValue[fieldName]
    }
}
