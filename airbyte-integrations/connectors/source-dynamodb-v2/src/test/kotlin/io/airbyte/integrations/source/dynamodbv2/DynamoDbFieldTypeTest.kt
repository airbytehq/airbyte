/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.util.Jsons
import java.nio.charset.StandardCharsets
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import software.amazon.awssdk.core.SdkBytes
import software.amazon.awssdk.services.dynamodb.model.AttributeValue

/** Port of the legacy connector's `DynamodbSchemaSerializerTest`, plus the `N` quirks. */
class DynamoDbFieldTypeTest {

    private fun schemaOf(value: AttributeValue): JsonNode =
        DynamoDbFieldType.of(value)!!.jsonSchema()

    @Test
    fun testLegacySchemaOfEveryAttributeType() {
        val item: Map<String, AttributeValue> =
            mapOf(
                "sAttribute" to AttributeValue.builder().s("string").build(),
                "nAttribute" to AttributeValue.builder().n("123").build(),
                "bAttribute" to
                    AttributeValue.builder()
                        .b(SdkBytes.fromByteArray("byteArray".toByteArray(StandardCharsets.UTF_8)))
                        .build(),
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
                "lAttribute" to
                    AttributeValue.builder()
                        .l(
                            AttributeValue.builder().s("string3").build(),
                            AttributeValue.builder().n("12.5").build(),
                        )
                        .build(),
                "mAttribute" to
                    AttributeValue.builder()
                        .m(
                            mapOf(
                                "attr1" to AttributeValue.builder().s("string4").build(),
                                "attr2" to AttributeValue.builder().s("number4").build(),
                            ),
                        )
                        .build(),
                "boolAttribute" to AttributeValue.builder().bool(false).build(),
                "nulAttribute" to AttributeValue.builder().nul(true).build(),
            )
        val actual: JsonNode = Jsons.valueToTree(item.mapValues { (_, value) -> schemaOf(value) })
        val expected: JsonNode =
            Jsons.readTree(
                """
{
  "bAttribute": {"type": ["null", "string"], "contentEncoding": "base64"},
  "boolAttribute": {"type": ["null", "boolean"]},
  "bsAttribute": {"type": ["null", "array"], "items": {"type": ["null", "string"], "contentEncoding": "base64"}},
  "lAttribute": {"type": ["null", "array"], "items": {"anyOf": [{"type": ["null", "string"]}, {"type": ["null", "number"]}]}},
  "mAttribute": {"type": ["null", "object"], "properties": {"attr2": {"type": ["null", "string"]}, "attr1": {"type": ["null", "string"]}}},
  "nAttribute": {"type": ["null", "integer"]},
  "nsAttribute": {"type": ["null", "array"], "items": {"type": ["null", "number"]}},
  "nulAttribute": {"type": "null"},
  "sAttribute": {"type": ["null", "string"]},
  "ssAttribute": {"type": ["null", "array"], "items": {"type": ["null", "string"]}}
}
""",
            )
        Assertions.assertEquals(expected, actual, actual.toPrettyString())
    }

    @Test
    fun testNumberIsIntegerOnlyWhenItParsesAsLong() {
        fun typeOfNumber(n: String): JsonNode =
            schemaOf(AttributeValue.builder().n(n).build())["type"]
        Assertions.assertEquals(Jsons.readTree("""["null","integer"]"""), typeOfNumber("42"))
        Assertions.assertEquals(Jsons.readTree("""["null","integer"]"""), typeOfNumber("-7"))
        Assertions.assertEquals(Jsons.readTree("""["null","number"]"""), typeOfNumber("1.0"))
        Assertions.assertEquals(Jsons.readTree("""["null","number"]"""), typeOfNumber("12.34"))
        Assertions.assertEquals(Jsons.readTree("""["null","number"]"""), typeOfNumber("1e3"))
        // 30 digits: within DynamoDB's 38-digit precision but beyond a Java long.
        Assertions.assertEquals(
            Jsons.readTree("""["null","number"]"""),
            typeOfNumber("123456789012345678901234567890"),
        )
    }

    @Test
    fun testNestedMapAndListRecurse() {
        val value: AttributeValue =
            AttributeValue.builder()
                .m(
                    mapOf(
                        "inner" to
                            AttributeValue.builder()
                                .m(mapOf("flag" to AttributeValue.builder().bool(true).build()))
                                .build(),
                        "list" to
                            AttributeValue.builder()
                                .l(
                                    AttributeValue.builder().nul(true).build(),
                                    AttributeValue.builder()
                                        .l(AttributeValue.builder().n("1").build())
                                        .build(),
                                )
                                .build(),
                    ),
                )
                .build()
        val expected: JsonNode =
            Jsons.readTree(
                """
{
  "type": ["null", "object"],
  "properties": {
    "inner": {"type": ["null", "object"], "properties": {"flag": {"type": ["null", "boolean"]}}},
    "list": {"type": ["null", "array"], "items": {"anyOf": [
      {"type": "null"},
      {"type": ["null", "array"], "items": {"anyOf": [{"type": ["null", "integer"]}]}}
    ]}}
  }
}
""",
            )
        Assertions.assertEquals(expected, schemaOf(value))
    }

    /** What the CDK derives from the catalog at READ time must equal the field's type. */
    @Test
    fun testAirbyteSchemaTypeRoundTrip() {
        Assertions.assertEquals(
            LeafAirbyteSchemaType.NULL,
            DynamoDbFieldType.of(AttributeValue.builder().nul(true).build())!!.airbyteSchemaType,
        )
        Assertions.assertEquals(
            LeafAirbyteSchemaType.JSONB,
            DynamoDbFieldType.of(AttributeValue.builder().s("x").build())!!.airbyteSchemaType,
        )
        Assertions.assertEquals(
            LeafAirbyteSchemaType.JSONB,
            DynamoDbFieldType.of(AttributeValue.builder().n("1").build())!!.airbyteSchemaType,
        )
        val schema: JsonNode = schemaOf(AttributeValue.builder().ss("a").build())
        Assertions.assertEquals(
            DynamoDbFieldType.of(AttributeValue.builder().ss("a").build()),
            DynamoDbFieldType.fromJsonSchema(schema),
        )
    }
}
