/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
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
import java.sql.Array
import java.sql.ResultSet
import java.sql.Struct

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
 * derived from JDBC metadata rather than from the table schema).
 */
data class BigQueryStructFieldType(
    val fields: List<EmittedField>?,
) : JdbcFieldType<JsonNode>(LeafAirbyteSchemaType.JSONB, BigQueryJsonValueGetter, JsonNodeEncoder) {

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
        BigQueryJsonValueGetter,
        JsonNodeEncoder,
    ) {

    fun jsonSchema(): ObjectNode =
        Jsons.objectNode()
            .put("type", "array")
            .set("items", BigQueryFieldTypes.jsonSchema(elementType))
}

/**
 * Reads a `STRUCT` or `ARRAY` column value from the JDBC driver as JSON. The driver returns
 * `java.sql.Struct` and `java.sql.Array` instances whose elements are Java values, nested structs
 * or arrays; scalars are converted with Jackson. Record-level conversion is exercised in the READ
 * stage.
 */
data object BigQueryJsonValueGetter : JdbcGetter<JsonNode> {
    override fun get(rs: ResultSet, colIdx: Int): JsonNode? {
        val value: Any = rs.getObject(colIdx) ?: return null
        return toJson(value)
    }

    fun toJson(value: Any?): JsonNode =
        when (value) {
            null -> Jsons.nullNode()
            is JsonNode -> value
            is Struct -> {
                val node: ObjectNode = Jsons.objectNode()
                val attributes: kotlin.Array<Any?> = value.attributes
                for ((i, attribute) in attributes.withIndex()) {
                    node.set<JsonNode>(i.toString(), toJson(attribute))
                }
                node
            }
            is Array -> {
                val node: ArrayNode = Jsons.arrayNode()
                val elements: kotlin.Array<*> = value.array as kotlin.Array<*>
                for (element in elements) {
                    node.add(toJson(element))
                }
                node
            }
            is Map<*, *> -> {
                val node: ObjectNode = Jsons.objectNode()
                for ((k, v) in value) {
                    node.set<JsonNode>(k.toString(), toJson(v))
                }
                node
            }
            is Iterable<*> -> {
                val node: ArrayNode = Jsons.arrayNode()
                for (element in value) {
                    node.add(toJson(element))
                }
                node
            }
            is ByteArray -> Jsons.binaryNode(value)
            is Number,
            is Boolean,
            is String -> Jsons.valueToTree(value)
            else -> Jsons.textNode(value.toString())
        }
}
