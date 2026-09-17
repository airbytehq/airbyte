/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.JsonDecoder
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.LosslessFieldType
import io.airbyte.cdk.output.sockets.ProtobufAwareCustomConnectorJsonCodec
import io.airbyte.cdk.util.Jsons
import software.amazon.awssdk.services.dynamodb.model.AttributeValue

/**
 * [FieldType] of a top-level DynamoDB item attribute.
 *
 * DynamoDB is schemaless: DISCOVER samples items and maps each attribute's [AttributeValue.Type] to
 * a JSON schema, recursing into maps and lists. The JSON schema is data-dependent (a map's
 * `properties`, a list's `anyOf`), so each field carries its own schema instead of picking one of a
 * fixed set of types. The mapping ([legacyJsonSchema]) mirrors the legacy `source-dynamodb`
 * connector's `DynamodbSchemaSerializer` so that the `discover` output of the two connectors is
 * identical.
 *
 * [airbyteSchemaType] is what the Bulk CDK derives from that JSON schema when it re-reads the
 * configured catalog at READ time (`StateManagerFactory.airbyteTypeFromJsonSchema`, CDK 1.1.11): a
 * `type` array reads as an empty string and therefore maps to JSONB; only `{"type": "null"}` maps
 * to NULL. The two must agree or the CDK drops the stream with a type mismatch.
 */
data class DynamoDbFieldType(
    private val jsonSchemaTemplate: ObjectNode,
) : LosslessFieldType {

    override val airbyteSchemaType: AirbyteSchemaType = airbyteSchemaTypeOf(jsonSchemaTemplate)

    /**
     * Values are converted to JSON according to their DynamoDB type when they are read (
     * [DynamoDbJson.toRecordValue]), not according to the discovered schema; the codec passes the
     * JSON through.
     */
    override val jsonEncoder: JsonEncoder<JsonNode> = DynamoDbJsonNodeCodec

    override val jsonDecoder: JsonDecoder<JsonNode> = DynamoDbJsonNodeCodec

    /** JSON schema of the attribute, as emitted in the catalog. Returns a fresh copy. */
    fun jsonSchema(): ObjectNode = jsonSchemaTemplate.deepCopy()

    companion object {
        /**
         * Field type of an attribute, or null for a value type unknown to the SDK (the legacy
         * connector silently ignored those).
         */
        fun of(value: AttributeValue): DynamoDbFieldType? =
            legacyJsonSchema(value)?.let(::DynamoDbFieldType)

        /** Field type for a JSON schema taken from a configured catalog. */
        fun fromJsonSchema(jsonSchema: JsonNode): DynamoDbFieldType =
            DynamoDbFieldType(jsonSchema.deepCopy() as ObjectNode)

        /**
         * The legacy connector's `DynamodbSchemaSerializer`, quirks included: `N` is an integer
         * only when the sampled value parses as a Java `long` (so `1.0`, or an integer beyond 19
         * digits, is a `number`); `L` lists an `anyOf` schema per element, without deduplication;
         * `M` recurses; sets and binaries are arrays / base64 strings. Returns null for a value
         * type unknown to the SDK.
         */
        fun legacyJsonSchema(value: AttributeValue): ObjectNode? =
            when (value.type()) {
                AttributeValue.Type.S -> nullable("string")
                AttributeValue.Type.N ->
                    if (value.n().toLongOrNull() != null) nullable("integer")
                    else nullable("number")
                AttributeValue.Type.B -> nullable("string").put("contentEncoding", "base64")
                AttributeValue.Type.SS -> arrayOf(nullable("string"))
                // A number set can mix integer and decimal values.
                AttributeValue.Type.NS -> arrayOf(nullable("number"))
                AttributeValue.Type.BS ->
                    arrayOf(nullable("string").put("contentEncoding", "base64"))
                AttributeValue.Type.M -> {
                    val properties: ObjectNode = Jsons.objectNode()
                    for ((name: String, nested: AttributeValue) in value.m()) {
                        legacyJsonSchema(nested)?.let { properties.set<JsonNode>(name, it) }
                    }
                    nullable("object").apply { set<JsonNode>("properties", properties) }
                }
                AttributeValue.Type.L -> {
                    val anyOf: ArrayNode = Jsons.arrayNode()
                    for (element: AttributeValue in value.l()) {
                        legacyJsonSchema(element)?.let(anyOf::add)
                    }
                    arrayOf(Jsons.objectNode().apply { set<JsonNode>("anyOf", anyOf) })
                }
                AttributeValue.Type.BOOL -> nullable("boolean")
                AttributeValue.Type.NUL -> Jsons.objectNode().put("type", "null")
                AttributeValue.Type.UNKNOWN_TO_SDK_VERSION,
                null -> null
            }

        /** `{"type": ["null", <type>]}` */
        private fun nullable(type: String): ObjectNode =
            Jsons.objectNode().apply {
                set<JsonNode>("type", Jsons.arrayNode().add("null").add(type))
            }

        /** `{"type": ["null", "array"], "items": <items>}` */
        private fun arrayOf(items: ObjectNode): ObjectNode =
            nullable("array").apply { set<JsonNode>("items", items) }

        /**
         * Mirrors how the CDK maps a configured stream's property schema back to an
         * [AirbyteSchemaType] at READ time (see the class documentation).
         */
        fun airbyteSchemaTypeOf(jsonSchema: JsonNode): AirbyteSchemaType {
            val type: JsonNode? = jsonSchema.get("type")
            return if (type != null && type.isTextual && type.asText() == "null") {
                LeafAirbyteSchemaType.NULL
            } else {
                LeafAirbyteSchemaType.JSONB
            }
        }
    }
}

/**
 * Identity codec for record values that are already JSON. On the protobuf data channel a value is
 * sent as the text of its JSON, which is what the CDK's encoder expects for a JSONB field.
 */
data object DynamoDbJsonNodeCodec : ProtobufAwareCustomConnectorJsonCodec<JsonNode> {
    override fun encode(decoded: JsonNode): JsonNode = decoded

    override fun decode(encoded: JsonNode): JsonNode = encoded

    override fun valueForProtobufEncoding(v: JsonNode): Any = v.toString()
}
