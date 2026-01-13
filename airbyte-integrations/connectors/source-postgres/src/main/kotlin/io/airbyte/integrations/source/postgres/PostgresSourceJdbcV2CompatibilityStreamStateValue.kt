/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.BinaryNode
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.discover.DataOrMetaField
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset.UTC
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.format.DateTimeParseException
import java.time.temporal.ChronoField
import java.util.*
import kotlin.collections.emptyMap

data class PostgresSourceJdbcV2VersionOnlyStreamStateValue(
    @JsonProperty("version") val version: Int?,
)

data class PostgresSourceJdbcV2CompatibilityStreamStateValue(
    @JsonProperty("version") val version: Int,
    @JsonProperty("state_type") val stateType: String, /*= StateType.CURSOR_BASED.serialized,*/
    @JsonProperty("ctid") val ctid: String?,
    @JsonProperty("incremental_state") val incrementalState: JsonNode?,
    @JsonProperty("relation_filenode") val filenode: Filenode?,
    @JsonProperty("cursor_field") val cursorField: List<String>?,
    @JsonProperty("cursor") val cursorValue: JsonNode?,
    @JsonProperty("num_wraparound") val numWraparound: Long?,
    @JsonProperty("xmin_raw_value") val xminRawValue: Long?,
    @JsonProperty("xmin_xid_value") val xminXidValue: Long?,
) {
    companion object {
        fun toV3StateValue(
            v2: PostgresSourceJdbcV2CompatibilityStreamStateValue,
            stream: Stream
        ): PostgresSourceJdbcStreamStateValue {

            // the internal incremental_state value
            val incrementalState: PostgresSourceJdbcV2CompatibilityStreamStateValue? by lazy {
                v2.incrementalState?.let {
                    if (it.isNull || it.isEmpty) {
                        return@let null
                    }
                    Jsons.treeToValue(
                        it,
                        PostgresSourceJdbcV2CompatibilityStreamStateValue::class.java
                    )
                }
            }

            val v3 =
                PostgresSourceJdbcStreamStateValue(
                    version = 3,
                    stateType = V2StateType.valueOf(v2.stateType).toV3().serialized,
                    ctid = v2.ctid,
                    filenode = v2.filenode,
                    cursors =
                        when (v2.stateType) {
                            V2StateType.cursor_based.serialized -> {
                                buildCursorMap(stream, v2.cursorField, v2.cursorValue)
                            }
                            V2StateType.ctid.serialized ->
                                incrementalState?.let {
                                    when (it.stateType) {
                                        V2StateType.cursor_based.serialized -> {
                                            buildCursorMap(stream, it.cursorField, it.cursorValue)
                                        }
                                        else -> emptyMap()
                                    }
                                }
                                    ?: emptyMap()
                            else -> emptyMap()
                        },
                    xmin =
                        when (v2.stateType) {
                            V2StateType.xmin.serialized ->
                                v2.xminXidValue?.let { xminXid ->
                                    Jsons.valueToTree(xminXid) as JsonNode
                                }
                            V2StateType.ctid.serialized -> {
                                incrementalState?.let {
                                    when (it.stateType) {
                                        V2StateType.xmin.serialized -> {
                                            it.xminXidValue?.let { xminXid ->
                                                Jsons.valueToTree(xminXid) as JsonNode
                                            }
                                        }
                                        else -> null
                                    }
                                }
                            }
                            else -> null
                        }
                )

            return v3
        }

        private fun buildCursorMap(
            stream: Stream,
            cursorFieldNames: List<String>?,
            cursorValue: JsonNode?
        ): Map<String, JsonNode> {
            val cursorField: EmittedField? =
                stream.fields.firstOrNull { it.id == cursorFieldNames?.firstOrNull() }
            val cursorValueText: String? =
                cursorValue?.takeUnless { it.isNull }?.asText().takeUnless { it.isNullOrBlank() }
            return if (cursorField != null && cursorValueText != null) {
                mapOf(cursorField.id to stateValueToJsonNode(cursorField, cursorValueText))
            } else {
                emptyMap()
            }
        }
    }
}

enum class V2StateType {
    ctid,
    cursor_based,
    xmin;

    val serialized: String = name

    fun toV3(): StateType =
        when (this) {
            ctid -> StateType.CTID_BASED
            cursor_based -> StateType.CURSOR_BASED
            xmin -> StateType.XMIN_BASED
        }
}

fun stateValueToJsonNode(field: DataOrMetaField, stateValue: String?): JsonNode {
    when (field.type.airbyteSchemaType) {
        is LeafAirbyteSchemaType ->
            return when (field.type.airbyteSchemaType as LeafAirbyteSchemaType) {
                LeafAirbyteSchemaType.INTEGER -> {
                    Jsons.valueToTree(stateValue?.toBigInteger())
                }
                LeafAirbyteSchemaType.NUMBER -> {
                    Jsons.valueToTree(stateValue?.toDouble())
                }
                LeafAirbyteSchemaType.BINARY -> {
                    try {
                        val ba = Base64.getDecoder().decode(stateValue!!)
                        Jsons.valueToTree<BinaryNode>(ba)
                    } catch (_: RuntimeException) {
                        Jsons.valueToTree<JsonNode>(stateValue)
                    }
                }
                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE -> {
                    val timestampInStatePattern = "yyyy-MM-dd'T'HH:mm:ss"
                    try {
                        val formatter: DateTimeFormatter =
                            DateTimeFormatterBuilder()
                                .appendPattern(timestampInStatePattern)
                                .optionalStart()
                                .appendFraction(ChronoField.NANO_OF_SECOND, 1, 9, true)
                                .optionalEnd()
                                .toFormatter()

                        Jsons.textNode(
                            LocalDateTime.parse(stateValue, formatter)
                                .format(LocalDateTimeCodec.formatter)
                        )
                    } catch (_: RuntimeException) {
                        // Resolve to use the new format.
                        Jsons.valueToTree<JsonNode>(stateValue)
                    }
                }
                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE -> {
                    val timestampInStatePattern = "yyyy-MM-dd'T'HH:mm:ss"
                    val formatter =
                        DateTimeFormatterBuilder()
                            .appendPattern(timestampInStatePattern)
                            .optionalStart()
                            .appendFraction(ChronoField.NANO_OF_SECOND, 1, 9, true)
                            .optionalEnd()
                            .optionalStart()
                            .optionalStart()
                            .appendLiteral(' ')
                            .optionalEnd()
                            .appendOffset("+HH:mm", "Z")
                            .optionalEnd()
                            .toFormatter()

                    try {
                        val offsetDateTime =
                            try {
                                OffsetDateTime.parse(stateValue, formatter)
                            } catch (_: DateTimeParseException) {
                                // if no offset exists, we assume it's UTC
                                LocalDateTime.parse(stateValue, formatter).atOffset(UTC)
                            }
                        Jsons.valueToTree(offsetDateTime.format(OffsetDateTimeCodec.formatter))
                    } catch (_: RuntimeException) {
                        // Resolve to use the new format.
                        Jsons.valueToTree<JsonNode>(stateValue)
                    }
                }
                else -> Jsons.valueToTree<JsonNode>(stateValue)
            }
        else ->
            throw IllegalStateException(
                "PK field must be leaf type but is ${field.type.airbyteSchemaType}."
            )
    }
}
