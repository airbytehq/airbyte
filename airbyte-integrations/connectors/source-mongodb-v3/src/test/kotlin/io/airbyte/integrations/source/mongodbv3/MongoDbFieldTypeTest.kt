/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class MongoDbFieldTypeTest {

    /**
     * BSON type names as reported by the `$type` aggregation operator -> legacy connector mapping.
     */
    @ParameterizedTest
    @CsvSource(
        "double, NUMBER",
        "string, STRING",
        "object, OBJECT",
        "array, ARRAY",
        "binData, STRING",
        "undefined, STRING",
        "objectId, STRING",
        "bool, STRING", // legacy quirk: only the never-reported name `boolean` maps to BOOLEAN
        "boolean, BOOLEAN",
        "date, STRING",
        "null, NULL",
        "regex, STRING",
        "dbPointer, STRING",
        "javascript, STRING",
        "symbol, STRING",
        "javascriptWithScope, OBJECT",
        "int, NUMBER",
        "timestamp, STRING",
        "long, NUMBER",
        "decimal, NUMBER",
        "minKey, STRING",
        "maxKey, STRING",
        "something-new, STRING",
    )
    fun testFromBsonTypeName(bsonTypeName: String, expected: MongoDbFieldType) {
        Assertions.assertEquals(expected, MongoDbFieldType.fromBsonTypeName(bsonTypeName))
    }

    @ParameterizedTest
    @CsvSource(
        "STRING, string",
        "NUMBER, number",
        "BOOLEAN, boolean",
        "ARRAY, array",
        "OBJECT, object",
        "NULL, null",
    )
    fun testJsonSchemaIsLegacyShape(type: MongoDbFieldType, jsonSchemaType: String) {
        Assertions.assertEquals(Jsons.readTree("""{"type":"$jsonSchemaType"}"""), type.jsonSchema())
    }

    @Test
    fun testJsonSchemaIsACopy() {
        MongoDbFieldType.STRING.jsonSchema().put("mutated", true)
        Assertions.assertEquals(
            Jsons.readTree("""{"type":"string"}"""),
            MongoDbFieldType.STRING.jsonSchema()
        )
    }

    @Test
    fun testCdcCursorMetaFieldMatchesLegacySchema() {
        Assertions.assertEquals("_ab_cdc_cursor", MongoDbMetaField.CDC_CURSOR.id)
        Assertions.assertEquals(
            Jsons.readTree("""{"type":"number","airbyte_type":"integer"}"""),
            MongoDbMetaField.CDC_CURSOR.type.airbyteSchemaType.asJsonSchema(),
        )
    }
}
