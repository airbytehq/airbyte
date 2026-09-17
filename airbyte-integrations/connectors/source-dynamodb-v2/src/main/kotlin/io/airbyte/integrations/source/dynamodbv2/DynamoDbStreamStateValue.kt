/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons

/**
 * The state of a stream, i.e. the `stream_state` of its STREAM state message.
 *
 * The shape is backward compatible with the legacy `source-dynamodb` connector, whose state was the
 * legacy Java CDK's `DbStreamState`: `cursor_field`, `cursor` and `cursor_record_count` are read as
 * they are (`stream_name` and `stream_namespace` are ignored), and the state emitted when an
 * incremental scan completes has exactly that shape, so a legacy connection resumes without a reset
 * and a downgrade keeps working.
 *
 * Two properties are new:
 * - [scan] is present while a table scan is in progress and is the point to resume it from: the
 * DynamoDB `LastEvaluatedKey` of the last page read, and, for an incremental stream, the highest
 * cursor value seen so far in this scan. [cursor] then still holds the lower bound the scan filters
 * on, so that an interrupted incremental scan resumes with the same filter;
 * - [scanComplete] marks a finished full refresh (the legacy connector emitted no state at all for
 * full refresh streams). The platform clears it after a successful sync; when it is passed back,
 * i.e. after a failed attempt in which this stream completed, the stream is not read again.
 */
@JsonIgnoreProperties(ignoreUnknown = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
data class DynamoDbStreamStateValue(
    @JsonProperty("cursor_field") val cursorField: List<String>? = null,
    @JsonProperty("cursor") val cursor: String? = null,
    @JsonProperty("cursor_record_count") val cursorRecordCount: Long? = null,
    @JsonProperty("scan") val scan: ScanProgress? = null,
    @JsonProperty("scan_complete") val scanComplete: Boolean? = null,
) {
    /** Where an in-progress scan stopped. */
    @JsonIgnoreProperties(ignoreUnknown = true)
    @JsonInclude(JsonInclude.Include.NON_NULL)
    data class ScanProgress(
        /** DynamoDB JSON of the `LastEvaluatedKey`, to pass back as `ExclusiveStartKey`. */
        @JsonProperty("exclusive_start_key") val exclusiveStartKey: ObjectNode,
        /** Highest cursor value seen in this scan, as text (incremental streams only). */
        @JsonProperty("max_cursor") val maxCursor: String? = null,
        /** Number of records seen with [maxCursor] (incremental streams only). */
        @JsonProperty("max_cursor_record_count") val maxCursorRecordCount: Long? = null,
    )

    /**
     * Serialized through text so that the tree uses the same node types as a parsed state (an
     * `IntNode` for a small count, not a `LongNode`), which keeps state values comparable.
     */
    fun toOpaqueStateValue(): OpaqueStateValue = Jsons.readTree(Jsons.writeValueAsString(this))

    companion object {
        /** State of a full refresh stream that has been read to the end. */
        val FULL_REFRESH_COMPLETE = DynamoDbStreamStateValue(scanComplete = true)

        /**
         * Parses a saved state; null when there is none. A state that cannot be parsed is a
         * configuration error: the user has to reset the stream.
         */
        fun parse(
            streamID: StreamIdentifier,
            opaqueStateValue: OpaqueStateValue?,
        ): DynamoDbStreamStateValue? {
            if (opaqueStateValue == null || opaqueStateValue.isNull) {
                return null
            }
            try {
                return Jsons.treeToValue(opaqueStateValue, DynamoDbStreamStateValue::class.java)
            } catch (e: Exception) {
                throw ConfigErrorException(
                    "The saved state of stream '$streamID' could not be read: ${e.message}. " +
                        "Clear the connection's data to reset the stream and retry.",
                    e,
                )
            }
        }
    }
}
