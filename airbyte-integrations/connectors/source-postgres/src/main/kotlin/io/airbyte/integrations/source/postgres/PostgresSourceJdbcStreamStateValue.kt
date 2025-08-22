package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.util.Jsons

data class PostgresSourceJdbcStreamStateValue(
    @JsonProperty("version") val version: Int = 2,
    @JsonProperty("state_type") val stateType: String = StateType.CURSOR_BASED.serialized,
    @JsonProperty("stream_name") val streamName: String = "",
    @JsonProperty("stream_namespace") val streamNamespace: String = "",
    @JsonProperty("ctid") val ctid: String? = null,
    @JsonProperty("incremental_state") val incrementalState: JsonNode? = null,
    @JsonProperty("cursors") val cursors: Map<String, JsonNode> = mapOf(),
) {
    companion object {
        val snapshotCompleted: OpaqueStateValue
            get() = Jsons.valueToTree(
                PostgresSourceJdbcStreamStateValue(
                    stateType = StateType.CTID_BASED.serialized,
                )
            )

        fun snapshotCheckpoint(
            ctidCheckpoint: JsonNode
        ) : OpaqueStateValue =
            Jsons.valueToTree(
                PostgresSourceJdbcStreamStateValue(
                    ctid = ctidCheckpoint.asText(),
                    stateType = StateType.CTID_BASED.serialized,
                )
            )

        fun cursorIncrementalCheckpoint(
            cursor: Field,
            cursorCheckpoint: JsonNode,
        ): OpaqueStateValue =
            when (cursorCheckpoint.isNull) {
                true -> Jsons.nullNode()
                false -> Jsons.valueToTree(PostgresSourceJdbcStreamStateValue(
                    cursors = mapOf(cursor.id to cursorCheckpoint)
                ))
            }

        fun snapshotWithCursorCheckpoint(
            ctidCheckpoint: JsonNode,
            cursor: Field,
            cursorCheckpoint: JsonNode,
        ): OpaqueStateValue =
            Jsons.valueToTree(PostgresSourceJdbcStreamStateValue(
                ctid = ctidCheckpoint.asText(),
                cursors = mapOf(cursor.id to cursorCheckpoint),
            ))
    }
}


enum class StateType {
    CTID_BASED,
    CURSOR_BASED,
    ;

    val serialized: String = name.lowercase()
}

