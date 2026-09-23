/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2.readapi

import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.bigqueryv2.BigQueryArrayFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryBigNumericFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryBooleanFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryDateFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryDateTimeFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryDoubleFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryLongFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryStructFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryTimeFieldType
import io.github.oshai.kotlinlogging.KotlinLogging
import java.math.BigDecimal
import java.nio.ByteBuffer
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import org.apache.arrow.vector.BigIntVector
import org.apache.arrow.vector.BitVector
import org.apache.arrow.vector.DateDayVector
import org.apache.arrow.vector.DateMilliVector
import org.apache.arrow.vector.Decimal256Vector
import org.apache.arrow.vector.DecimalVector
import org.apache.arrow.vector.FieldVector
import org.apache.arrow.vector.Float4Vector
import org.apache.arrow.vector.Float8Vector
import org.apache.arrow.vector.IntVector
import org.apache.arrow.vector.IntervalMonthDayNanoVector
import org.apache.arrow.vector.LargeVarBinaryVector
import org.apache.arrow.vector.LargeVarCharVector
import org.apache.arrow.vector.TimeMicroVector
import org.apache.arrow.vector.TimeMilliVector
import org.apache.arrow.vector.TimeNanoVector
import org.apache.arrow.vector.TimeSecVector
import org.apache.arrow.vector.TimeStampMicroVector
import org.apache.arrow.vector.TimeStampMilliVector
import org.apache.arrow.vector.TimeStampNanoVector
import org.apache.arrow.vector.TimeStampSecVector
import org.apache.arrow.vector.TimeStampVector
import org.apache.arrow.vector.VarBinaryVector
import org.apache.arrow.vector.VarCharVector
import org.apache.arrow.vector.VectorSchemaRoot
import org.apache.arrow.vector.complex.ListVector
import org.apache.arrow.vector.complex.StructVector
import org.apache.arrow.vector.types.pojo.ArrowType
import org.apache.arrow.vector.types.pojo.Field

private val log = KotlinLogging.logger {}

/**
 * Turns the rows of an Arrow [VectorSchemaRoot] read through the Storage Read API into the
 * [NativeRecordPayload] the connector's record consumers expect, producing for every column the
 * same JVM value the JDBC path produces for it, so that the JSON and protobuf output of both paths
 * is identical:
 * - scalars come out as the value type of the column's `FieldType` (`Long`, `Double`, `Boolean`,
 * `String`, `BigDecimal`, `ByteBuffer`, `LocalDate`, `LocalDateTime`, `LocalTime`,
 * `OffsetDateTime`, JSON text);
 * - `NUMERIC`/`BIGNUMERIC` values are normalized like BigQuery's own text rendering (no trailing
 * zeros, no exponent for integers), which is what the JDBC driver returns;
 * - `STRUCT` and `ARRAY` columns become the [JsonNode] that `TO_JSON_STRING` + [BigQueryValues]
 * produce on the JDBC path, nested temporals rendered with the CDK codecs and nested `BYTES` as
 * binary nodes;
 * - `INTERVAL` (Arrow month-day-nano) and `RANGE` (Arrow struct of bounds) are rendered as
 * BigQuery's canonical text, the form the JDBC driver returns for those types.
 *
 * The decoder is bound to one root; the reader loads every Arrow batch into the same root.
 */
class BigQueryArrowRecordDecoder(
    private val root: VectorSchemaRoot,
    private val fields: List<EmittedField>,
) {
    private val columns: List<Column> =
        fields.map { field ->
            val vector: FieldVector? = root.getVector(field.id)
            if (vector == null) {
                log.warn { "Column '${field.id}' is absent from the Arrow schema; emitting NULL." }
            }
            Column(field, vector)
        }

    private class Column(val field: EmittedField, val vector: FieldVector?) {
        @Suppress("UNCHECKED_CAST")
        val encoder: JsonEncoder<in Any?> = field.type.jsonEncoder as JsonEncoder<in Any?>
        var hasLoggedError: Boolean = false
    }

    /** Number of rows currently loaded into the root. */
    val rowCount: Int
        get() = root.rowCount

    /**
     * Writes row [row] into [payload] (reused between rows) and any conversion failure into
     * [changes].
     */
    fun decode(
        row: Int,
        payload: NativeRecordPayload,
        changes: MutableMap<EmittedField, FieldValueChange>,
    ) {
        changes.clear()
        for (column in columns) {
            val vector: FieldVector? = column.vector
            if (vector == null || vector.isNull(row)) {
                payload[column.field.id] = FieldValueEncoder(null, column.encoder)
                continue
            }
            try {
                payload[column.field.id] =
                    FieldValueEncoder(
                        BigQueryArrowValues.value(vector, row, column.field.type),
                        column.encoder
                    )
            } catch (e: RuntimeException) {
                if (!column.hasLoggedError) {
                    log.warn(e) { "Error converting Arrow value of column '${column.field.id}'." }
                    column.hasLoggedError = true
                }
                changes[column.field] = FieldValueChange.DESERIALIZATION_FAILURE_TOTAL
                payload[column.field.id] = FieldValueEncoder(null, NullCodec)
            }
        }
    }
}

/** Arrow value conversions; see [BigQueryArrowRecordDecoder]. */
object BigQueryArrowValues {

    /** Parses embedded JSON keeping every digit of numbers, like the JDBC path does. */
    private val exactMapper: ObjectMapper =
        ObjectMapper().enable(DeserializationFeature.USE_BIG_DECIMAL_FOR_FLOATS)

    /**
     * The value of a non-null top-level column, typed for the column's [FieldType] JSON encoder.
     */
    fun value(vector: FieldVector, row: Int, type: FieldType): Any? =
        when (type) {
            BigQueryBooleanFieldType -> boolean(vector, row)
            BigQueryLongFieldType -> long(vector, row)
            BigQueryDoubleFieldType -> double(vector, row)
            BigDecimalFieldType,
            BigQueryBigNumericFieldType -> decimal(vector, row)
            BigQueryDateFieldType -> date(vector, row)
            BigQueryDateTimeFieldType -> dateTime(vector, row)
            BigQueryTimeFieldType -> time(vector, row)
            OffsetDateTimeFieldType -> timestamp(vector, row)
            BytesFieldType -> ByteBuffer.wrap(bytes(vector, row))
            JsonStringFieldType -> text(vector, row)
            StringFieldType -> text(vector, row)
            is BigQueryStructFieldType -> toJson(vector, row, type)
            is BigQueryArrayFieldType -> toJson(vector, row, type)
            else -> {
                // PokemonFieldType and anything unexpected: the encoder renders toString().
                val nested: JsonNode = toJson(vector, row, null)
                if (nested.isValueNode && !nested.isNull) nested.asText() else nested.toString()
            }
        }

    /**
     * The JSON rendering of a nested (or untyped) value, matching what
     * [BigQueryValues.fromJsonText] derives from `TO_JSON_STRING` on the JDBC path.
     */
    fun toJson(vector: FieldVector, row: Int, type: FieldType?): JsonNode {
        if (vector.isNull(row)) {
            // BigQuery never stores a NULL array: it is an empty array on every path.
            return if (vector is ListVector) Jsons.arrayNode() else Jsons.nullNode()
        }
        return when (vector) {
            is StructVector ->
                if (isRange(vector.field)) rangeJson(vector, row)
                else structToJson(vector, row, (type as? BigQueryStructFieldType)?.fields)
            is ListVector -> listToJson(vector, row, (type as? BigQueryArrayFieldType)?.elementType)
            is BitVector -> Jsons.booleanNode(vector.get(row) == 1)
            is BigIntVector -> integerNode(vector.get(row))
            is IntVector -> integerNode(vector.get(row).toLong())
            is Float8Vector -> floatNode(vector.get(row))
            is Float4Vector -> floatNode(vector.get(row).toDouble())
            is DecimalVector -> nestedDecimalNode(vector.getObject(row))
            is Decimal256Vector -> nestedDecimalNode(vector.getObject(row))
            is VarBinaryVector -> Jsons.binaryNode(vector.get(row))
            is LargeVarBinaryVector -> Jsons.binaryNode(vector.get(row))
            is DateDayVector,
            is DateMilliVector -> LocalDateCodec.encode(date(vector, row))
            is TimeSecVector,
            is TimeMilliVector,
            is TimeMicroVector,
            is TimeNanoVector -> LocalTimeCodec.encode(time(vector, row))
            is TimeStampVector ->
                if (
                    isDateTime(vector.field) ||
                        type?.airbyteSchemaType == LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                )
                    LocalDateTimeCodec.encode(dateTime(vector, row))
                else OffsetDateTimeCodec.encode(timestamp(vector, row))
            is IntervalMonthDayNanoVector -> Jsons.textNode(intervalIsoText(vector, row))
            is VarCharVector,
            is LargeVarCharVector -> {
                val text: String = text(vector, row)
                if (isJson(vector.field) || type is JsonStringFieldType) parseJson(text)
                else Jsons.textNode(text)
            }
            else -> Jsons.textNode(vector.getObject(row).toString())
        }
    }

    private fun structToJson(
        vector: StructVector,
        row: Int,
        fields: List<EmittedField>?
    ): JsonNode {
        val node: ObjectNode = Jsons.objectNode()
        if (fields != null) {
            for (field in fields) {
                val child: FieldVector? = vector.getChild(field.id)
                node.set<JsonNode>(
                    field.id,
                    if (child == null) Jsons.nullNode() else toJson(child, row, field.type)
                )
            }
        } else {
            for (child in vector.childrenFromFields) {
                node.set<JsonNode>(child.name, toJson(child, row, null))
            }
        }
        return node
    }

    private fun listToJson(vector: ListVector, row: Int, elementType: FieldType?): JsonNode {
        val node: ArrayNode = Jsons.arrayNode()
        val data: FieldVector = vector.dataVector
        for (i in vector.getElementStartIndex(row) until vector.getElementEndIndex(row)) {
            node.add(toJson(data, i, elementType))
        }
        return node
    }

    fun boolean(vector: FieldVector, row: Int): Boolean =
        when (vector) {
            is BitVector -> vector.get(row) == 1
            else -> vector.getObject(row).toString().toBooleanStrict()
        }

    fun long(vector: FieldVector, row: Int): Long =
        when (vector) {
            is BigIntVector -> vector.get(row)
            is IntVector -> vector.get(row).toLong()
            is DecimalVector -> vector.getObject(row).longValueExact()
            else -> vector.getObject(row).toString().toLong()
        }

    fun double(vector: FieldVector, row: Int): Double =
        when (vector) {
            is Float8Vector -> vector.get(row)
            is Float4Vector -> vector.get(row).toDouble()
            is DecimalVector -> vector.getObject(row).toDouble()
            else -> vector.getObject(row).toString().toDouble()
        }

    fun decimal(vector: FieldVector, row: Int): BigDecimal =
        when (vector) {
            is DecimalVector -> normalizeDecimal(vector.getObject(row))
            is Decimal256Vector -> normalizeDecimal(vector.getObject(row))
            is BigIntVector -> BigDecimal.valueOf(vector.get(row))
            is Float8Vector -> BigDecimal.valueOf(vector.get(row))
            else -> normalizeDecimal(BigDecimal(vector.getObject(row).toString()))
        }

    fun text(vector: FieldVector, row: Int): String =
        when (vector) {
            is VarCharVector -> String(vector.get(row), Charsets.UTF_8)
            is LargeVarCharVector -> String(vector.get(row), Charsets.UTF_8)
            is IntervalMonthDayNanoVector -> intervalText(vector, row)
            is StructVector ->
                if (isRange(vector.field)) rangeText(vector, row)
                else toJson(vector, row, null).toString()
            is ListVector -> toJson(vector, row, null).toString()
            else -> vector.getObject(row).toString()
        }

    fun bytes(vector: FieldVector, row: Int): ByteArray =
        when (vector) {
            is VarBinaryVector -> vector.get(row)
            is LargeVarBinaryVector -> vector.get(row)
            is VarCharVector -> java.util.Base64.getDecoder().decode(vector.get(row))
            else ->
                throw IllegalArgumentException(
                    "Cannot read BYTES from ${vector.javaClass.simpleName}"
                )
        }

    fun date(vector: FieldVector, row: Int): LocalDate =
        when (vector) {
            is DateDayVector -> LocalDate.ofEpochDay(vector.get(row).toLong())
            is DateMilliVector -> LocalDate.ofEpochDay(Math.floorDiv(vector.get(row), 86_400_000L))
            is TimeStampVector -> dateTime(vector, row).toLocalDate()
            else -> LocalDate.parse(vector.getObject(row).toString())
        }

    fun time(vector: FieldVector, row: Int): LocalTime =
        when (vector) {
            is TimeMicroVector -> LocalTime.ofNanoOfDay(vector.get(row) * 1_000L)
            is TimeNanoVector -> LocalTime.ofNanoOfDay(vector.get(row))
            is TimeMilliVector -> LocalTime.ofNanoOfDay(vector.get(row) * 1_000_000L)
            is TimeSecVector -> LocalTime.ofSecondOfDay(vector.get(row).toLong())
            else -> LocalTime.parse(vector.getObject(row).toString())
        }

    /** A `DATETIME`: the Arrow timestamp value is a wall-clock time without zone. */
    fun dateTime(vector: FieldVector, row: Int): LocalDateTime =
        when (vector) {
            is TimeStampVector ->
                LocalDateTime.ofEpochSecond(
                    epochSeconds(vector, row),
                    nanoAdjustment(vector, row),
                    ZoneOffset.UTC
                )
            else -> LocalDateTime.parse(vector.getObject(row).toString())
        }

    /** A `TIMESTAMP`: an instant, rendered in UTC like the JDBC path does. */
    fun timestamp(vector: FieldVector, row: Int): OffsetDateTime =
        when (vector) {
            is TimeStampVector ->
                Instant.ofEpochSecond(
                        epochSeconds(vector, row),
                        nanoAdjustment(vector, row).toLong()
                    )
                    .atOffset(ZoneOffset.UTC)
            else -> OffsetDateTime.parse(vector.getObject(row).toString())
        }

    private fun unitsPerSecond(vector: TimeStampVector): Long =
        when (vector) {
            is TimeStampSecVector -> 1L
            is TimeStampMilliVector -> 1_000L
            is TimeStampMicroVector -> 1_000_000L
            is TimeStampNanoVector -> 1_000_000_000L
            else ->
                when ((vector.field.type as ArrowType.Timestamp).unit) {
                    org.apache.arrow.vector.types.TimeUnit.SECOND -> 1L
                    org.apache.arrow.vector.types.TimeUnit.MILLISECOND -> 1_000L
                    org.apache.arrow.vector.types.TimeUnit.MICROSECOND -> 1_000_000L
                    org.apache.arrow.vector.types.TimeUnit.NANOSECOND -> 1_000_000_000L
                }
        }

    private fun epochSeconds(vector: TimeStampVector, row: Int): Long =
        Math.floorDiv(vector.get(row), unitsPerSecond(vector))

    private fun nanoAdjustment(vector: TimeStampVector, row: Int): Int {
        val perSecond: Long = unitsPerSecond(vector)
        return (Math.floorMod(vector.get(row), perSecond) * (1_000_000_000L / perSecond)).toInt()
    }

    /**
     * BigQuery's canonical text of an `INTERVAL` (`[-]Y-M [-]D [-]H:M:S[.F]`), which is what the
     * JDBC driver returns for a top-level column of the type (verified: `CAST(INTERVAL ... AS
     * STRING)` gives `-1-2 -3 -4:5:6.789012`). Fractions have up to six digits, trailing zeros
     * dropped.
     */
    fun intervalText(vector: IntervalMonthDayNanoVector, row: Int): String {
        val value: org.apache.arrow.vector.PeriodDuration = vector.getObject(row)
        return intervalText(
            value.period.toTotalMonths(),
            value.period.days,
            value.duration.toNanos()
        )
    }

    fun intervalText(months: Long, days: Int, nanos: Long): String {
        val monthsSign: String = if (months < 0) "-" else ""
        val absMonths: Long = Math.abs(months)
        val nanosSign: String = if (nanos < 0) "-" else ""
        val absNanos: Long = Math.abs(nanos)
        val hours: Long = absNanos / 3_600_000_000_000L
        val minutes: Long = (absNanos / 60_000_000_000L) % 60
        val seconds: Long = (absNanos / 1_000_000_000L) % 60
        return "$monthsSign${absMonths / 12}-${absMonths % 12} $days " +
            "$nanosSign$hours:$minutes:$seconds${fractionText(absNanos)}"
    }

    /**
     * The ISO-8601 duration `TO_JSON_STRING` renders for a nested `INTERVAL` (verified:
     * `P1Y2M3DT4H5M6.789S`, `P-1Y-2M-3DT-4H-5M-6.789012S`, `P-5D`, `PT100H`): every non-zero part
     * carries its own sign, zero parts are omitted, hours are not folded into days.
     */
    fun intervalIsoText(vector: IntervalMonthDayNanoVector, row: Int): String {
        val value: org.apache.arrow.vector.PeriodDuration = vector.getObject(row)
        return intervalIsoText(
            value.period.toTotalMonths(),
            value.period.days,
            value.duration.toNanos()
        )
    }

    fun intervalIsoText(months: Long, days: Int, nanos: Long): String {
        val years: Long = months / 12
        val remainingMonths: Long = months % 12
        val absNanos: Long = Math.abs(nanos)
        val sign: String = if (nanos < 0) "-" else ""
        val hours: Long = absNanos / 3_600_000_000_000L
        val minutes: Long = (absNanos / 60_000_000_000L) % 60
        val seconds: Long = (absNanos / 1_000_000_000L) % 60
        val fraction: String = fractionText(absNanos)
        val builder = StringBuilder("P")
        if (years != 0L) builder.append(years).append('Y')
        if (remainingMonths != 0L) builder.append(remainingMonths).append('M')
        if (days != 0) builder.append(days).append('D')
        if (hours != 0L || minutes != 0L || seconds != 0L || fraction.isNotEmpty()) {
            builder.append('T')
            if (hours != 0L) builder.append(sign).append(hours).append('H')
            if (minutes != 0L) builder.append(sign).append(minutes).append('M')
            if (seconds != 0L || fraction.isNotEmpty()) {
                builder.append(sign).append(seconds).append(fraction).append('S')
            }
        }
        if (builder.length == 1) builder.append("0D")
        return builder.toString()
    }

    /** `.F` with up to six digits and no trailing zeros, empty for a whole number of seconds. */
    private fun fractionText(absNanos: Long): String {
        val micros: Long = (absNanos % 1_000_000_000L) / 1_000L
        return if (micros == 0L) "" else "." + String.format("%06d", micros).trimEnd('0')
    }

    /**
     * BigQuery's canonical text of a `RANGE` value, `[start, end)` with `UNBOUNDED` for a missing
     * bound, which is what the JDBC driver returns for a top-level column of the type (verified:
     * `[2020-01-01 00:00:00+00, 2020-12-31 00:00:00.500+00)`, `[2020-01-01 00:00:00, 2020-12-31
     * 12:34:56.123456)`).
     */
    fun rangeText(vector: StructVector, row: Int): String {
        fun bound(child: FieldVector?): String =
            if (child == null || child.isNull(row)) "UNBOUNDED"
            else rangeBoundText(child, row, nested = false)
        return "[${bound(vector.getChild("start"))}, ${bound(vector.getChild("end"))})"
    }

    /**
     * The object `TO_JSON_STRING` renders for a nested `RANGE` (verified:
     * `{"start":"2020-01-01","end":"2020-12-31"}`, `{"start":null,"end":"2021-01-01"}`,
     * `{"start":"2020-01-01T00:00:00Z","end":"2020-12-31T00:00:00.500Z"}`), which the JDBC path
     * keeps as is.
     */
    fun rangeJson(vector: StructVector, row: Int): JsonNode {
        val node: ObjectNode = Jsons.objectNode()
        for (name in listOf("start", "end")) {
            val child: FieldVector? = vector.getChild(name)
            node.set<JsonNode>(
                name,
                if (child == null || child.isNull(row)) Jsons.nullNode()
                else Jsons.textNode(rangeBoundText(child, row, nested = true)),
            )
        }
        return node
    }

    private fun rangeBoundText(vector: FieldVector, row: Int, nested: Boolean): String =
        when (vector) {
            is DateDayVector,
            is DateMilliVector -> date(vector, row).toString()
            is TimeStampVector -> {
                val isDateTime: Boolean =
                    isDateTime(vector.field) ||
                        (vector.field.type as ArrowType.Timestamp).timezone == null
                if (isDateTime) {
                    val value: LocalDateTime = dateTime(vector, row)
                    value.toLocalDate().toString() +
                        (if (nested) "T" else " ") +
                        value.toLocalTime().format(RANGE_TIME) +
                        rangeFraction(value.nano)
                } else {
                    val value: OffsetDateTime = timestamp(vector, row)
                    value.toLocalDate().toString() +
                        (if (nested) "T" else " ") +
                        value.toLocalTime().format(RANGE_TIME) +
                        rangeFraction(value.nano) +
                        (if (nested) "Z" else "+00")
                }
            }
            else -> vector.getObject(row).toString()
        }

    private val RANGE_TIME: DateTimeFormatter = DateTimeFormatter.ofPattern("HH:mm:ss")

    /** Milliseconds when they suffice, else microseconds, nothing for a whole second. */
    private fun rangeFraction(nanos: Int): String {
        val micros: Int = nanos / 1_000
        return when {
            micros == 0 -> ""
            micros % 1_000 == 0 -> "." + String.format("%03d", micros / 1_000)
            else -> "." + String.format("%06d", micros)
        }
    }

    /** Drops trailing zeros and never uses an exponent for an integer, like BigQuery's text. */
    fun normalizeDecimal(value: BigDecimal): BigDecimal {
        val stripped: BigDecimal = value.stripTrailingZeros()
        return if (stripped.scale() < 0) stripped.setScale(0) else stripped
    }

    /**
     * A nested `NUMERIC`/`BIGNUMERIC` as `TO_JSON_STRING` renders it and the JDBC path keeps it: a
     * number when the value is an integer that fits a JSON number (verified: `NUMERIC '100'` ->
     * `100`), otherwise its plain decimal text as a string (verified: `NUMERIC '12345.678900000'`
     * -> `"12345.6789"`, `BIGNUMERIC '1E-38'` -> `"0.00000000000000000000000000000000000001"`).
     */
    fun nestedDecimalNode(value: BigDecimal): JsonNode {
        val normalized: BigDecimal = normalizeDecimal(value)
        if (normalized.scale() == 0 && normalized.precision() <= 18) {
            return integerNode(normalized.longValueExact())
        }
        return Jsons.textNode(normalized.toPlainString())
    }

    /** An integer as the node Jackson would parse it from JSON text. */
    private fun integerNode(value: Long): JsonNode =
        if (value in Int.MIN_VALUE..Int.MAX_VALUE) Jsons.numberNode(value.toInt())
        else Jsons.numberNode(value)

    /**
     * A nested `FLOAT64` as `TO_JSON_STRING` renders it and the JDBC path parses it back (verified:
     * `1.0` -> `1`, `100.0` -> `100`, `0.1` -> `0.1`, `1e20` -> `1e+20`, `1e-7` -> `1e-07`, `NaN`
     * -> `"NaN"`): shortest round-trip digits, an exponent when the decimal exponent is below -4 or
     * at least 16, integers without a fraction, non-finite values as strings.
     */
    private fun floatNode(value: Double): JsonNode {
        if (value.isNaN()) return Jsons.textNode("NaN")
        if (value == Double.POSITIVE_INFINITY) return Jsons.textNode("Infinity")
        if (value == Double.NEGATIVE_INFINITY) return Jsons.textNode("-Infinity")
        if (value == 0.0) return integerNode(0L)
        val decimal: BigDecimal = BigDecimal.valueOf(value).stripTrailingZeros()
        val exponent: Int = decimal.precision() - decimal.scale() - 1
        if (exponent < -4 || exponent >= 16) return Jsons.numberNode(decimal)
        if (decimal.scale() <= 0) return integerNode(decimal.setScale(0).longValueExact())
        return Jsons.numberNode(decimal)
    }

    private fun parseJson(text: String): JsonNode =
        try {
            exactMapper.readTree(text)
        } catch (_: RuntimeException) {
            Jsons.textNode(text)
        } catch (_: java.io.IOException) {
            Jsons.textNode(text)
        }

    private fun extensionName(field: Field): String? = field.metadata?.get("ARROW:extension:name")

    fun isJson(field: Field): Boolean = extensionName(field) == "google:sqlType:json"

    fun isDateTime(field: Field): Boolean = extensionName(field) == "google:sqlType:datetime"

    fun isRange(field: Field): Boolean =
        field.metadata?.get("google:sqlType") == "range" ||
            (field.children.size == 2 &&
                field.children.map { it.name }.toSet() == setOf("start", "end") &&
                field.children.all { it.type is ArrowType.Date || it.type is ArrowType.Timestamp })
}
