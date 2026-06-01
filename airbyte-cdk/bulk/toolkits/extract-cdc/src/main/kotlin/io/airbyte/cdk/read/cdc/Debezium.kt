/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import com.fasterxml.jackson.core.exc.StreamConstraintsException
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import io.airbyte.cdk.SystemErrorException
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
        event.key()?.let { readDebeziumPayload(it, "key") }?.let(::DebeziumRecordKey)

    val value: DebeziumRecordValue? =
        event.value()?.let { readDebeziumPayload(it, "value") }?.let(::DebeziumRecordValue)

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

/** Return type for [CdcPartitionsCreatorDebeziumOperations.deserializeState]. */
sealed interface DebeziumWarmStartState

data class ValidDebeziumWarmStartState(
    val offset: DebeziumOffset,
    val schemaHistory: DebeziumSchemaHistory?
) : DebeziumWarmStartState

sealed interface InvalidDebeziumWarmStartState : DebeziumWarmStartState

data class AbortDebeziumWarmStartState(val reason: String) : InvalidDebeziumWarmStartState

data class ResetDebeziumWarmStartState(val reason: String) : InvalidDebeziumWarmStartState

/** [DebeziumOffset] wraps the contents of a Debezium offset file. */
@JvmInline value class DebeziumOffset(val wrapped: Map<JsonNode, JsonNode>)

/** [DebeziumSchemaHistory] wraps the contents of a Debezium schema history file. */
@JvmInline value class DebeziumSchemaHistory(val wrapped: List<HistoryRecord>)

/**
 * Deserialize a Debezium change event payload (key or value), translating Jackson stream-constraint
 * failures into a [SystemErrorException] whose user-facing message names the connector-level limit
 * and the remediation, without leaking Jackson internals. Other parse failures fall through to the
 * existing null-event handling so a single malformed event does not abort the entire CDC stream.
 *
 * The wrapping is defensive: [Jsons] is configured with `maxStringLength = Int.MAX_VALUE`, so this
 * branch should not fire under normal operation.
 *
 * @param parser exposed for unit tests so the wrapping behavior can be exercised without producing
 * a multi-gigabyte input.
 */
internal fun readDebeziumPayload(
    raw: String,
    payloadPart: String,
    parser: (String) -> JsonNode = Jsons::readTree,
): JsonNode? {
    try {
        return parser(raw)
    } catch (e: Exception) {
        if (hasStreamConstraintsCause(e)) {
            throw SystemErrorException(
                "A CDC event payload exceeds the connector's per-row deserialization " +
                    "limit. Reduce the column size in the source row or exclude the row from " +
                    "CDC replication. " +
                    "Debezium event part: $payloadPart, raw size: ${raw.length} bytes.",
                e,
            )
        }
        return null
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
