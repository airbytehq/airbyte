package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.BinaryNode
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.discover.DataOrMetaField
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

) {
    companion object {
        fun toV3StateValue(v2: PostgresSourceJdbcV2CompatibilityStreamStateValue, stream: Stream): PostgresSourceJdbcStreamStateValue {
            val v3 = PostgresSourceJdbcStreamStateValue(
                version = 3,
                stateType = V2StateType.valueOf(v2.stateType).toV3().serialized,
                ctid = v2.ctid,
                filenode = v2.filenode,

                cursors = v2.incrementalState?.let {
                    val incrementalState = Jsons.treeToValue(it, PostgresSourceJdbcV2CompatibilityStreamStateValue::class.java)
                    when (incrementalState.stateType) {
                        V2StateType.cursor_based.serialized -> {
                            val cursorField: DataOrMetaField = stream.fields.first { field -> field.id == incrementalState.cursorField!!.first() }
                            mapOf(
                                incrementalState.cursorField!!.first()
                                    to stateValueToJsonNode(
                                    cursorField,
                                    incrementalState.cursorValue!!.asText()
                                )
                            )
                        }
                        else -> mapOf()
                    }
                } ?: mapOf()
            )

            return v3
        }
    }
}

enum class V2StateType {
    ctid,
    cursor_based,
    xmin
    ;

    val serialized: String = name

    fun toV3(): StateType = when (this) {
        ctid -> StateType.CTID_BASED
        cursor_based -> StateType.CURSOR_BASED
        xmin -> throw UnsupportedOperationException("xmin is not supported yet")
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
