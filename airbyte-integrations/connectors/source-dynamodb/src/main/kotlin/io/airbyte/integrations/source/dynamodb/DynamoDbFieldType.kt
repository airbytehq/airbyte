/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.JsonDecoder
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.LosslessFieldType
import io.airbyte.cdk.output.sockets.ProtobufAwareCustomConnectorJsonCodec
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.format.DateTimeParseException
import java.util.Base64
import software.amazon.awssdk.services.dynamodb.model.AttributeValue

/**
 * [FieldType] of a top-level DynamoDB item attribute.
 *
 * DynamoDB is schemaless: DISCOVER samples items and maps each attribute's [AttributeValue.Type] to
 * a JSON schema, recursing into maps and lists. The JSON schema is data-dependent (a map's
 * `properties`, a list's `anyOf`), so each field carries its own schema instead of picking one of a
 * fixed set of types. The type rules ([jsonSchemaOf]) follow the legacy `source-dynamodb`
 * connector's `DynamodbSchemaSerializer` (`N` is an integer only when the sampled value parses as a
 * Java `long`, lists get one `anyOf` entry per element, ...), but the schemas are written in the
 * canonical shapes every Bulk CDK connector emits (`LeafAirbyteSchemaType.asJsonSchema`): `{"type":
 * "string"}` where the legacy connector wrote `{"type": ["null", "string"]}`, and `{"type":
 * "number", "airbyte_type": "integer"}` where it wrote `{"type": ["null", "integer"]}`. Nullability
 * is not expressed in the schema, as in the JDBC connectors. This is a deliberate deviation from
 * the legacy catalog (2026-09-24): the Bulk CDK derives a field's type from the configured catalog
 * at READ time ([airbyteSchemaTypeOf]) and understands a textual `type` only, so the legacy shapes
 * would type every attribute as JSONB.
 *
 * [airbyteSchemaType] is derived from the schema with the CDK's own rules, so the connector and the
 * CDK always agree (otherwise the CDK drops the stream with a type mismatch): `S` is a STRING, `B`
 * a BINARY, `BOOL` a BOOLEAN, an integral `N` an INTEGER, any other `N` a NUMBER, `NULL` a NULL,
 * `M` a JSONB, `SS`/`NS`/`BS` arrays of STRING/NUMBER/BINARY and `L` an array of JSONB (its `items`
 * is an `anyOf`). A configured catalog saved before this change (or by the legacy connector) still
 * carries the `["null", ...]` shapes: those derive as JSONB on both sides, so such a connection
 * keeps reading, with every value as JSON, until its schema is refreshed. The type only matters on
 * the protobuf data channel, where values travel typed ([DynamoDbJsonNodeCodec]); the JSON channels
 * emit the record value as is.
 */
data class DynamoDbFieldType(
    private val jsonSchemaTemplate: ObjectNode,
) : LosslessFieldType {

    override val airbyteSchemaType: AirbyteSchemaType = airbyteSchemaTypeOf(jsonSchemaTemplate)

    /**
     * Values are converted to JSON according to their DynamoDB type when they are read (
     * [DynamoDbJson.toRecordValue]), not according to the discovered schema; the codec passes the
     * JSON through on the JSON channels and converts it to a typed value on the protobuf channel.
     */
    val codec: DynamoDbJsonNodeCodec = DynamoDbJsonNodeCodec(airbyteSchemaType)

    override val jsonEncoder: JsonEncoder<JsonNode> = codec

    override val jsonDecoder: JsonDecoder<JsonNode> = codec

    /** JSON schema of the attribute, as emitted in the catalog. Returns a fresh copy. */
    fun jsonSchema(): ObjectNode = jsonSchemaTemplate.deepCopy()

    companion object {
        /**
         * Field type of an attribute, or null for a value type unknown to the SDK (the legacy
         * connector silently ignored those).
         */
        fun of(value: AttributeValue): DynamoDbFieldType? =
            jsonSchemaOf(value)?.let(::DynamoDbFieldType)

        /** Field type for a JSON schema taken from a configured catalog. */
        fun fromJsonSchema(jsonSchema: JsonNode): DynamoDbFieldType =
            DynamoDbFieldType(jsonSchema.deepCopy() as ObjectNode)

        /**
         * The JSON schema of a sampled attribute value, in the canonical Bulk CDK shapes, with the
         * legacy connector's type rules: `N` is an integer only when the sampled value parses as a
         * Java `long` (so `1.0`, or an integer beyond 19 digits, is a `number`); `NS` is an array
         * of numbers (a set can mix integers and decimals); `L` lists an `anyOf` schema per
         * element, without deduplication; `M` recurses into `properties`. Returns null for a value
         * type unknown to the SDK.
         */
        fun jsonSchemaOf(value: AttributeValue): ObjectNode? =
            when (value.type()) {
                AttributeValue.Type.S -> leaf(LeafAirbyteSchemaType.STRING)
                AttributeValue.Type.N ->
                    if (value.n().toLongOrNull() != null) leaf(LeafAirbyteSchemaType.INTEGER)
                    else leaf(LeafAirbyteSchemaType.NUMBER)
                AttributeValue.Type.B -> leaf(LeafAirbyteSchemaType.BINARY)
                AttributeValue.Type.SS -> arrayOf(leaf(LeafAirbyteSchemaType.STRING))
                AttributeValue.Type.NS -> arrayOf(leaf(LeafAirbyteSchemaType.NUMBER))
                AttributeValue.Type.BS -> arrayOf(leaf(LeafAirbyteSchemaType.BINARY))
                AttributeValue.Type.M -> {
                    val properties: ObjectNode = Jsons.objectNode()
                    for ((name: String, nested: AttributeValue) in value.m()) {
                        jsonSchemaOf(nested)?.let { properties.set<JsonNode>(name, it) }
                    }
                    Jsons.objectNode().put("type", "object").apply {
                        set<JsonNode>("properties", properties)
                    }
                }
                AttributeValue.Type.L -> {
                    val anyOf: ArrayNode = Jsons.arrayNode()
                    for (element: AttributeValue in value.l()) {
                        jsonSchemaOf(element)?.let(anyOf::add)
                    }
                    arrayOf(Jsons.objectNode().apply { set<JsonNode>("anyOf", anyOf) })
                }
                AttributeValue.Type.BOOL -> leaf(LeafAirbyteSchemaType.BOOLEAN)
                AttributeValue.Type.NUL -> leaf(LeafAirbyteSchemaType.NULL)
                AttributeValue.Type.UNKNOWN_TO_SDK_VERSION,
                null -> null
            }

        /** The CDK's own rendering of a leaf type, e.g. `{"type": "string"}`. */
        private fun leaf(type: LeafAirbyteSchemaType): ObjectNode =
            type.asJsonSchema().deepCopy() as ObjectNode

        /** `{"type": "array", "items": <items>}` */
        private fun arrayOf(items: ObjectNode): ObjectNode =
            Jsons.objectNode().put("type", "array").apply { set<JsonNode>("items", items) }

        /**
         * The [AirbyteSchemaType] of a property schema, exactly as the Bulk CDK (1.1.11,
         * `StateManagerFactory.airbyteTypeFromJsonSchema`) derives it from the configured catalog
         * at READ time. Kept in sync by hand: it only reads a textual `type` (a `type` array, or a
         * bare `"integer"`, is JSONB), refines `string` by `format`, `airbyte_type` and
         * `contentEncoding`, `number` by `airbyte_type`, and recurses into an array's `items`.
         */
        fun airbyteSchemaTypeOf(jsonSchema: JsonNode): AirbyteSchemaType {
            fun value(key: String): String = jsonSchema[key]?.asText() ?: ""
            return when (value("type")) {
                "array" ->
                    ArrayAirbyteSchemaType(
                        jsonSchema["items"]?.let(::airbyteSchemaTypeOf)
                            ?: LeafAirbyteSchemaType.JSONB
                    )
                "null" -> LeafAirbyteSchemaType.NULL
                "boolean" -> LeafAirbyteSchemaType.BOOLEAN
                "number" ->
                    when (value("airbyte_type")) {
                        "integer",
                        "big_integer", -> LeafAirbyteSchemaType.INTEGER
                        else -> LeafAirbyteSchemaType.NUMBER
                    }
                "string" ->
                    when (value("format")) {
                        "date" -> LeafAirbyteSchemaType.DATE
                        "date-time" ->
                            if (value("airbyte_type") == "timestamp_with_timezone") {
                                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
                            } else {
                                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
                            }
                        "time" ->
                            if (value("airbyte_type") == "time_with_timezone") {
                                LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
                            } else {
                                LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
                            }
                        else ->
                            if (value("contentEncoding") == "base64") {
                                LeafAirbyteSchemaType.BINARY
                            } else {
                                LeafAirbyteSchemaType.STRING
                            }
                    }
                else -> LeafAirbyteSchemaType.JSONB
            }
        }
    }
}

/**
 * Codec of a [DynamoDbFieldType]: identity on the JSON channels (record values are already JSON,
 * see [DynamoDbJson.toRecordValue]), and on the protobuf data channel the typed value the CDK's
 * encoder expects for the field's [schemaType]: a string for STRING, a [BigInteger] for INTEGER, an
 * exact [BigDecimal] for NUMBER (written in plain notation by the encoder: `100000`, never `1E+5`),
 * a boolean, the bytes of a BINARY, parsed temporals, and the JSON text (from the CDK's [Jsons]
 * mapper, plain decimals included) for JSONB and array fields. A JSON null is a protobuf null, like
 * an attribute the item does not have.
 *
 * DynamoDB is schemaless and the schema comes from a sample, so an item may hold a value of another
 * type than the field declares (a `S` where the sample had `N`, say). The JSON channels pass such a
 * value through unchanged and leave the coercion to the destination, as the legacy connector did;
 * on the protobuf channel the slot is typed, so [DynamoDbPartitionReader] asks [representable]
 * first and sends a null with a change record when the answer is no.
 */
class DynamoDbJsonNodeCodec(val schemaType: AirbyteSchemaType) :
    ProtobufAwareCustomConnectorJsonCodec<JsonNode> {
    override fun encode(decoded: JsonNode): JsonNode = decoded

    override fun decode(encoded: JsonNode): JsonNode = encoded

    /** Whether [value] can travel in a protobuf slot of [schemaType]. */
    fun representable(value: JsonNode): Boolean =
        value.isNull ||
            when (schemaType) {
                LeafAirbyteSchemaType.STRING -> value.isTextual || value.isBinary
                // Bytes, or their base64 text: the form a binary takes once it has been through
                // JSON, and the form the CDK puts on the wire anyway.
                LeafAirbyteSchemaType.BINARY ->
                    value.isBinary || (value.isTextual && isBase64(value.textValue()))
                LeafAirbyteSchemaType.BOOLEAN -> value.isBoolean
                LeafAirbyteSchemaType.INTEGER -> value.isNumber && isIntegral(value)
                LeafAirbyteSchemaType.NUMBER -> value.isNumber
                LeafAirbyteSchemaType.NULL -> false
                LeafAirbyteSchemaType.DATE,
                LeafAirbyteSchemaType.TIME_WITH_TIMEZONE,
                LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE ->
                    value.isTextual && temporal(value.asText()) != null
                LeafAirbyteSchemaType.JSONB,
                is ArrayAirbyteSchemaType -> true
            }

    override fun valueForProtobufEncoding(v: JsonNode): Any? {
        if (v.isNull) return null
        require(representable(v)) { "A $v is not representable as $schemaType" }
        return when (schemaType) {
            LeafAirbyteSchemaType.STRING -> v.asText()
            LeafAirbyteSchemaType.BINARY ->
                if (v.isBinary) v.binaryValue() else Base64.getDecoder().decode(v.textValue())
            LeafAirbyteSchemaType.BOOLEAN -> v.booleanValue()
            LeafAirbyteSchemaType.INTEGER ->
                if (v.isIntegralNumber) v.bigIntegerValue()
                else v.decimalValue().stripTrailingZeros().toBigIntegerExact()
            LeafAirbyteSchemaType.NUMBER -> v.decimalValue()
            LeafAirbyteSchemaType.NULL -> null
            LeafAirbyteSchemaType.DATE,
            LeafAirbyteSchemaType.TIME_WITH_TIMEZONE,
            LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
            LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
            LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE -> temporal(v.asText())
            LeafAirbyteSchemaType.JSONB,
            is ArrayAirbyteSchemaType -> Jsons.writeValueAsString(v)
        }
    }

    private fun isBase64(text: String): Boolean =
        try {
            Base64.getDecoder().decode(text)
            true
        } catch (_: IllegalArgumentException) {
            false
        }

    /** Whether a JSON number has no fractional part (`1`, `1.0`, `1e5`, a 30-digit integer). */
    private fun isIntegral(value: JsonNode): Boolean =
        value.isIntegralNumber ||
            value.decimalValue().let { it.signum() == 0 || it.stripTrailingZeros().scale() <= 0 }

    /**
     * The `java.time` value the protobuf encoder expects for a temporal [schemaType], or null when
     * the text does not parse. DISCOVER never produces temporal schemas (attributes have no
     * `format`), so this only applies to a hand-edited catalog.
     */
    private fun temporal(text: String): Any? =
        try {
            when (schemaType) {
                LeafAirbyteSchemaType.DATE -> LocalDate.parse(text)
                LeafAirbyteSchemaType.TIME_WITH_TIMEZONE -> OffsetTime.parse(text)
                LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE -> LocalTime.parse(text)
                LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE -> OffsetDateTime.parse(text)
                LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE -> LocalDateTime.parse(text)
                else -> null
            }
        } catch (_: DateTimeParseException) {
            null
        }
}
