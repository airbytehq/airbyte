/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.util.Jsons
import java.nio.charset.StandardCharsets
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import software.amazon.awssdk.core.SdkBytes
import software.amazon.awssdk.services.dynamodb.model.AttributeValue

/**
 * Port of the legacy connector's `DynamodbSchemaSerializerTest` with the schemas in the canonical
 * Bulk CDK shapes (`{"type": "string"}`, not the legacy `{"type": ["null", "string"]}`), plus the
 * `N` quirks and the agreement between the emitted schema and the declared [AirbyteSchemaType].
 */
class DynamoDbFieldTypeTest {

    private fun schemaOf(value: AttributeValue): JsonNode =
        DynamoDbFieldType.of(value)!!.jsonSchema()

    private fun typeOf(value: AttributeValue): AirbyteSchemaType =
        DynamoDbFieldType.of(value)!!.airbyteSchemaType

    private fun s(text: String): AttributeValue = AttributeValue.fromS(text)

    private fun n(text: String): AttributeValue = AttributeValue.fromN(text)

    private fun b(text: String): AttributeValue =
        AttributeValue.fromB(SdkBytes.fromByteArray(text.toByteArray(StandardCharsets.UTF_8)))

    @Test
    fun testCanonicalSchemaOfEveryAttributeType() {
        val item: Map<String, AttributeValue> =
            mapOf(
                "sAttribute" to s("string"),
                "nAttribute" to n("123"),
                "bAttribute" to b("byteArray"),
                "ssAttribute" to AttributeValue.builder().ss("string1", "string2").build(),
                "nsAttribute" to AttributeValue.builder().ns("125", "126").build(),
                "bsAttribute" to
                    AttributeValue.builder()
                        .bs(
                            SdkBytes.fromByteArray(
                                "byteArray1".toByteArray(StandardCharsets.UTF_8)
                            ),
                            SdkBytes.fromByteArray(
                                "byteArray2".toByteArray(StandardCharsets.UTF_8)
                            ),
                        )
                        .build(),
                "lAttribute" to AttributeValue.builder().l(s("string3"), n("12.5")).build(),
                "mAttribute" to
                    AttributeValue.builder()
                        .m(mapOf("attr1" to s("string4"), "attr2" to s("number4")))
                        .build(),
                "boolAttribute" to AttributeValue.fromBool(false),
                "nulAttribute" to AttributeValue.fromNul(true),
            )
        val actual: JsonNode = Jsons.valueToTree(item.mapValues { (_, value) -> schemaOf(value) })
        val expected: JsonNode =
            Jsons.readTree(
                """
{
  "bAttribute": {"type": "string", "contentEncoding": "base64"},
  "boolAttribute": {"type": "boolean"},
  "bsAttribute": {"type": "array", "items": {"type": "string", "contentEncoding": "base64"}},
  "lAttribute": {"type": "array", "items": {"anyOf": [{"type": "string"}, {"type": "number"}]}},
  "mAttribute": {"type": "object", "properties": {"attr2": {"type": "string"}, "attr1": {"type": "string"}}},
  "nAttribute": {"type": "number", "airbyte_type": "integer"},
  "nsAttribute": {"type": "array", "items": {"type": "number"}},
  "nulAttribute": {"type": "null"},
  "sAttribute": {"type": "string"},
  "ssAttribute": {"type": "array", "items": {"type": "string"}}
}
""",
            )
        Assertions.assertEquals(expected, actual, actual.toPrettyString())
    }

    /** The leaf shapes are the CDK's own renderings, as every JDBC connector emits them. */
    @Test
    fun testLeafShapesAreTheCdkRenderings() {
        Assertions.assertEquals(LeafAirbyteSchemaType.STRING.asJsonSchema(), schemaOf(s("x")))
        Assertions.assertEquals(LeafAirbyteSchemaType.INTEGER.asJsonSchema(), schemaOf(n("1")))
        Assertions.assertEquals(LeafAirbyteSchemaType.NUMBER.asJsonSchema(), schemaOf(n("1.5")))
        Assertions.assertEquals(LeafAirbyteSchemaType.BINARY.asJsonSchema(), schemaOf(b("x")))
        Assertions.assertEquals(
            LeafAirbyteSchemaType.BOOLEAN.asJsonSchema(),
            schemaOf(AttributeValue.fromBool(true)),
        )
        Assertions.assertEquals(
            LeafAirbyteSchemaType.NULL.asJsonSchema(),
            schemaOf(AttributeValue.fromNul(true)),
        )
        Assertions.assertEquals(
            ArrayAirbyteSchemaType(LeafAirbyteSchemaType.STRING).asJsonSchema(),
            schemaOf(AttributeValue.builder().ss("a").build()),
        )
    }

    @Test
    fun testNumberIsIntegerOnlyWhenItParsesAsLong() {
        val integer: JsonNode = Jsons.readTree("""{"type":"number","airbyte_type":"integer"}""")
        val number: JsonNode = Jsons.readTree("""{"type":"number"}""")
        Assertions.assertEquals(integer, schemaOf(n("42")))
        Assertions.assertEquals(integer, schemaOf(n("-7")))
        Assertions.assertEquals(number, schemaOf(n("1.0")))
        Assertions.assertEquals(number, schemaOf(n("12.34")))
        Assertions.assertEquals(number, schemaOf(n("1e3")))
        // 30 digits: within DynamoDB's 38-digit precision but beyond a Java long.
        Assertions.assertEquals(number, schemaOf(n("123456789012345678901234567890")))
    }

    @Test
    fun testNestedMapAndListRecurse() {
        val value: AttributeValue =
            AttributeValue.builder()
                .m(
                    mapOf(
                        "inner" to
                            AttributeValue.builder()
                                .m(mapOf("flag" to AttributeValue.fromBool(true)))
                                .build(),
                        "list" to
                            AttributeValue.builder()
                                .l(
                                    AttributeValue.fromNul(true),
                                    AttributeValue.builder().l(n("1")).build(),
                                )
                                .build(),
                    ),
                )
                .build()
        val expected: JsonNode =
            Jsons.readTree(
                """
{
  "type": "object",
  "properties": {
    "inner": {"type": "object", "properties": {"flag": {"type": "boolean"}}},
    "list": {"type": "array", "items": {"anyOf": [
      {"type": "null"},
      {"type": "array", "items": {"anyOf": [{"type": "number", "airbyte_type": "integer"}]}}
    ]}}
  }
}
""",
            )
        Assertions.assertEquals(expected, schemaOf(value))
    }

    /**
     * The declared type is what the CDK derives from the emitted schema at READ time, for every
     * attribute type, and a field rebuilt from its own schema (as at READ time) is the same field.
     */
    @Test
    fun testDeclaredTypeIsWhatTheCdkDerives() {
        val cases: Map<AttributeValue, AirbyteSchemaType> =
            mapOf(
                s("x") to LeafAirbyteSchemaType.STRING,
                n("1") to LeafAirbyteSchemaType.INTEGER,
                n("123456789012345678901234567890") to LeafAirbyteSchemaType.NUMBER,
                n("1.5") to LeafAirbyteSchemaType.NUMBER,
                b("x") to LeafAirbyteSchemaType.BINARY,
                AttributeValue.fromBool(true) to LeafAirbyteSchemaType.BOOLEAN,
                AttributeValue.fromNul(true) to LeafAirbyteSchemaType.NULL,
                AttributeValue.builder().m(mapOf("a" to s("x"))).build() to
                    LeafAirbyteSchemaType.JSONB,
                AttributeValue.builder().l(s("x"), n("1")).build() to
                    ArrayAirbyteSchemaType(LeafAirbyteSchemaType.JSONB),
                AttributeValue.builder().ss("a").build() to
                    ArrayAirbyteSchemaType(LeafAirbyteSchemaType.STRING),
                AttributeValue.builder().ns("1", "2.5").build() to
                    ArrayAirbyteSchemaType(LeafAirbyteSchemaType.NUMBER),
                AttributeValue.builder().bs(SdkBytes.fromByteArray(byteArrayOf(1))).build() to
                    ArrayAirbyteSchemaType(LeafAirbyteSchemaType.BINARY),
            )
        for ((value, expected) in cases) {
            Assertions.assertEquals(expected, typeOf(value), value.toString())
            val fromCatalog: DynamoDbFieldType = DynamoDbFieldType.fromJsonSchema(schemaOf(value))
            Assertions.assertEquals(expected, fromCatalog.airbyteSchemaType, value.toString())
            Assertions.assertEquals(DynamoDbFieldType.of(value), fromCatalog)
        }
    }

    /**
     * A catalog configured from the legacy connector (or from this connector before 2026-09-24)
     * carries `["null", <type>]` shapes; the CDK types those as JSONB, and so must the connector,
     * so that such a connection keeps validating at READ until its schema is refreshed.
     */
    @Test
    fun testLegacyShapesDeriveAsJsonb() {
        fun derived(json: String): AirbyteSchemaType =
            DynamoDbFieldType.fromJsonSchema(Jsons.readTree(json)).airbyteSchemaType
        Assertions.assertEquals(
            LeafAirbyteSchemaType.JSONB,
            derived("""{"type":["null","string"]}""")
        )
        Assertions.assertEquals(
            LeafAirbyteSchemaType.JSONB,
            derived("""{"type":["null","integer"]}"""),
        )
        Assertions.assertEquals(LeafAirbyteSchemaType.JSONB, derived("""{"type":"integer"}"""))
        Assertions.assertEquals(
            LeafAirbyteSchemaType.JSONB,
            derived("""{"type":["null","array"],"items":{"type":["null","string"]}}"""),
        )
        Assertions.assertEquals(LeafAirbyteSchemaType.NULL, derived("""{"type":"null"}"""))
        Assertions.assertEquals(
            ArrayAirbyteSchemaType(LeafAirbyteSchemaType.JSONB),
            derived("""{"type":"array","items":{"type":["null","string"]}}"""),
        )
        Assertions.assertEquals(
            ArrayAirbyteSchemaType(LeafAirbyteSchemaType.JSONB),
            derived("""{"type":"array"}"""),
        )
        Assertions.assertEquals(
            LeafAirbyteSchemaType.INTEGER,
            derived("""{"type":"number","airbyte_type":"integer"}"""),
        )
        Assertions.assertEquals(
            LeafAirbyteSchemaType.BINARY,
            derived("""{"type":"string","contentEncoding":"base64"}"""),
        )
    }
}
