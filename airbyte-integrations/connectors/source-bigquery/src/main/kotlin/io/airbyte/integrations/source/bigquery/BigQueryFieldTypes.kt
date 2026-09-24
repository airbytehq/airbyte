/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery

import com.fasterxml.jackson.core.JsonProcessingException
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.FieldValue
import com.google.cloud.bigquery.FieldValueList
import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.BigDecimalCodec
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.jdbc.BigDecimalAccessor
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BooleanAccessor
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.DateAccessor
import io.airbyte.cdk.jdbc.DoubleAccessor
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.JdbcGetter
import io.airbyte.cdk.jdbc.JdbcSetter
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.LongAccessor
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import io.airbyte.cdk.jdbc.TimeAccessor
import io.airbyte.cdk.jdbc.TimestampAccessor
import io.airbyte.cdk.output.sockets.ProtobufAwareCustomConnectorJsonCodec
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import java.nio.ByteBuffer
import java.sql.Array
import java.sql.ResultSet
import java.sql.Struct
import java.sql.Time
import java.sql.Timestamp
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.temporal.ChronoField
import java.util.Base64

/**
 * Maps BigQuery column types to [FieldType]s.
 *
 * Scalars reuse the `extract-jdbc` field types where the JDBC driver behaves
 * (`NUMERIC`/`BIGNUMERIC` as `BigDecimal`, `TIMESTAMP` as `OffsetDateTime`, `BYTES` as `byte[]`,
 * `JSON`/`GEOGRAPHY`/`INTERVAL`/`RANGE` as `String`). `BOOL`/`INT64`/`FLOAT64` get connector types
 * which read with `getObject` ([NullSafeGetter], the driver's primitive getters throw on NULL);
 * `DATE`/`DATETIME`/`TIME` are selected as text ([BigQueryTextTemporalFieldType]). `STRUCT`
 * (RECORD) and `ARRAY` (REPEATED) columns get connector-defined types which carry the nested
 * schema, so that the catalog advertises `properties` and `items`.
 *
 * | BigQuery | Airbyte | |---|---| | BOOL | boolean | | INT64 | integer | | FLOAT64, NUMERIC,
 * BIGNUMERIC | number | | STRING, GEOGRAPHY (WKT), INTERVAL, RANGE | string | | BYTES | string,
 * base64 | | DATE | date | | DATETIME | timestamp without timezone | | TIMESTAMP | timestamp with
 * timezone | | TIME | time without timezone | | JSON | object (json) | | STRUCT | object with
 * properties | | ARRAY<T> | array of T |
 */
object BigQueryFieldTypes {

    /** The [FieldType] of a top-level or nested BigQuery table [Field]. */
    fun fromField(field: Field): FieldType {
        val elementType: FieldType = scalarOrStructType(field)
        return if (field.mode == Field.Mode.REPEATED) BigQueryArrayFieldType(elementType)
        else elementType
    }

    /** The [FieldType] of a BigQuery type name as reported by the JDBC driver's metadata. */
    fun fromTypeName(typeName: String?): FieldType =
        when (typeName?.uppercase()) {
            "BOOL",
            "BOOLEAN" -> BigQueryBooleanFieldType
            "INT64",
            "INT",
            "SMALLINT",
            "INTEGER",
            "BIGINT",
            "TINYINT",
            "BYTEINT" -> BigQueryLongFieldType
            "FLOAT64",
            "FLOAT" -> BigQueryDoubleFieldType
            "NUMERIC",
            "DECIMAL" -> BigDecimalFieldType
            "BIGNUMERIC",
            "BIGDECIMAL" -> BigQueryBigNumericFieldType
            "STRING" -> StringFieldType
            "BYTES" -> BytesFieldType
            "DATE" -> BigQueryDateFieldType
            "DATETIME" -> BigQueryDateTimeFieldType
            "TIMESTAMP" -> OffsetDateTimeFieldType
            "TIME" -> BigQueryTimeFieldType
            "JSON" -> JsonStringFieldType
            "GEOGRAPHY",
            "INTERVAL",
            "RANGE" -> StringFieldType
            // The JDBC metadata does not carry the nested schema.
            "STRUCT",
            "RECORD" -> BigQueryStructFieldType(fields = null)
            "ARRAY" -> BigQueryArrayFieldType(elementType = PokemonFieldType)
            else -> PokemonFieldType
        }

    private fun scalarOrStructType(field: Field): FieldType =
        when (field.type.standardType) {
            StandardSQLTypeName.STRUCT ->
                BigQueryStructFieldType(
                    fields =
                        (field.subFields ?: emptyList()).map {
                            EmittedField(it.name, fromField(it))
                        }
                )
            // A schema field is never typed ARRAY; repetition is expressed by the REPEATED mode.
            StandardSQLTypeName.ARRAY -> PokemonFieldType
            else -> fromTypeName(field.type.standardType.name)
        }

    /** JSON schema of a field of this type, as emitted in the catalog. Returns a fresh copy. */
    fun jsonSchema(type: FieldType): ObjectNode =
        when (type) {
            is BigQueryStructFieldType -> type.jsonSchema()
            is BigQueryArrayFieldType -> type.jsonSchema()
            else -> type.airbyteSchemaType.asJsonSchema().deepCopy()
        }
}

/**
 * Codec for values which are already JSON ([BigQueryStructFieldType], [BigQueryArrayFieldType]).
 *
 * On the socket data channel in `PROTOBUF` format the CDK encodes an object or array field from its
 * serialized text ([io.airbyte.cdk.output.sockets.valueForProtobufEncoding]), so the node is
 * rendered with the same mapper as the JSON records; a JSON `null` becomes a protobuf null.
 */
data object JsonNodeCodec : ProtobufAwareCustomConnectorJsonCodec<JsonNode> {
    override fun encode(decoded: JsonNode): JsonNode = decoded

    override fun decode(encoded: JsonNode): JsonNode = encoded

    override fun valueForProtobufEncoding(v: JsonNode): Any? =
        if (v.isNull || v.isMissingNode) null else Jsons.writeValueAsString(v)
}

/**
 * BigQuery `BOOL`, `INT64` and `FLOAT64` are read with `getObject` instead of the JDBC primitive
 * getters.
 *
 * Every primitive getter of the driver's `BigQueryBaseResultSet` (`getBoolean`, `getLong`,
 * `getInt`, `getShort`, `getByte`, `getDouble`, `getFloat`; driver 1.4.0) is `getObject` followed
 * by `BigQueryTypeRegistry.convert(value, Long.class)` and an unboxing without a null check, so a
 * NULL value throws `NullPointerException: Cannot invoke "java.lang.Long.longValue()" because the
 * return value of "BigQueryTypeRegistry.convert(Object, Class)" is null`. The toolkit's
 * `BooleanFieldType`, `LongFieldType` and `DoubleFieldType` call those getters before `wasNull`,
 * and `JdbcSelectQuerier` turns the exception into a spurious `SOURCE_RETRIEVAL_ERROR` change on
 * every record with a NULL in such a column (the value is null either way). Seen on the real
 * service on 2026-09-15 (`test_parquet.flag`, `rodi_proto_type_test.purchases.user_id`).
 * `getObject` returns the boxed value, or null. The object getters (`getString`, `getBytes`,
 * `getBigDecimal`, `getObject(int, Class)`) return null for NULL, so the other scalar types are not
 * affected.
 */
sealed class NullSafeGetter<T : Any>(private val convert: (Any) -> T) : JdbcGetter<T> {
    override fun get(rs: ResultSet, colIdx: Int): T? {
        val value: Any = rs.getObject(colIdx) ?: return null
        if (rs.wasNull()) return null
        return convert(value)
    }
}

data object NullSafeBooleanGetter :
    NullSafeGetter<Boolean>({ value ->
        when (value) {
            is Boolean -> value
            is Number -> value.toInt() != 0
            else -> value.toString().toBooleanStrict()
        }
    })

data object NullSafeLongGetter :
    NullSafeGetter<Long>({ value ->
        when (value) {
            is Long -> value
            is Number -> value.toLong()
            else -> value.toString().toLong()
        }
    })

data object NullSafeDoubleGetter :
    NullSafeGetter<Double>({ value ->
        when (value) {
            is Double -> value
            is Number -> value.toDouble()
            else -> value.toString().toDouble()
        }
    })

data object BigQueryBooleanFieldType :
    LosslessJdbcFieldType<Boolean, Boolean>(
        LeafAirbyteSchemaType.BOOLEAN,
        NullSafeBooleanGetter,
        BooleanCodec,
        BooleanCodec,
        BooleanAccessor,
    )

data object BigQueryLongFieldType :
    LosslessJdbcFieldType<Long, Long>(
        LeafAirbyteSchemaType.INTEGER,
        NullSafeLongGetter,
        LongCodec,
        LongCodec,
        LongAccessor,
    )

data object BigQueryDoubleFieldType :
    LosslessJdbcFieldType<Double, Double>(
        LeafAirbyteSchemaType.NUMBER,
        NullSafeDoubleGetter,
        DoubleCodec,
        DoubleCodec,
        DoubleAccessor,
    )

/**
 * BigQuery `DATE`, `DATETIME` and `TIME` columns are selected as `CAST(col AS STRING)` and parsed
 * from BigQuery's canonical text instead of going through the JDBC driver's `java.sql` types:
 * - the driver materializes `TIME` as `java.sql.Time`, which keeps milliseconds at best while
 * BigQuery stores microseconds (`15:30:00.000001` comes back as `15:30:00.000`);
 * - the driver converts `DATE` and `DATETIME` through `java.util.Date`, whose calendar is Julian
 * before 1582-10-15, so `DATE '0001-01-01'` comes back as `0001-01-03` from every accessor,
 * `getString` included (verified against the service on 2026-09-14). `TIMESTAMP` is not affected
 * (its conversion is epoch-based) and stays on [OffsetDateTimeFieldType].
 *
 * Values that were not cast (e.g. `MAX(col)` on a `TIME` cursor) parse too, since the driver's text
 * form uses the same layout with fewer fraction digits.
 */
sealed class BigQueryTextTemporalFieldType<T>(
    airbyteSchemaType: LeafAirbyteSchemaType,
    codec: JsonCodec<T>,
    setter: JdbcSetter<in T>,
    parser: (String) -> T,
    /**
     * The BigQuery type name (`DATE`, `DATETIME`, `TIME`) used to `CAST` a bound cursor/PK value in
     * a `WHERE` clause. These columns are compared natively (not as text), but no JDBC setter
     * produces a `DATETIME` parameter — the driver's `setTimestamp`/`setObject(LocalDateTime)` both
     * bind a `TIMESTAMP`, which BigQuery refuses to compare against a `DATETIME` column ("No
     * matching signature for operator >= for argument types: DATETIME, TIMESTAMP"). The value is
     * therefore bound as a `STRING` and cast back to this type in SQL (see
     * [BigQuerySourceOperations]).
     */
    val bigQueryTypeName: String,
) :
    LosslessJdbcFieldType<T, T>(
        airbyteSchemaType,
        TextParsingGetter(parser),
        codec,
        codec,
        setter,
    )

data object BigQueryDateFieldType :
    BigQueryTextTemporalFieldType<LocalDate>(
        LeafAirbyteSchemaType.DATE,
        LocalDateCodec,
        DateAccessor,
        { LocalDate.parse(it) },
        "DATE",
    )

data object BigQueryDateTimeFieldType :
    BigQueryTextTemporalFieldType<LocalDateTime>(
        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
        LocalDateTimeCodec,
        TimestampAccessor,
        { LocalDateTime.parse(it, BigQueryTemporalText.DATETIME) },
        "DATETIME",
    )

data object BigQueryTimeFieldType :
    BigQueryTextTemporalFieldType<LocalTime>(
        LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
        LocalTimeCodec,
        TimeAccessor,
        { LocalTime.parse(it, BigQueryTemporalText.TIME) },
        "TIME",
    )

/**
 * `BIGNUMERIC` is read as a [BigDecimal] exactly like `NUMERIC` ([BigDecimalFieldType]); it exists
 * as a distinct type only so a `WHERE` bound can be cast to `BIGNUMERIC` (see
 * [BigQuerySourceOperations]): the JDBC driver binds a `BigDecimal` as a `NUMERIC` parameter, which
 * cannot hold a `BIGNUMERIC` value ("Invalid NUMERIC value") and would be a `NUMERIC` vs
 * `BIGNUMERIC` comparison. Values are emitted as plain JSON numbers (never scientific notation),
 * which the CDK's number serialization already guarantees.
 */
data object BigQueryBigNumericFieldType :
    SymmetricJdbcFieldType<BigDecimal>(
        LeafAirbyteSchemaType.NUMBER,
        BigDecimalAccessor,
        BigDecimalCodec,
    )

/** Reads the column as text and parses it. */
data class TextParsingGetter<T>(val parser: (String) -> T) : JdbcGetter<T> {
    override fun get(rs: ResultSet, colIdx: Int): T? {
        val text: String = rs.getString(colIdx) ?: return null
        if (rs.wasNull()) return null
        return parser(text.trim())
    }
}

/** BigQuery canonical text layouts: `HH:MM:SS[.F]` and `YYYY-MM-DD[ T]HH:MM:SS[.F]`. */
object BigQueryTemporalText {
    val TIME: DateTimeFormatter =
        DateTimeFormatterBuilder()
            .appendPattern("HH:mm:ss")
            .optionalStart()
            .appendFraction(ChronoField.NANO_OF_SECOND, 0, 9, true)
            .optionalEnd()
            .toFormatter()

    val DATETIME: DateTimeFormatter =
        DateTimeFormatterBuilder()
            .appendPattern("yyyy-MM-dd")
            .optionalStart()
            .appendLiteral('T')
            .optionalEnd()
            .optionalStart()
            .appendLiteral(' ')
            .optionalEnd()
            .appendPattern("HH:mm:ss")
            .optionalStart()
            .appendFraction(ChronoField.NANO_OF_SECOND, 0, 9, true)
            .optionalEnd()
            .toFormatter()
}

/**
 * A BigQuery `STRUCT` (`RECORD`) column. [fields] is null when the nested schema is unknown (type
 * derived from JDBC metadata rather than from the table schema); nested values are then keyed by
 * position.
 */
data class BigQueryStructFieldType(
    val fields: List<EmittedField>?,
) :
    JdbcFieldType<JsonNode>(
        LeafAirbyteSchemaType.JSONB,
        BigQueryNestedValueGetter(fields = fields, elementType = null),
        JsonNodeCodec,
    ) {

    fun jsonSchema(): ObjectNode {
        val schema: ObjectNode = Jsons.objectNode().put("type", "object")
        if (fields != null) {
            val properties: ObjectNode = Jsons.objectNode()
            for (field in fields) {
                properties.set<JsonNode>(field.id, BigQueryFieldTypes.jsonSchema(field.type))
            }
            schema.set<JsonNode>("properties", properties)
        }
        return schema
    }
}

/** A BigQuery `ARRAY<T>` column (a `REPEATED` field of type T). */
data class BigQueryArrayFieldType(
    val elementType: FieldType,
) :
    JdbcFieldType<JsonNode>(
        ArrayAirbyteSchemaType(elementType.airbyteSchemaType),
        BigQueryNestedValueGetter(fields = null, elementType = elementType),
        JsonNodeCodec,
    ) {

    fun jsonSchema(): ObjectNode =
        Jsons.objectNode()
            .put("type", "array")
            .set("items", BigQueryFieldTypes.jsonSchema(elementType))
}

/**
 * Reads a `STRUCT` or `ARRAY` column value as JSON, using the nested schema ([fields] of a struct,
 * [elementType] of an array) to type every nested value.
 *
 * The query generator selects these columns as `TO_JSON_STRING(col)`, so the value normally arrives
 * as BigQuery's own JSON rendering, which is exact: the driver's `java.sql.Struct`/`java.sql.Array`
 * objects lose the microseconds of nested `TIME`s, shift nested `DATE`/`DATETIME`s before 1582 and
 * turn a NULL nested struct into a struct of nulls. Those objects are still converted when they do
 * show up (a query that was not generated here).
 */
data class BigQueryNestedValueGetter(
    val fields: List<EmittedField>?,
    val elementType: FieldType?,
) : JdbcGetter<JsonNode> {
    override fun get(rs: ResultSet, colIdx: Int): JsonNode? {
        val value: Any = rs.getObject(colIdx) ?: return null
        if (rs.wasNull()) return null
        if (value is String) {
            return BigQueryValues.fromJsonText(value, fields, elementType)
        }
        return BigQueryValues.toJson(value, fields, elementType)
    }
}

/**
 * Converts the Java objects returned by the JDBC driver for BigQuery values into JSON. Scalars are
 * rendered like the corresponding [FieldType] would render them at the top level (temporal types
 * with the CDK codecs, `BYTES` as base64, `JSON` as parsed JSON); `java.sql.Struct` attributes,
 * `java.sql.Array` elements, maps, lists and the native client's `FieldValue`s are converted
 * recursively.
 */
object BigQueryValues {

    /** Parses JSON keeping every digit of NUMERIC/BIGNUMERIC values. */
    private val exactMapper: ObjectMapper =
        ObjectMapper().enable(DeserializationFeature.USE_BIG_DECIMAL_FOR_FLOATS)

    /**
     * Converts the `TO_JSON_STRING` rendering of a `STRUCT` ([fields]) or `ARRAY` ([elementType])
     * value: nested temporals are re-encoded with the CDK codecs, `BYTES` stay base64, `GEOGRAPHY`
     * (GeoJSON in that rendering) becomes WKT like at the top level, everything else is kept.
     */
    fun fromJsonText(text: String, fields: List<EmittedField>?, elementType: FieldType?): JsonNode {
        val node: JsonNode =
            try {
                exactMapper.readTree(text)
            } catch (e: JsonProcessingException) {
                // The BigQuery emulator (goccy) leaves DATE/DATETIME/TIMESTAMP/TIME values unquoted
                // in TO_JSON_STRING output; the real service never does.
                exactMapper.readTree(quoteBareTemporals(text))
            }
        return when {
            fields != null -> structFromJson(node, fields)
            elementType != null -> arrayFromJson(node, elementType)
            else -> node
        }
    }

    /** Converts a `TO_JSON_STRING` value of the given BigQuery [type]. */
    fun fromJson(node: JsonNode, type: FieldType?): JsonNode =
        when {
            node.isNull || node.isMissingNode -> Jsons.nullNode()
            type is BigQueryStructFieldType -> type.fields?.let { structFromJson(node, it) } ?: node
            type is BigQueryArrayFieldType -> arrayFromJson(node, type.elementType)
            type == null -> node
            else -> scalarFromJson(node, type)
        }

    private fun structFromJson(node: JsonNode, fields: List<EmittedField>): JsonNode {
        if (!node.isObject) return node
        val result: ObjectNode = Jsons.objectNode()
        for (field in fields) {
            result.set<JsonNode>(
                field.id,
                fromJson(node.get(field.id) ?: Jsons.nullNode(), field.type)
            )
        }
        return result
    }

    private fun arrayFromJson(node: JsonNode, elementType: FieldType): JsonNode {
        if (!node.isArray) return node
        val result: ArrayNode = Jsons.arrayNode()
        for (element in node) {
            result.add(fromJson(element, elementType))
        }
        return result
    }

    private val bareTemporal: Regex =
        Regex(
            """(?<=[:\[,])\s*(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?|\d{2}:\d{2}:\d{2}(?:\.\d+)?)(?=\s*[,}\]])"""
        )

    internal fun quoteBareTemporals(text: String): String =
        bareTemporal.replace(text) { "\"${it.groupValues[1]}\"" }

    private fun scalarFromJson(node: JsonNode, type: FieldType): JsonNode =
        try {
            when (type.airbyteSchemaType) {
                // The emulator renders BOOL as 0/1 in TO_JSON_STRING; BigQuery uses true/false.
                LeafAirbyteSchemaType.BOOLEAN ->
                    if (node.isNumber) Jsons.booleanNode(node.intValue() != 0) else node
                LeafAirbyteSchemaType.DATE -> LocalDateCodec.encode(LocalDate.parse(node.asText()))
                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE ->
                    LocalDateTimeCodec.encode(
                        LocalDateTime.parse(node.asText(), BigQueryTemporalText.DATETIME)
                    )
                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE ->
                    OffsetDateTimeCodec.encode(OffsetDateTime.parse(node.asText()))
                LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE ->
                    LocalTimeCodec.encode(LocalTime.parse(node.asText(), BigQueryTemporalText.TIME))
                LeafAirbyteSchemaType.BINARY ->
                    Jsons.binaryNode(Base64.getDecoder().decode(node.asText()))
                LeafAirbyteSchemaType.STRING ->
                    if (node.isObject && (node.has("coordinates") || node.has("geometries")))
                        Jsons.textNode(GeoJson.toWkt(node))
                    else node
                else -> node
            }
        } catch (_: RuntimeException) {
            node
        }

    /** [type] is the BigQuery [FieldType] of the value when known. */
    fun toJson(value: Any?, type: FieldType?): JsonNode =
        when (type) {
            is BigQueryStructFieldType -> toJson(value, type.fields, null)
            is BigQueryArrayFieldType -> toJson(value, null, type.elementType)
            else -> toJson(value, null, null, type)
        }

    /**
     * [fields] names the attributes of a struct value, [elementType] types the elements of an array
     * value; [scalarType] types a scalar value.
     */
    fun toJson(
        value: Any?,
        fields: List<EmittedField>?,
        elementType: FieldType?,
        scalarType: FieldType? = null,
    ): JsonNode {
        return when (value) {
            null -> Jsons.nullNode()
            is JsonNode -> value
            is Struct -> structToJson(value.attributes.asList(), fields)
            is Array -> arrayToJson((value.array as kotlin.Array<*>).asList(), elementType)
            is FieldValue -> fieldValueToJson(value, fields, elementType, scalarType)
            is FieldValueList -> {
                // The driver's own list type: a struct when the schema says so, else an array.
                if (fields != null || elementType == null) structToJson(value, fields)
                else arrayToJson(value, elementType)
            }
            is Map<*, *> -> {
                val node: ObjectNode = Jsons.objectNode()
                val byName: Map<String, FieldType> =
                    fields?.associate { it.id to it.type } ?: emptyMap()
                for ((k, v) in value) {
                    node.set<JsonNode>(k.toString(), toJson(v, byName[k.toString()]))
                }
                node
            }
            is Iterable<*> -> arrayToJson(value.toList(), elementType)
            is kotlin.Array<*> -> arrayToJson(value.asList(), elementType)
            is String -> stringToJson(value, fields, elementType, scalarType)
            is ByteArray -> Jsons.binaryNode(value)
            is ByteBuffer ->
                Jsons.binaryNode(value.array().copyOfRange(value.position(), value.limit()))
            is OffsetDateTime -> OffsetDateTimeCodec.encode(value)
            is ZonedDateTime -> OffsetDateTimeCodec.encode(value.toOffsetDateTime())
            is Instant -> OffsetDateTimeCodec.encode(value.atOffset(ZoneOffset.UTC))
            is LocalDateTime -> LocalDateTimeCodec.encode(value)
            is LocalDate -> LocalDateCodec.encode(value)
            is LocalTime -> LocalTimeCodec.encode(value)
            is Timestamp ->
                if (scalarType?.airbyteSchemaType == LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE)
                    OffsetDateTimeCodec.encode(value.toInstant().atOffset(ZoneOffset.UTC))
                else LocalDateTimeCodec.encode(value.toLocalDateTime())
            is java.sql.Date -> LocalDateCodec.encode(value.toLocalDate())
            // java.sql.Time.toLocalTime() drops the fraction; keep the milliseconds the driver has.
            is Time ->
                LocalTimeCodec.encode(
                    Instant.ofEpochMilli(value.time).atZone(ZoneId.systemDefault()).toLocalTime()
                )
            is BigDecimal -> Jsons.numberNode(value)
            is Number,
            is Boolean -> Jsons.valueToTree(value)
            else -> Jsons.textNode(value.toString())
        }
    }

    private fun structToJson(attributes: List<Any?>, fields: List<EmittedField>?): JsonNode {
        val node: ObjectNode = Jsons.objectNode()
        for ((i, attribute) in attributes.withIndex()) {
            val field: EmittedField? = fields?.getOrNull(i)
            node.set<JsonNode>(field?.id ?: i.toString(), toJson(attribute, field?.type))
        }
        return node
    }

    private fun arrayToJson(elements: List<Any?>, elementType: FieldType?): JsonNode {
        val node: ArrayNode = Jsons.arrayNode()
        for (element in elements) {
            node.add(toJson(element, elementType))
        }
        return node
    }

    private fun fieldValueToJson(
        value: FieldValue,
        fields: List<EmittedField>?,
        elementType: FieldType?,
        scalarType: FieldType?,
    ): JsonNode =
        when {
            value.isNull -> Jsons.nullNode()
            value.attribute == FieldValue.Attribute.RECORD ->
                structToJson(value.recordValue, fields)
            value.attribute == FieldValue.Attribute.REPEATED ->
                arrayToJson(value.repeatedValue, elementType)
            else -> toJson(value.value, fields, elementType, scalarType)
        }

    /**
     * A string standing for a nested value: JSON text for `STRUCT`/`ARRAY`/`JSON` values, otherwise
     * a scalar in its BigQuery text form.
     */
    private fun stringToJson(
        value: String,
        fields: List<EmittedField>?,
        elementType: FieldType?,
        scalarType: FieldType?,
    ): JsonNode {
        if (fields != null || elementType != null || scalarType is JsonStringFieldType) {
            val parsed: JsonNode? =
                try {
                    Jsons.readTree(value)
                } catch (_: Exception) {
                    null
                }
            if (parsed != null && (parsed.isContainerNode || scalarType is JsonStringFieldType)) {
                return toJson(parsed, fields, elementType, scalarType)
            }
        }
        return Jsons.textNode(value)
    }
}

/**
 * Renders the GeoJSON that `TO_JSON_STRING` produces for a `GEOGRAPHY` value as the WKT that
 * `ST_ASTEXT` (and the JDBC driver, and the legacy connector) produce for the same value.
 */
object GeoJson {
    fun toWkt(node: JsonNode): String {
        val type: String = node["type"]?.asText() ?: return node.toString()
        return when (type) {
            "Point" -> "POINT" + wrap(position(node["coordinates"]))
            "MultiPoint" -> "MULTIPOINT" + wrap(positions(node["coordinates"]))
            "LineString" -> "LINESTRING" + wrap(positions(node["coordinates"]))
            "MultiLineString" -> "MULTILINESTRING" + wrap(rings(node["coordinates"]))
            "Polygon" -> "POLYGON" + wrap(rings(node["coordinates"]))
            "MultiPolygon" ->
                "MULTIPOLYGON" + wrap(node["coordinates"].joinToString(", ") { wrap(rings(it)) })
            "GeometryCollection" ->
                "GEOMETRYCOLLECTION" + wrap(node["geometries"].joinToString(", ") { toWkt(it) })
            else -> node.toString()
        }
    }

    private fun wrap(inner: String): String = if (inner.isEmpty()) " EMPTY" else "($inner)"

    private fun rings(node: JsonNode): String = node.joinToString(", ") { wrap(positions(it)) }

    private fun positions(node: JsonNode): String = node.joinToString(", ") { position(it) }

    private fun position(node: JsonNode): String = node.joinToString(" ") { number(it) }

    private fun number(node: JsonNode): String =
        node.decimalValue().stripTrailingZeros().toPlainString()
}
