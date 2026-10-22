/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.temporal.ChronoField
import java.util.Base64

/**
 * Per-stream state persisted by the legacy `source-bigquery` connector (old Java CDK
 * `DbStreamState`), for example:
 * ```
 * {"stream_name":"id_and_name","stream_namespace":"my_dataset","cursor_field":["id"],
 *  "cursor":"3","cursor_record_count":1}
 * ```
 * The legacy connector only checkpointed cursor-based incremental syncs; full refresh syncs emitted
 * no state at all. The cursor value is the `asText()` of the emitted record value: numbers as
 * decimal strings, `DATE`/`DATETIME`/`TIMESTAMP` as `yyyy-MM-dd'T'HH:mm:ss'Z'`, `TIME` as
 * `HH:mm:ss`, `BYTES` as base64.
 */
data class BigQueryLegacyStreamState(
    @JsonProperty("stream_name") val streamName: String? = null,
    @JsonProperty("stream_namespace") val streamNamespace: String? = null,
    @JsonProperty("cursor_field") val cursorField: List<String> = emptyList(),
    @JsonProperty("cursor") val cursor: String? = null,
    @JsonProperty("cursor_record_count") val cursorRecordCount: Long? = null,
) {
    companion object {
        /** Returns the legacy state, or null when [opaqueStateValue] is not in the legacy shape. */
        fun parseOrNull(opaqueStateValue: OpaqueStateValue?): BigQueryLegacyStreamState? {
            if (opaqueStateValue == null || !opaqueStateValue.isObject) return null
            if (opaqueStateValue.has("primary_key") || opaqueStateValue.has("cursors")) return null
            if (!opaqueStateValue.has("cursor_field") && !opaqueStateValue.has("stream_name")) {
                return null
            }
            return Jsons.treeToValue(opaqueStateValue, BigQueryLegacyStreamState::class.java)
        }

        /**
         * Converts the legacy cursor string into the JSON value the Bulk CDK codecs of [cursor]
         * expect, or null when the string cannot be interpreted for that type.
         */
        fun cursorValue(cursor: EmittedField, legacyCursor: String?): JsonNode? {
            if (legacyCursor.isNullOrBlank() || legacyCursor == "null") return null
            val type: AirbyteSchemaType = cursor.type.airbyteSchemaType
            return try {
                when (type) {
                    LeafAirbyteSchemaType.INTEGER ->
                        Jsons.numberNode(BigDecimal(legacyCursor).toBigIntegerExact())
                    LeafAirbyteSchemaType.NUMBER -> Jsons.numberNode(BigDecimal(legacyCursor))
                    LeafAirbyteSchemaType.STRING -> Jsons.textNode(legacyCursor)
                    LeafAirbyteSchemaType.BOOLEAN ->
                        Jsons.booleanNode(legacyCursor.toBooleanStrict())
                    LeafAirbyteSchemaType.BINARY ->
                        Jsons.binaryNode(Base64.getDecoder().decode(legacyCursor))
                    LeafAirbyteSchemaType.DATE ->
                        LocalDateCodec.encode(parseLegacyTemporal(legacyCursor).toLocalDate())
                    LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE ->
                        LocalDateTimeCodec.encode(parseLegacyTemporal(legacyCursor))
                    LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE ->
                        OffsetDateTimeCodec.encode(
                            parseLegacyTemporal(legacyCursor).atOffset(ZoneOffset.UTC)
                        )
                    LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE ->
                        LocalTimeCodec.encode(LocalTime.parse(legacyCursor, LEGACY_TIME))
                    else -> null
                }
            } catch (_: RuntimeException) {
                null
            }
        }

        /**
         * Legacy `DATE`, `DATETIME` and `TIMESTAMP` cursors all read `yyyy-MM-dd'T'HH:mm:ss'Z'`
         * (UTC); a bare date or an offset are accepted as well.
         */
        fun parseLegacyTemporal(value: String): LocalDateTime {
            if (value.length == 10) return LocalDate.parse(value).atStartOfDay()
            return try {
                OffsetDateTime.parse(value, LEGACY_TIMESTAMP)
                    .withOffsetSameInstant(ZoneOffset.UTC)
                    .toLocalDateTime()
            } catch (_: RuntimeException) {
                LocalDateTime.parse(value, LEGACY_TIMESTAMP)
            }
        }

        private val BigInteger.node: JsonNode
            get() = Jsons.numberNode(this)

        private val LEGACY_TIMESTAMP: DateTimeFormatter =
            DateTimeFormatterBuilder()
                .appendPattern("yyyy-MM-dd'T'HH:mm:ss")
                .optionalStart()
                .appendFraction(ChronoField.NANO_OF_SECOND, 0, 9, true)
                .optionalEnd()
                .optionalStart()
                .appendOffsetId()
                .optionalEnd()
                .toFormatter()

        private val LEGACY_TIME: DateTimeFormatter =
            DateTimeFormatterBuilder()
                .appendPattern("HH:mm:ss")
                .optionalStart()
                .appendFraction(ChronoField.NANO_OF_SECOND, 0, 9, true)
                .optionalEnd()
                .toFormatter()
    }
}
