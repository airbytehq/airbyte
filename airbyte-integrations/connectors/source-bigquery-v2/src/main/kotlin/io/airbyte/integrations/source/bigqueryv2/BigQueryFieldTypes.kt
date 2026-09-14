/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.FieldValue
import com.google.cloud.bigquery.FieldValueList
import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.JdbcGetter
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.LocalTimeFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.StringFieldType
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
import java.time.ZoneOffset
import java.time.ZonedDateTime

/**
 * Maps BigQuery column types to [FieldType]s.
 *
 * Scalars reuse the `extract-jdbc` field types (the JDBC driver returns `INT64` as `Long`,
 * `NUMERIC`/`BIGNUMERIC` as `BigDecimal`, `DATE`/`TIME`/`DATETIME`/`TIMESTAMP` as `java.sql`
 * temporal types, `BYTES` as `byte[]`, `JSON`/`GEOGRAPHY`/`INTERVAL`/`RANGE` as `String`). `STRUCT`
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
            "BOOLEAN" -> BooleanFieldType
            "INT64",
            "INT",
            "SMALLINT",
            "INTEGER",
            "BIGINT",
            "TINYINT",
            "BYTEINT" -> LongFieldType
            "FLOAT64",
            "FLOAT" -> DoubleFieldType
            "NUMERIC",
            "DECIMAL",
            "BIGNUMERIC",
            "BIGDECIMAL" -> BigDecimalFieldType
            "STRING" -> StringFieldType
            "BYTES" -> BytesFieldType
            "DATE" -> LocalDateFieldType
            "DATETIME" -> LocalDateTimeFieldType
            "TIMESTAMP" -> OffsetDateTimeFieldType
            "TIME" -> LocalTimeFieldType
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

/** Encodes values which are already JSON. */
data object JsonNodeEncoder : JsonEncoder<JsonNode> {
    override fun encode(decoded: JsonNode): JsonNode = decoded
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
        JsonNodeEncoder,
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
        JsonNodeEncoder,
    ) {

    fun jsonSchema(): ObjectNode =
        Jsons.objectNode()
            .put("type", "array")
            .set("items", BigQueryFieldTypes.jsonSchema(elementType))
}

/**
 * Reads a `STRUCT` or `ARRAY` column value from the JDBC driver as JSON, using the nested schema (
 * [fields] of a struct, [elementType] of an array) to name struct attributes and to render nested
 * scalars the way their own [FieldType] would.
 */
data class BigQueryNestedValueGetter(
    val fields: List<EmittedField>?,
    val elementType: FieldType?,
) : JdbcGetter<JsonNode> {
    override fun get(rs: ResultSet, colIdx: Int): JsonNode? {
        val value: Any = rs.getObject(colIdx) ?: return null
        if (rs.wasNull()) return null
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
            is Time -> LocalTimeCodec.encode(value.toLocalTime())
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
