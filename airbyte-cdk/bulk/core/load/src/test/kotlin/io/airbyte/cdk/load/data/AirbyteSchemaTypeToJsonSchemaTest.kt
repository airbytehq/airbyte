/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class AirbyteSchemaTypeToJsonSchemaTest {
    @Test
    fun testRoundTrip() {
        val schema = JsonNodeFactory.instance.objectNode()
        val props = schema.putObject("properties")
        props.putObject("name").put("type", "string").put("required", true)
        props.putObject("age").put("type", "integer")
        props.putObject("is_cool").put("type", "boolean")
        props.putObject("height").put("type", "number")
        props.putObject("friends").put("type", "array").putObject("items").put("type", "string")
        val subProps = props.putObject("address").put("type", "object").putObject("properties")
        subProps.putObject("street").put("type", "string")
        subProps.putObject("city").put("type", "string")
        props.putObject("null_field").put("type", "null")
        val union = props.putObject("nullable_union").putArray("oneOf")
        union.add(JsonNodeFactory.instance.objectNode().put("type", "string"))
        union.add(JsonNodeFactory.instance.objectNode().put("type", "integer"))
        union.add(JsonNodeFactory.instance.objectNode().put("type", "null"))

        val union2 = props.putObject("nonnullable_union")
        val union2opts = union2.putArray("oneOf")
        union2opts.add(JsonNodeFactory.instance.objectNode().put("type", "string"))
        union2opts.add(JsonNodeFactory.instance.objectNode().put("type", "integer"))
        union2.put("required", true)

        props.putObject("combined_null").putArray("type").add("string").add("null")

        val combinedDenormalized = props.putObject("combined_denormalized")
        combinedDenormalized.putArray("type").add("string").add("object")
        combinedDenormalized.putObject("properties").putObject("name").put("type", "string")

        props
            .putObject("union_array")
            .put("type", "array")
            .putArray("items")
            .add("string")
            .add("integer")

        props.putObject("date").put("type", "string").put("format", "date")
        props.putObject("time").put("type", "string").put("format", "time")
        props.putObject("timestamp").put("type", "string").put("format", "date-time")
        props
            .putObject("time_without_timezone")
            .put("type", "string")
            .put("format", "time")
            .put("airbyte_type", "time_without_timezone")
        props
            .putObject("timestamp_without_timezone")
            .put("type", "string")
            .put("format", "date-time")
            .put("airbyte_type", "timestamp_without_timezone")

        val converted = JsonSchemaToAirbyteType().convert(schema)
        val unconverted = AirbyteTypeToJsonSchema().convert(converted)

        val propsOut = unconverted.get("properties")
        Assertions.assertEquals(ofType("string", false), propsOut.get("name"))
        Assertions.assertEquals(ofType("integer", true), propsOut.get("age"))
        Assertions.assertEquals(ofType("boolean", true), propsOut.get("is_cool"))
        Assertions.assertEquals(ofType("number", true), propsOut.get("height"))

        val friends = JsonNodeFactory.instance.objectNode()
        friends.put("type", "array").replace("items", ofType("string", true))
        Assertions.assertEquals(ofNullable(friends), propsOut.get("friends"))

        val address = JsonNodeFactory.instance.objectNode()
        val addressProps = address.put("type", "object").putObject("properties")
        addressProps.replace("street", ofType("string", true))
        addressProps.replace("city", ofType("string", true))
        Assertions.assertEquals(ofNullable(address), propsOut.get("address"))

        Assertions.assertEquals(ofType("null", true), propsOut.get("null_field"))

        val nullableUnion = JsonNodeFactory.instance.objectNode()
        nullableUnion
            .putArray("oneOf")
            .add(ofType("string", false))
            .add(ofType("integer", false))
            .add(ofType("null", false))
        Assertions.assertEquals(nullableUnion, propsOut.get("nullable_union"))

        val nonnullableUnion = JsonNodeFactory.instance.objectNode()
        nonnullableUnion
            .putArray("oneOf")
            .add(ofType("string", false))
            .add(ofType("integer", false))
        Assertions.assertEquals(nonnullableUnion, propsOut.get("nonnullable_union"))

        Assertions.assertEquals(ofType("string", true), propsOut.get("combined_null"))

        val combinedDenormed = JsonNodeFactory.instance.objectNode()
        val cdObj = ofType("object", false)
        cdObj.putObject("properties").replace("name", ofType("string", true))
        combinedDenormed
            .putArray("oneOf")
            .add(ofType("string", false))
            .add(cdObj)
            .add(ofType("null", false))
        Assertions.assertEquals(combinedDenormed, propsOut.get("combined_denormalized"))

        val unionArrayOut = JsonNodeFactory.instance.objectNode()
        unionArrayOut
            .put("type", "array")
            .putObject("items")
            .putArray("oneOf")
            .add(ofType("string", false))
            .add(ofType("integer", false))
        Assertions.assertEquals(ofNullable(unionArrayOut), propsOut.get("union_array"))

        val timeTypeFieldNames =
            listOf("time", "timestamp", "time_without_timezone", "timestamp_without_timezone")
        timeTypeFieldNames.forEach { fieldName ->
            val expected = props.get(fieldName) as ObjectNode
            if (listOf("date-time", "time").contains(expected.get("format").asText())) {
                val formatName = expected.get("format").asText().replace("date-time", "timestamp")
                if (!expected.has("airbyte_type")) {
                    expected.put("airbyte_type", "${formatName}_with_timezone")
                }
            }
            Assertions.assertEquals(ofNullable(expected), propsOut.get(fieldName))
        }
    }

    private fun ofType(type: String, nullable: Boolean = true): ObjectNode =
        if (nullable) {
            ofNullable(ofType(type, false))
        } else {
            JsonNodeFactory.instance.objectNode().put("type", type)
        }

    private fun ofNullable(typeNode: JsonNode): ObjectNode {
        val schema = JsonNodeFactory.instance.objectNode()
        schema.putArray("oneOf").add(typeNode).add(ofType("null", false))
        return schema
    }
}
