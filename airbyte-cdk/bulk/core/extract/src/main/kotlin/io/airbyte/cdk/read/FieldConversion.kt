/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.BigDecimalCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.JsonStringCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.OffsetTimeCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import java.time.ZoneOffset

/**
 * Converts the values of a column whose type in the source no longer matches the type in the
 * configured catalog.
 *
 * When a column's type changes in the source, the platform can keep the column at a wider type that
 * fits both the old and the new values, and record the source's type in the [AIRBYTE_SOURCE_TYPE]
 * key of the column's JSON schema. The source then reads the column with its actual type, [from],
 * and emits each value as the configured type, [to]. The destination only ever sees [to].
 */
data class FieldConversion(
    val from: AirbyteSchemaType,
    val to: AirbyteSchemaType,
) {
    /** The type reported for the converted field in the emitted records. */
    val outputType: FieldType =
        object : FieldType {
            override val airbyteSchemaType: AirbyteSchemaType = to
            override val jsonEncoder: JsonEncoder<*> = encoderFor(to)
        }

    /**
     * Converts a value read with type [from] into a value of type [to]. Returns null when the value
     * can't be converted.
     */
    fun convert(value: FieldValueEncoder<*>): FieldValueEncoder<*>? {
        if (value.fieldValue == null) {
            return FieldValueEncoder(null, NullCodec)
        }
        // Converting the JSON encoding rather than the JVM value keeps this independent of the
        // connector-specific types a column can be read into.
        val encoded: JsonNode = value.encode()
        if (encoded.isNull) {
            return FieldValueEncoder(null, NullCodec)
        }
        return try {
            convertEncoded(encoded)
        } catch (_: Exception) {
            null
        }
    }

    private fun convertEncoded(encoded: JsonNode): FieldValueEncoder<*> =
        when (to) {
            LeafAirbyteSchemaType.JSONB ->
                FieldValueEncoder(Jsons.writeValueAsString(encoded), JsonStringCodec)
            LeafAirbyteSchemaType.STRING -> FieldValueEncoder(asString(encoded), TextCodec)
            LeafAirbyteSchemaType.NUMBER -> FieldValueEncoder(asNumber(encoded), BigDecimalCodec)
            LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE ->
                FieldValueEncoder(
                    LocalDateCodec.decode(encoded).atStartOfDay(),
                    LocalDateTimeCodec,
                )
            LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE -> {
                val localDateTime =
                    if (from == LeafAirbyteSchemaType.DATE) {
                        LocalDateCodec.decode(encoded).atStartOfDay()
                    } else {
                        LocalDateTimeCodec.decode(encoded)
                    }
                FieldValueEncoder(localDateTime.atOffset(ZoneOffset.UTC), OffsetDateTimeCodec)
            }
            LeafAirbyteSchemaType.TIME_WITH_TIMEZONE ->
                FieldValueEncoder(
                    LocalTimeCodec.decode(encoded).atOffset(ZoneOffset.UTC),
                    OffsetTimeCodec,
                )
            else -> throw IllegalStateException("unsupported conversion $from -> $to")
        }

    companion object {
        /** The key in a column's JSON schema which holds the column's type in the source. */
        const val AIRBYTE_SOURCE_TYPE = "airbyte_source_type"

        /**
         * The conversion of values of type [from] to type [to], or null when there's none. [from]
         * and [to] must differ.
         */
        fun of(
            from: AirbyteSchemaType,
            to: AirbyteSchemaType,
        ): FieldConversion? = FieldConversion(from, to).takeIf { from != to && it.isSupported() }

        /**
         * Whether the platform's name for a column type, [sourceTypeName], describes the CDK type
         * [actual]. The platform's types are coarser than the CDK's: it sees a binary column as a
         * string, the JSON schema of a JSON column as a union ("multi"), and doesn't distinguish
         * array element types.
         */
        fun sourceTypeMatches(
            sourceTypeName: String,
            actual: AirbyteSchemaType,
        ): Boolean =
            when (sourceTypeName) {
                "integer" -> actual == LeafAirbyteSchemaType.INTEGER
                "number" -> actual == LeafAirbyteSchemaType.NUMBER
                "boolean" -> actual == LeafAirbyteSchemaType.BOOLEAN
                "string" ->
                    actual == LeafAirbyteSchemaType.STRING || actual == LeafAirbyteSchemaType.BINARY
                "date" -> actual == LeafAirbyteSchemaType.DATE
                "timestamp_without_timezone" ->
                    actual == LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                "timestamp_with_timezone" -> actual == LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
                "time_without_timezone" -> actual == LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
                "time_with_timezone" -> actual == LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
                "array" -> actual is ArrayAirbyteSchemaType
                "object",
                "multi",
                "unknown" -> actual == LeafAirbyteSchemaType.JSONB
                else -> false
            }

        private val TO_STRING_SOURCES: Set<AirbyteSchemaType> =
            setOf(
                LeafAirbyteSchemaType.INTEGER,
                LeafAirbyteSchemaType.NUMBER,
                LeafAirbyteSchemaType.BOOLEAN,
                LeafAirbyteSchemaType.DATE,
                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
                LeafAirbyteSchemaType.TIME_WITH_TIMEZONE,
            )

        private fun FieldConversion.isSupported(): Boolean =
            when (to) {
                LeafAirbyteSchemaType.JSONB -> from != LeafAirbyteSchemaType.NULL
                LeafAirbyteSchemaType.STRING -> from in TO_STRING_SOURCES
                LeafAirbyteSchemaType.NUMBER -> from == LeafAirbyteSchemaType.INTEGER
                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE ->
                    from == LeafAirbyteSchemaType.DATE
                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE ->
                    from == LeafAirbyteSchemaType.DATE ||
                        from == LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                LeafAirbyteSchemaType.TIME_WITH_TIMEZONE ->
                    from == LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
                else -> false
            }

        private fun encoderFor(type: AirbyteSchemaType): JsonEncoder<*> =
            when (type) {
                LeafAirbyteSchemaType.STRING -> TextCodec
                LeafAirbyteSchemaType.NUMBER -> BigDecimalCodec
                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE -> LocalDateTimeCodec
                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE -> OffsetDateTimeCodec
                LeafAirbyteSchemaType.TIME_WITH_TIMEZONE -> OffsetTimeCodec
                else -> JsonStringCodec
            }

        private fun asString(encoded: JsonNode): String =
            when {
                encoded.isTextual -> encoded.textValue()
                encoded.isIntegralNumber -> encoded.bigIntegerValue().toString()
                // NaN and infinities have no decimal representation.
                encoded.isDouble && !encoded.doubleValue().isFinite() -> encoded.asText()
                encoded.isFloat && !encoded.floatValue().isFinite() -> encoded.asText()
                encoded.isNumber -> encoded.decimalValue().toPlainString()
                encoded.isBoolean -> encoded.booleanValue().toString()
                else -> throw IllegalArgumentException("can't convert $encoded to a string")
            }

        private fun asNumber(encoded: JsonNode): BigDecimal =
            when {
                encoded.isIntegralNumber -> BigDecimal(encoded.bigIntegerValue())
                encoded.isTextual -> BigDecimal(encoded.textValue())
                else -> throw IllegalArgumentException("can't convert $encoded to a number")
            }
    }
}

/**
 * Converts the values of this stream's [Stream.fieldConversions] fields in [recordData]. A value
 * which can't be converted is nulled and reported in the returned changes. Returns the inputs as is
 * when the stream has no conversions.
 */
internal fun Stream.convertFields(
    recordData: NativeRecordPayload,
    changes: Map<EmittedField, FieldValueChange>?,
): Pair<NativeRecordPayload, Map<EmittedField, FieldValueChange>?> {
    if (fieldConversions.isEmpty()) {
        return recordData to changes
    }
    // Copied, not modified in place: callers can keep using their payload after emitting it.
    val converted: NativeRecordPayload = LinkedHashMap(recordData)
    var convertedChanges: Map<EmittedField, FieldValueChange>? = changes
    for ((id, conversion) in fieldConversions) {
        val value: FieldValueEncoder<*> = recordData[id] ?: continue
        val convertedValue: FieldValueEncoder<*>? = conversion.convert(value)
        if (convertedValue != null) {
            converted[id] = convertedValue
        } else {
            converted[id] = FieldValueEncoder(null, NullCodec)
            val field: EmittedField = fields.first { it.id == id }
            convertedChanges =
                convertedChanges.orEmpty() +
                    (field to FieldValueChange.DESERIALIZATION_FAILURE_TOTAL)
        }
    }
    return converted to convertedChanges
}
