/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sap_hana

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.util.Jsons

class SapHanaSourceJdbcStreamStateValue(
    @JsonProperty("primary_key") val primaryKey: Map<String, JsonNode> = mapOf(),
    @JsonProperty("cursors") val cursors: Map<String, JsonNode> = mapOf(),
) {
    companion object {
        /** Empty json representing the completion of a FULL_REFRESH snapshot. */
        val snapshotCompleted: OpaqueStateValue
            get() = Jsons.valueToTree(SapHanaSourceJdbcStreamStateValue())

        /** Value representing the progress of an ongoing snapshot not involving cursor columns. */
        fun snapshotCheckpoint(
            primaryKey: List<Field>,
            primaryKeyCheckpoint: List<JsonNode>,
        ): OpaqueStateValue =
            Jsons.valueToTree(
                SapHanaSourceJdbcStreamStateValue(
                    primaryKey = primaryKey.map { it.id }.zip(primaryKeyCheckpoint).toMap(),
                )
            )

        /** Value representing the progress of an ongoing snapshot involving cursor columns. */
        fun snapshotWithCursorCheckpoint(
            primaryKey: List<Field>,
            primaryKeyCheckpoint: List<JsonNode>,
            cursor: Field,
            cursorUpperBound: JsonNode,
        ): OpaqueStateValue =
            Jsons.valueToTree(
                SapHanaSourceJdbcStreamStateValue(
                    primaryKey = primaryKey.map { it.id }.zip(primaryKeyCheckpoint).toMap(),
                    cursors = mapOf(cursor.id to cursorUpperBound),
                )
            )

        /** Value representing the progress of an ongoing incremental cursor read. */
        fun cursorIncrementalCheckpoint(
            cursor: Field,
            cursorCheckpoint: JsonNode,
        ): OpaqueStateValue =
            Jsons.valueToTree(
                SapHanaSourceJdbcStreamStateValue(
                    cursors = mapOf(cursor.id to cursorCheckpoint),
                )
            )
    }
}
