/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

/** Represents the old OrderedColumnLoadStatus format used by the legacy MSSQL connector */
data class LegacyOrderedColumnLoadStatus(
    @JsonProperty("version") val version: Long? = null,
    @JsonProperty("state_type") val stateType: String? = null,
    @JsonProperty("ordered_col") val orderedCol: String? = null,
    @JsonProperty("ordered_col_val") val orderedColVal: String? = null,
    @JsonProperty("incremental_state") val incrementalState: JsonNode? = null,
)

/** Represents the old CursorBasedStatus format used by the legacy MSSQL connector */
data class LegacyCursorBasedStatus(
    @JsonProperty("version") val version: Long? = null,
    @JsonProperty("state_type") val stateType: String? = null,
    @JsonProperty("stream_name") val streamName: String? = null,
    @JsonProperty("stream_namespace") val streamNamespace: String? = null,
    @JsonProperty("cursor_field") val cursorField: List<String>? = null,
    @JsonProperty("cursor") val cursor: String? = null,
    @JsonProperty("cursor_record_count") val cursorRecordCount: Long? = null,
)

/** Helper class to migrate legacy MSSQL connector states to the new v2 format */
object MsSqlServerStateMigration {

    /** Parses state value and handles backward compatibility with legacy formats */
    fun parseStateValue(opaqueStateValue: OpaqueStateValue): MsSqlServerJdbcStreamStateValue {
        // Check version to detect legacy state using centralized version constants
        val version = opaqueStateValue.get("version")?.asInt()
        val isLegacy = MsSqlServerJdbcStreamStateValue.isLegacy(version)

        return if (isLegacy) {
            log.info {
                "Detected legacy state (version=$version), migrating to version ${MsSqlServerJdbcStreamStateValue.CURRENT_VERSION}"
            }
            migrateLegacyState(opaqueStateValue)
        } else {
            try {
                // Version 3+ states should parse directly
                Jsons.treeToValue(opaqueStateValue, MsSqlServerJdbcStreamStateValue::class.java)
            } catch (e: Exception) {
                throw IllegalStateException(
                    "Failed to parse state with version $version as MsSqlServerJdbcStreamStateValue.",
                    e
                )
            }
        }
    }

    /** Migrates legacy state formats to new MsSqlServerJdbcStreamStateValue format */
    private fun migrateLegacyState(
        opaqueStateValue: OpaqueStateValue
    ): MsSqlServerJdbcStreamStateValue {
        val stateType = opaqueStateValue.get("state_type")?.asText()

        return when (stateType) {
            "ordered_column" -> migrateOrderedColumnLoadStatus(opaqueStateValue)
            "cursor_based" -> migrateCursorBasedStatus(opaqueStateValue)
            else -> {
                // Try to detect format based on field presence
                when {
                    opaqueStateValue.has("ordered_col") ->
                        migrateOrderedColumnLoadStatus(opaqueStateValue)
                    opaqueStateValue.has("cursor_field") ->
                        migrateCursorBasedStatus(opaqueStateValue)
                    else -> {
                        log.warn {
                            "Unknown legacy state format, falling back to default: $opaqueStateValue"
                        }
                        MsSqlServerJdbcStreamStateValue()
                    }
                }
            }
        }
    }

    /** Migrates OrderedColumnLoadStatus (primary key based initial sync) to new format */
    private fun migrateOrderedColumnLoadStatus(
        opaqueStateValue: OpaqueStateValue
    ): MsSqlServerJdbcStreamStateValue {
        val legacy = Jsons.treeToValue(opaqueStateValue, LegacyOrderedColumnLoadStatus::class.java)

        log.info {
            "Migrating OrderedColumnLoadStatus state: ordered_col=${legacy.orderedCol}, ordered_col_val=${legacy.orderedColVal}"
        }

        // Extract incremental state if present and not null
        val incrementalState =
            legacy.incrementalState
                ?.takeIf { !it.isNull }
                ?.let { migrateCursorBasedStatusFromJson(it) }

        // Convert String to JsonNode, handling null and "null" string
        val pkValueNode: JsonNode? =
            legacy.orderedColVal?.let { value ->
                when {
                    value.isEmpty() || value == "null" -> null
                    else -> Jsons.valueToTree<JsonNode>(value)
                }
            }

        return MsSqlServerJdbcStreamStateValue(
            version = MsSqlServerJdbcStreamStateValue.CURRENT_VERSION,
            stateType =
                StateType.PRIMARY_KEY.stateType, // Convert "ordered_column" to "primary_key"
            pkName = legacy.orderedCol,
            pkValue = pkValueNode,
            // If there's incremental state, embed it for transition after initial sync completes
            incrementalState = incrementalState?.let { Jsons.valueToTree(it) }
        )
    }

    /** Migrates CursorBasedStatus (cursor-based incremental) to new format */
    private fun migrateCursorBasedStatusFromJson(
        stateValue: JsonNode
    ): MsSqlServerJdbcStreamStateValue {
        val legacy = Jsons.treeToValue(stateValue, LegacyCursorBasedStatus::class.java)

        log.info {
            "Migrating CursorBasedStatus state: stream=${legacy.streamName}, cursor_field=${legacy.cursorField}, cursor=${legacy.cursor}"
        }

        // Convert String to JsonNode, handling null and "null" string
        val cursorNode: JsonNode? =
            legacy.cursor?.let { value ->
                when {
                    value.isEmpty() || value == "null" -> null
                    else -> Jsons.valueToTree<JsonNode>(value)
                }
            }

        return MsSqlServerJdbcStreamStateValue(
            version = MsSqlServerJdbcStreamStateValue.CURRENT_VERSION,
            stateType = StateType.CURSOR_BASED.stateType,
            cursorField = legacy.cursorField ?: emptyList(),
            cursor = cursorNode,
            cursorRecordCount = legacy.cursorRecordCount?.toInt() ?: 0
        )
    }

    private fun migrateCursorBasedStatus(
        opaqueStateValue: OpaqueStateValue
    ): MsSqlServerJdbcStreamStateValue {
        return migrateCursorBasedStatusFromJson(opaqueStateValue)
    }
}
