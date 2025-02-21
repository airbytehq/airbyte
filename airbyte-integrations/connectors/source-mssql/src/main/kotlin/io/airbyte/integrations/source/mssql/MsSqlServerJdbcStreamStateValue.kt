/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

data class MsSqlServerJdbcStreamStateValue(
    @JsonProperty("cursor") val cursors: String = "",
    @JsonProperty("version") val version: Int = 2,
    @JsonProperty("state_type") val stateType: String = StateType.CURSOR_BASED.stateType,
    @JsonProperty("stream_name") val streamName: String = "",
    @JsonProperty("cursor_field") val cursorField: List<String> = listOf(),
    @JsonProperty("stream_namespace") val streamNamespace: String = "",
    @JsonProperty("cursor_record_count") val cursorRecordCount: Int = 0,
    @JsonProperty("pk_name") val pkName: String? = null,
    @JsonProperty("pk_val") val pkValue: String? = null,
    @JsonProperty("incremental_state") val incrementalState: JsonNode? = null,
) {
    companion object {
        /** Value representing the completion of a FULL_REFRESH snapshot. */
        val snapshotCompleted: OpaqueStateValue
            get() = Jsons.valueToTree(MsSqlServerJdbcStreamStateValue(stateType = "primary_key"))

        /** Value representing the progress of an ongoing incremental cursor read. */
        fun cursorIncrementalCheckpoint(
            cursor: Field,
            cursorCheckpoint: JsonNode,
            stream: Stream,
        ): OpaqueStateValue {
            return Jsons.valueToTree(
                MsSqlServerJdbcStreamStateValue(
                    cursorField = listOf(cursor.id),
                    cursors = cursorCheckpoint.asText(),
                    streamName = stream.name,
                    streamNamespace = stream.namespace!!
                )
            )
        }

        /** Value representing the progress of an ongoing snapshot not involving cursor columns. */
        fun snapshotCheckpoint(
            primaryKey: List<Field>,
            primaryKeyCheckpoint: List<JsonNode>,
        ): OpaqueStateValue {
            val primaryKeyField = primaryKey.first()
            return Jsons.valueToTree(
                MsSqlServerJdbcStreamStateValue(
                    pkName = primaryKeyField.id,
                    pkValue = primaryKeyCheckpoint.first().asText(),
                    stateType = StateType.PRIMARY_KEY.stateType,
                )
            )
        }

        /** Value representing the progress of an ongoing snapshot involving cursor columns. */
        fun snapshotWithCursorCheckpoint(
            primaryKey: List<Field>,
            primaryKeyCheckpoint: List<JsonNode>,
            cursor: Field,
            stream: Stream
        ): OpaqueStateValue {
            val primaryKeyField = primaryKey.first()
            return Jsons.valueToTree(
                MsSqlServerJdbcStreamStateValue(
                    pkName = primaryKeyField.id,
                    pkValue = primaryKeyCheckpoint.first().asText(),
                    stateType = StateType.PRIMARY_KEY.stateType,
                    incrementalState =
                        Jsons.valueToTree(
                            MsSqlServerJdbcStreamStateValue(
                                cursorField = listOf(cursor.id),
                                streamName = stream.name,
                                streamNamespace = stream.namespace!!
                            )
                        ),
                )
            )
        }
    }
}

enum class StateType(val stateType: String) {
    PRIMARY_KEY("primary_key"),
    CURSOR_BASED("cursor_based"),
}
