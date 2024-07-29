package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode

abstract class JsonSchemaVisitor() {
    // Objects
    abstract fun visitObjectWithProperties(node: ObjectNode)
    abstract fun visitObjectProperty(name: String, node: ObjectNode)
    abstract fun visitEndOfObjectWithProperties(node: ObjectNode)

    abstract fun visitObjectWithoutProperties(node: ObjectNode)

    // Arrays
    abstract fun visitArrayWithSingleItem(node: ObjectNode)
    abstract fun visitEndOfArrayWithSingleItem(node: ObjectNode)

    abstract fun visitArrayWithItems(node: ObjectNode)
    abstract fun visitEndOfArrayWithItems(node: ObjectNode)

    abstract fun visitArrayWithoutItems(node: ObjectNode)

    // Unions
    abstract fun visitStartOfUnion(node: ObjectNode)
    abstract fun visitEndOfUnion(node: ObjectNode)

    // Simple primitive types
    abstract fun visitString(node: ObjectNode)
    abstract fun visitBoolean(node: ObjectNode)
    abstract fun visitInteger(node: ObjectNode)
    abstract fun visitNumber(node: ObjectNode)

    // Time types
    abstract fun visitDate(node: ObjectNode)
    abstract fun visitTimeWithTimezone(node: ObjectNode)
    abstract fun visitTimeWithoutTimezone(node: ObjectNode)
    abstract fun visitDateTimeWithTimezone(node: ObjectNode)
    abstract fun visitDateTimeWithoutTimezone(node: ObjectNode)

    fun visit(schema: JsonNode) {
        if (schema !is ObjectNode) {
            throw IllegalArgumentException("Schema must be an object")
        }

        val schemaType = AirbyteJsonSchemaType.fromJsonSchema(schema)

        when (schemaType) {
            AirbyteJsonSchemaType.OBJECT_WITH_PROPERTIES -> {
                visitObjectWithProperties(schema)
                schema["properties"].fields().forEach { (key, value) ->
                    visitObjectProperty(key, value as ObjectNode)
                    visit(value)
                }
                visitEndOfObjectWithProperties(schema)
            }
            AirbyteJsonSchemaType.OBJECT_WITHOUT_PROPERTIES ->
                visitObjectWithoutProperties(schema)

            AirbyteJsonSchemaType.ARRAY_WITH_ITEMS -> {
                visitArrayWithItems(schema)
                schema["items"].elements().forEach { item ->
                    visit(item)
                }
                visitEndOfArrayWithItems(schema)
            }
            AirbyteJsonSchemaType.ARRAY_WITH_ITEM -> {
                visitArrayWithSingleItem(schema)
                visit(schema["items"])
                visitEndOfArrayWithSingleItem(schema)
            }
            AirbyteJsonSchemaType.ARRAY_WITHOUT_ITEMS ->
                visitArrayWithoutItems(schema)

            AirbyteJsonSchemaType.DATE -> visitDate(schema)
            AirbyteJsonSchemaType.TIME_WITHOUT_TIMEZONE -> visitTimeWithoutTimezone(schema)
            AirbyteJsonSchemaType.TIME_WITH_TIMEZONE -> visitTimeWithTimezone(schema)
            AirbyteJsonSchemaType.TIMESTAMP_WITH_TIMEZONE -> visitDateTimeWithTimezone(schema)
            AirbyteJsonSchemaType.TIMESTAMP_WITHOUT_TIMEZONE -> visitDateTimeWithoutTimezone(schema)

            AirbyteJsonSchemaType.STRING ->  visitString(schema)
            AirbyteJsonSchemaType.BOOLEAN -> visitBoolean(schema)
            AirbyteJsonSchemaType.INTEGER -> visitInteger(schema)
            AirbyteJsonSchemaType.NUMBER -> visitNumber(schema)

            AirbyteJsonSchemaType.UNION -> {
                visitStartOfUnion(schema)
                schema["oneOf"].elements().forEach { option ->
                    visit(option)
                }
                visitEndOfUnion(schema)
            }
        }
    }
}
