/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.DataField
import io.airbyte.cdk.util.Jsons

data class PostgresSourceJdbcStreamStateValue(
    @JsonProperty("version") val version: Int = 3,
    @JsonProperty("state_type") val stateType: String = StateType.CURSOR_BASED.serialized,
    @JsonProperty("stream_name") val streamName: String = "",
    @JsonProperty("stream_namespace") val streamNamespace: String = "",
    @JsonProperty("ctid") val ctid: String? = null,
    @JsonProperty("cursors") val cursors: Map<String, JsonNode> = mapOf(),
    @JsonProperty("relation_filenode") val filenode: Filenode? = null,
    @JsonProperty("xmin") val xmin: JsonNode? = null,
) {
    companion object {
        val snapshotCompleted: OpaqueStateValue
            get() =
                Jsons.valueToTree(
                    PostgresSourceJdbcStreamStateValue(
                        stateType = StateType.CTID_BASED.serialized,
                    )
                )

        fun snapshotCheckpoint(
            ctidCheckpoint: JsonNode,
            filenode: Filenode?,
        ): OpaqueStateValue =
            Jsons.valueToTree(
                PostgresSourceJdbcStreamStateValue(
                    ctid = ctidCheckpoint.asText(),
                    filenode = filenode,
                    stateType = StateType.CTID_BASED.serialized,
                )
            )

        fun cursorIncrementalCheckpoint(
            cursor: DataField,
            cursorCheckpoint: JsonNode,
        ): OpaqueStateValue =
            when (cursorCheckpoint.isNull) {
                true -> Jsons.nullNode()
                false ->
                    Jsons.valueToTree(
                        PostgresSourceJdbcStreamStateValue(
                            cursors = mapOf(cursor.id to cursorCheckpoint),
                        )
                    )
            }

        fun xminIncrementalCheckpoint(
            xminCheckpoint: JsonNode,
        ): OpaqueStateValue =
            when (xminCheckpoint.isNull) {
                true -> Jsons.nullNode()
                false ->
                    Jsons.valueToTree(
                        PostgresSourceJdbcStreamStateValue(
                            stateType = StateType.XMIN_BASED.serialized,
                            xmin = xminCheckpoint
                        )
                    )
            }

        fun snapshotWithCursorCheckpoint(
            ctidCheckpoint: JsonNode,
            cursor: DataField,
            cursorCheckpoint: JsonNode,
            filenode: Filenode?,
        ): OpaqueStateValue =
            Jsons.valueToTree(
                PostgresSourceJdbcStreamStateValue(
                    ctid = ctidCheckpoint.asText(),
                    cursors = mapOf(cursor.id to cursorCheckpoint),
                    filenode = filenode,
                    stateType = StateType.CTID_BASED.serialized,
                )
            )

        fun snapshotWithXminCheckpoint(
            ctidCheckpoint: JsonNode,
            xminCheckpoint: JsonNode,
            filenode: Filenode?,
        ): OpaqueStateValue =
            Jsons.valueToTree(
                PostgresSourceJdbcStreamStateValue(
                    ctid = ctidCheckpoint.asText(),
                    xmin = xminCheckpoint,
                    filenode = filenode,
                    stateType = StateType.CTID_BASED.serialized,
                )
            )
    }
}

enum class StateType {
    CTID_BASED,
    CURSOR_BASED,
    XMIN_BASED,
    ;

    val serialized: String = name.lowercase()
}
