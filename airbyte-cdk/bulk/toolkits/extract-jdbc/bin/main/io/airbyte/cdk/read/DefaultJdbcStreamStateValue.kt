/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.util.Jsons

/**
 * [DefaultJdbcStreamStateValue] is used by [DefaultJdbcPartitionFactory] for deserializing an
 * [OpaqueStateValue] into a [DefaultJdbcPartition]. The latter is able to, in turn, serialize a
 * partition boundary into an [OpaqueStateValue] with [DefaultJdbcStreamStateValue].
 */
data class DefaultJdbcStreamStateValue(
    @JsonProperty("primary_key") val primaryKey: Map<String, JsonNode> = mapOf(),
    @JsonProperty("cursors") val cursors: Map<String, JsonNode> = mapOf(),
) {
    companion object {
        /** Value representing the completion of a FULL_REFRESH snapshot. */
        val snapshotCompleted: OpaqueStateValue
            get() = Jsons.valueToTree(DefaultJdbcStreamStateValue())

        /** Value representing the progress of a ongoing snapshot not involving cursor columns. */
        fun snapshotCheckpoint(
            primaryKey: List<Field>,
            primaryKeyCheckpoint: List<JsonNode>,
        ): OpaqueStateValue =
            when (primaryKeyCheckpoint.first().isNull) {
                true -> Jsons.nullNode()
                false ->
                    Jsons.valueToTree(
                        DefaultJdbcStreamStateValue(
                            primaryKey = primaryKey.map { it.id }.zip(primaryKeyCheckpoint).toMap(),
                        )
                    )
            }

        /** Value representing the progress of an ongoing snapshot involving cursor columns. */
        fun snapshotWithCursorCheckpoint(
            primaryKey: List<Field>,
            primaryKeyCheckpoint: List<JsonNode>,
            cursor: Field,
            cursorUpperBound: JsonNode,
        ): OpaqueStateValue =
            when (primaryKeyCheckpoint.first().isNull) {
                true -> Jsons.nullNode()
                false ->
                    Jsons.valueToTree(
                        DefaultJdbcStreamStateValue(
                            primaryKey = primaryKey.map { it.id }.zip(primaryKeyCheckpoint).toMap(),
                            cursors = mapOf(cursor.id to cursorUpperBound),
                        )
                    )
            }

        /** Value representing the progress of an ongoing incremental cursor read. */
        fun cursorIncrementalCheckpoint(
            cursor: Field,
            cursorCheckpoint: JsonNode,
        ): OpaqueStateValue =
            when (cursorCheckpoint.isNull) {
                true -> Jsons.nullNode()
                false ->
                    Jsons.valueToTree(
                        DefaultJdbcStreamStateValue(
                            cursors = mapOf(cursor.id to cursorCheckpoint),
                        )
                    )
            }
    }
}
