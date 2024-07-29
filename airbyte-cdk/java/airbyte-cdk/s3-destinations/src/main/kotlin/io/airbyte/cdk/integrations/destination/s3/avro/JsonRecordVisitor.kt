package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode

abstract class JsonRecordVisitor {
    abstract fun visitObjectWithProperties(tree: JsonNode, schema: ObjectNode)
    abstract fun visitObjectPropertyName(name: String, schema: ObjectNode)
    abstract fun visitEndOfObjectWithProperties(tree: JsonNode, schema: ObjectNode)
    abstract fun visitObjectWithoutProperties(tree: JsonNode, schema: ObjectNode)
    abstract fun visitArrayWithSingleItem(tree: JsonNode, schema: ObjectNode)
    abstract fun visitArrayItemUnionTyped(tree: JsonNode, schema: ArrayNode)
    abstract fun visitEndOfArrayWithSingleItem(tree: JsonNode, schema: ObjectNode)
    abstract fun visitArrayWithItems(tree: JsonNode, schema: ObjectNode)
    abstract fun visitArrayItemTyped(tree: JsonNode, schema: ObjectNode)
    abstract fun visitEndOfArrayWithItems(tree: JsonNode, schema: ObjectNode)
    abstract fun visitArrayWithoutItems(tree: JsonNode, schema: ObjectNode)
    abstract fun visitArrayItemUntyped(tree: JsonNode)
    abstract fun visitEndOfArrayWithoutItems(tree: JsonNode, schema: ObjectNode)
    abstract fun visitUnion(tree: JsonNode, schema: ObjectNode)
    abstract fun visitUnionItem(tree: JsonNode, schema: ArrayNode)
    abstract fun visitEndOfUnion(tree: JsonNode, schema: ObjectNode)
    abstract fun visitString(tree: JsonNode, schema: ObjectNode)
    abstract fun visitBoolean(tree: JsonNode, schema: ObjectNode)
    abstract fun visitInteger(tree: JsonNode, schema: ObjectNode)
    abstract fun visitNumber(tree: JsonNode, schema: ObjectNode)
    abstract fun visitDate(tree: JsonNode, schema: ObjectNode)
    abstract fun visitTimestampWithTimezone(tree: JsonNode, schema: ObjectNode)
    abstract fun visitTimestampWithoutTimezone(tree: JsonNode, schema: ObjectNode)
    abstract fun visitTimeWithTimezone(tree: JsonNode, schema: ObjectNode)
    abstract fun visitTimeWithoutTimezone(tree: JsonNode, schema: ObjectNode)

    fun visit(tree: JsonNode, schema: ObjectNode) {
        val schemaType = AirbyteJsonSchemaType.fromJsonSchema(schema)

        when (schemaType) {
            AirbyteJsonSchemaType.OBJECT_WITH_PROPERTIES -> {
                visitObjectWithProperties(tree, schema)
                tree.fields().forEach { (key, value) ->
                    visitObjectPropertyName(key, schema["properties"][key] as ObjectNode)
                    visit(value, schema["properties"][key] as ObjectNode)
                }
                visitEndOfObjectWithProperties(tree, schema)
            }
            AirbyteJsonSchemaType.OBJECT_WITHOUT_PROPERTIES -> {
                visitObjectWithoutProperties(tree, schema)
            }

            AirbyteJsonSchemaType.ARRAY_WITH_ITEMS -> {
                visitArrayWithItems(tree, schema)
                tree.forEach { item ->
                    visitArrayItemUnionTyped(item, schema["items"] as ArrayNode)
                    visit(item, schema["items"] as ObjectNode)
                }
                visitEndOfArrayWithItems(tree, schema)
            }
            AirbyteJsonSchemaType.ARRAY_WITH_ITEM -> {
                visitArrayWithSingleItem(tree, schema)
                tree.forEach { item ->
                    visitArrayItemTyped(item, schema["items"] as ObjectNode)
                }
                visitEndOfArrayWithSingleItem(tree, schema)
            }
            AirbyteJsonSchemaType.ARRAY_WITHOUT_ITEMS -> {
                visitArrayWithoutItems(tree, schema)
                visitArrayItemUntyped(tree)
                visitEndOfArrayWithoutItems(tree, schema)
            }

            AirbyteJsonSchemaType.UNION -> {
                visitUnion(tree, schema)
                val matching = schema["oneOf"].elements().asSequence().filter { option ->
                    AirbyteJsonSchemaType.fromJsonSchema(option as ObjectNode).matchesValue(tree)
                }.toList()
                if (matching.size != 1) {
                    throw IllegalArgumentException("Union type does not match exactly one option")
                }
                visit(tree, matching.first() as ObjectNode)
                visitEndOfUnion(tree, schema)
            }

            AirbyteJsonSchemaType.STRING -> {
                visitString(tree, schema)
            }
            AirbyteJsonSchemaType.BOOLEAN -> {
                visitBoolean(tree, schema)
            }
            AirbyteJsonSchemaType.INTEGER -> {
                visitInteger(tree, schema)
            }
            AirbyteJsonSchemaType.NUMBER -> {
                visitNumber(tree, schema)
            }

            AirbyteJsonSchemaType.DATE -> {
                visitDate(tree, schema)
            }
            AirbyteJsonSchemaType.TIMESTAMP_WITH_TIMEZONE -> {
                visitTimestampWithTimezone(tree, schema)
            }
            AirbyteJsonSchemaType.TIMESTAMP_WITHOUT_TIMEZONE -> {
                visitTimestampWithoutTimezone(tree, schema)
            }
            AirbyteJsonSchemaType.TIME_WITH_TIMEZONE -> {
                visitTimeWithTimezone(tree, schema)
            }
            AirbyteJsonSchemaType.TIME_WITHOUT_TIMEZONE -> {
                visitTimeWithoutTimezone(tree, schema)
            }
        }
    }
}
