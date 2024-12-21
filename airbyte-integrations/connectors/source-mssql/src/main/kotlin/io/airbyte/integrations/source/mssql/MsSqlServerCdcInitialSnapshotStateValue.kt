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

data class MsSqlServerCdcInitialSnapshotStateValue(
    @JsonProperty("pk_val") val pkVal: String? = null,
    @JsonProperty("pk_name") val pkName: String? = null,
    @JsonProperty("version") val version: Int? = null,
    @JsonProperty("state_type") val stateType: String? = null,
    @JsonProperty("incremental_state") val incrementalState: JsonNode? = null,
    @JsonProperty("stream_name") val streamName: String? = null,
    @JsonProperty("cursor_field") val cursorField: List<String>? = null,
    @JsonProperty("stream_namespace") val streamNamespace: String? = null,
) {
    companion object {
        /** Value representing the completion of a FULL_REFRESH snapshot. */
        fun getSnapshotCompletedState(stream: Stream): OpaqueStateValue =
            Jsons.valueToTree(
                MsSqlServerCdcInitialSnapshotStateValue(
                    streamName = stream.name,
                    cursorField = listOf(),
                    streamNamespace = stream.namespace
                )
            )

        /** Value representing the progress of an ongoing snapshot. */
        fun snapshotCheckpoint(
            primaryKey: List<Field>,
            primaryKeyCheckpoint: List<JsonNode>,
        ): OpaqueStateValue {
            val primaryKeyField = primaryKey.first()
            return Jsons.valueToTree(
                MsSqlServerCdcInitialSnapshotStateValue(
                    pkName = primaryKeyField.id,
                    pkVal = primaryKeyCheckpoint.first().asText(),
                    stateType = "primary_key",
                )
            )
        }
    }
}
