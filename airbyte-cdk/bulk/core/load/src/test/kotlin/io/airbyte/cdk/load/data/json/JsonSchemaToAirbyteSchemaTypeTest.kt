/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.json

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.util.deserializeToNode
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JsonSchemaToAirbyteSchemaTypeTest {
    private fun ofType(type: String): ObjectNode {
        return JsonNodeFactory.instance.objectNode().put("type", type)
    }

    @Test
    fun testString() {
        val stringType = ofType("string")
        val airbyteType = JsonSchemaToAirbyteType().convert(stringType)
        Assertions.assertTrue(airbyteType is StringType)
    }

    @Test
    fun testBoolean() {
        val booleanType = ofType("boolean")
        val airbyteType = JsonSchemaToAirbyteType().convert(booleanType)
        Assertions.assertTrue(airbyteType is BooleanType)
    }

    @Test
    fun testInteger() {
        val integerType = ofType("integer")
        val airbyteType = JsonSchemaToAirbyteType().convert(integerType)
        Assertions.assertTrue(airbyteType is IntegerType)
    }

    /** Note: this is nonstandard, but some sources apparently use it. */
    @Test
    fun testInt() {
        val integerType = ofType("int")
        val airbyteType = JsonSchemaToAirbyteType().convert(integerType)
        Assertions.assertTrue(airbyteType is IntegerType)
    }

    @Test
    fun testNumber() {
        val numberType = ofType("number")
        val airbyteType = JsonSchemaToAirbyteType().convert(numberType)
        Assertions.assertTrue(airbyteType is NumberType)
        numberType.put("airbyte_type", "integer")
        val airbyteType2 = JsonSchemaToAirbyteType().convert(numberType)
        Assertions.assertTrue(airbyteType2 is IntegerType)
    }

    @Test
    fun testStringDate() {
        val stringType = ofType("string").put("format", "date")
        val airbyteType = JsonSchemaToAirbyteType().convert(stringType)
        Assertions.assertTrue(airbyteType is DateType)
    }

    @Test
    fun testStringTime() {
        val stringType = ofType("string").put("format", "time")
        val airbyteType = JsonSchemaToAirbyteType().convert(stringType)
        Assertions.assertEquals(airbyteType, TimeTypeWithTimezone)
        stringType.put("airbyte_type", "time_without_timezone")
        val airbyteType2 = JsonSchemaToAirbyteType().convert(stringType)
        Assertions.assertEquals(airbyteType2, TimeTypeWithoutTimezone)
        stringType.put("airbyte_type", "time_with_timezone")
        val airbyteType3 = JsonSchemaToAirbyteType().convert(stringType)
        Assertions.assertEquals(airbyteType3, TimeTypeWithTimezone)
    }

    @Test
    fun testStringTimestamp() {
        val stringType = ofType("string").put("format", "date-time")
        val airbyteType = JsonSchemaToAirbyteType().convert(stringType)
        Assertions.assertEquals(airbyteType, TimestampTypeWithTimezone)
        stringType.put("airbyte_type", "timestamp_without_timezone")
        val airbyteType2 = JsonSchemaToAirbyteType().convert(stringType)
        Assertions.assertEquals(airbyteType2, TimestampTypeWithoutTimezone)
        stringType.put("airbyte_type", "timestamp_with_timezone")
        val airbyteType3 = JsonSchemaToAirbyteType().convert(stringType)
        Assertions.assertEquals(airbyteType3, TimestampTypeWithTimezone)
    }

    @Test
    fun testObjectWithoutSchema() {
        val objectType = ofType("object")
        val airbyteType = JsonSchemaToAirbyteType().convert(objectType)
        Assertions.assertTrue(airbyteType is ObjectTypeWithoutSchema)
    }

    @Test
    fun testObjectWithEmptySchema() {
        val objectType = ofType("object")
        objectType.replace("properties", JsonNodeFactory.instance.objectNode())
        val airbyteType = JsonSchemaToAirbyteType().convert(objectType)
        Assertions.assertTrue(airbyteType is ObjectTypeWithEmptySchema)
    }

    @Test
    fun testArrayWithoutSchema() {
        val arrayType = ofType("array")
        val airbyteType = JsonSchemaToAirbyteType().convert(arrayType)
        Assertions.assertTrue(airbyteType is ArrayTypeWithoutSchema)
    }

    @Test
    fun testObjectWithSchema() {
        val schemaNode = ofType("object")
        val properties = schemaNode.putObject("properties")
        properties.replace("field1", ofType("string"))
        properties.replace("field2", ofType("integer"))
        val nestedProperties =
            properties.putObject("nested").put("type", "object").putObject("properties")
        nestedProperties.replace("field1", ofType("string"))
        nestedProperties.replace("field2", ofType("integer"))
        val airbyteType = JsonSchemaToAirbyteType().convert(schemaNode)
        Assertions.assertTrue(airbyteType is ObjectType)
        val objectType = airbyteType as ObjectType
        Assertions.assertEquals(FieldType(StringType, true), objectType.properties["field1"])
        Assertions.assertEquals(FieldType(IntegerType, true), objectType.properties["field2"])

        Assertions.assertTrue(objectType.properties.containsKey("nested"))
        val nestedField = objectType.properties["nested"]!!
        Assertions.assertTrue(nestedField.type is ObjectType)
        val nestedObjectType = nestedField.type as ObjectType
        Assertions.assertEquals(FieldType(StringType, true), nestedObjectType.properties["field1"])
        Assertions.assertEquals(FieldType(IntegerType, true), nestedObjectType.properties["field2"])
    }

    @Test
    fun testArrayWithSingleSchema() {
        val schemaNode = JsonNodeFactory.instance.objectNode().put("type", "array")
        val itemsNode = schemaNode.putObject("items").put("type", "string") as ObjectNode
        val airbyteType = JsonSchemaToAirbyteType().convert(schemaNode)
        Assertions.assertTrue(airbyteType is ArrayType)
        val arrayType = airbyteType as ArrayType
        Assertions.assertEquals(FieldType(StringType, true), arrayType.items)

        itemsNode.put("type", "integer")
        val airbyteType2 = JsonSchemaToAirbyteType().convert(schemaNode)
        Assertions.assertTrue(airbyteType2 is ArrayType)
        val arrayType2 = airbyteType2 as ArrayType
        Assertions.assertEquals(FieldType(IntegerType, true), arrayType2.items)
    }

    @Test
    fun testUnionFromArrayOfTypes() {
        listOf("oneOf", "anyOf", "allOf").forEach {
            val schemaNode = JsonNodeFactory.instance.objectNode()
            schemaNode.putArray(it).add(ofType("string")).add(ofType("integer"))

            val airbyteType = JsonSchemaToAirbyteType().convert(schemaNode)
            Assertions.assertTrue(airbyteType is UnionType)
            val unionType = airbyteType as UnionType
            Assertions.assertEquals(2, unionType.options.size)
            Assertions.assertTrue(unionType.options.contains(StringType))
            Assertions.assertTrue(unionType.options.contains(IntegerType))
        }
    }

    @Test
    fun testUnionFromArrayOfTypeNames() {
        val schemaNode = JsonNodeFactory.instance.objectNode()
        schemaNode.putArray("type").add("string").add("integer").add("object")
        val airbyteType = JsonSchemaToAirbyteType().convert(schemaNode)
        Assertions.assertTrue(airbyteType is UnionType)
        val unionType = airbyteType as UnionType
        Assertions.assertEquals(3, unionType.options.size)
        Assertions.assertTrue(unionType.options.contains(StringType))
    }

    @Test
    fun testObjectWithUnionProperties() {
        val schemaNode = ofType("object")
        val properties = schemaNode.putObject("properties")
        val typesNode = JsonNodeFactory.instance.objectNode()
        typesNode.putArray("type").add("string").add("integer")
        properties.replace("field1", typesNode)
        properties.replace("field2", ofType("integer"))
        val airbyteType = JsonSchemaToAirbyteType().convert(schemaNode)
        Assertions.assertTrue(airbyteType is ObjectType)
        val objectType = airbyteType as ObjectType
        Assertions.assertTrue(objectType.properties.containsKey("field1"))
        val field1 = objectType.properties["field1"]!!
        Assertions.assertTrue(field1.type is UnionType)
        val unionType = field1.type as UnionType
        Assertions.assertEquals(2, unionType.options.size)
        Assertions.assertTrue(unionType.options.contains(StringType))
        Assertions.assertTrue(unionType.options.contains(IntegerType))
        Assertions.assertEquals(FieldType(IntegerType, true), objectType.properties["field2"])
    }

    @Test
    fun testDenormalizeUnionProperties() {
        val schemaNode = JsonNodeFactory.instance.objectNode()
        schemaNode.putArray("type").add("object").add("array")
        schemaNode.putObject("properties").replace("field1", ofType("string"))
        schemaNode.putObject("items").put("type", "integer")
        val airbyteType = JsonSchemaToAirbyteType().convert(schemaNode)
        Assertions.assertTrue(airbyteType is UnionType)
        val unionType = airbyteType as UnionType
        Assertions.assertEquals(2, unionType.options.size)
        val objectOption = unionType.options.find { it is ObjectType }!!
        val arrayOption = unionType.options.find { it is ArrayType }!!
        Assertions.assertTrue(objectOption is ObjectType)
        val objectProperties = (objectOption as ObjectType).properties
        Assertions.assertEquals(1, objectProperties.size)
        Assertions.assertEquals(FieldType(StringType, true), objectProperties["field1"])
        Assertions.assertTrue(arrayOption is ArrayType)
        val arrayItems = (arrayOption as ArrayType).items
        Assertions.assertEquals(FieldType(IntegerType, true), arrayItems)
    }

    @Test
    fun testHandleNonstandardFields() {
        val inputSchema =
            """
                    {
                      "type": [
                        "string",
                        "integer"
                      ],
                      "description": "foo",
                      "some_random_other_property": "lol, lmao, isn't jsonschema great"
                    }
                """
                .trimIndent()
                .deserializeToNode() as ObjectNode
        val airbyteType = JsonSchemaToAirbyteType().convert(inputSchema)
        Assertions.assertEquals(UnionType.of(StringType, IntegerType), airbyteType)
    }

    @Test
    fun testUnrecognizedStringFormats() {
        val schemaNode = ofType("string").put("format", "foo")
        val airbyteType = JsonSchemaToAirbyteType().convert(schemaNode)
        Assertions.assertTrue(airbyteType is StringType)
    }
}
