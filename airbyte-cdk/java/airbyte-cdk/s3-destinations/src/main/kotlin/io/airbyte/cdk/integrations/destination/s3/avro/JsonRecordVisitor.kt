package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers

abstract class JsonRecordVisitor {
    abstract fun visitObjectWithProperties(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitObjectPropertyName(name: String, schema: ObjectNode)
    abstract fun visitObjectAdditionalProperty(name: String, value: JsonNode)
    abstract fun visitEndOfObjectWithProperties(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitObjectWithoutProperties(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitArrayWithSingleItem(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitArrayItemUnionTyped(tree: JsonNode?, schema: ArrayNode)
    abstract fun visitEndOfArrayWithSingleItem(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitArrayWithItems(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitArrayItemTyped(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitEndOfArrayWithItems(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitArrayWithoutItems(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitArrayItemUntyped(tree: JsonNode?)
    abstract fun visitEndOfArrayWithoutItems(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitUnion(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitUnionItem(tree: JsonNode?, schema: ArrayNode)
    abstract fun visitEndOfUnion(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitBinaryData(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitString(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitBoolean(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitInteger(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitNumber(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitDate(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitTimestampWithTimezone(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitTimestampWithoutTimezone(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitTimeWithTimezone(tree: JsonNode?, schema: ObjectNode)
    abstract fun visitTimeWithoutTimezone(tree: JsonNode?, schema: ObjectNode)

    fun visit(tree: JsonNode?, schema: ObjectNode) {
        println("visting $tree with schema $schema")
        val schemaType = AirbyteJsonSchemaType.fromJsonSchema(schema)

        when (schemaType) {
            AirbyteJsonSchemaType.OBJECT_WITH_PROPERTIES -> {
                visitObjectWithProperties(tree, schema)
                tree?.fields()?.forEach { (key, value) ->
                    if (!schema["properties"].has("key")) {
                        visitObjectAdditionalProperty(key, value)
                    } else {
                        visitObjectPropertyName(key, schema["properties"] as ObjectNode)
                        visit(value, schema["properties"][key] as ObjectNode)
                    }
                }
                visitEndOfObjectWithProperties(tree, schema)
            }
            AirbyteJsonSchemaType.OBJECT_WITHOUT_PROPERTIES -> {
                visitObjectWithoutProperties(tree, schema)
            }

            AirbyteJsonSchemaType.ARRAY_WITH_ITEMS -> {
                visitArrayWithItems(tree, schema)
                tree?.forEach { item ->
                    visitArrayItemUnionTyped(item, schema["items"] as ArrayNode)
                    val matching = AirbyteJsonSchemaType.getMatchingValueForType(schema["items"] as ArrayNode, item)
                    visit(item, matching)
                }
                visitEndOfArrayWithItems(tree, schema)
            }
            AirbyteJsonSchemaType.ARRAY_WITH_ITEM -> {
                visitArrayWithSingleItem(tree, schema)
                val itemSchema = schema["items"] as ObjectNode
                tree?.forEach { item ->
                    visitArrayItemTyped(item, itemSchema)
                    visit(item, itemSchema)
                }
                visitEndOfArrayWithSingleItem(tree, schema)
            }
            AirbyteJsonSchemaType.ARRAY_WITHOUT_ITEMS -> {
                visitArrayWithoutItems(tree, schema)
                tree?.forEach { item ->
                    visitArrayItemUntyped(item)
                }
                visitEndOfArrayWithoutItems(tree, schema)
            }

            AirbyteJsonSchemaType.COMBINED -> {
                visitUnion(tree, schema)
                val options = MoreMappers.initMapper().createArrayNode()
                schema["type"].forEach { type ->
                    val option = MoreMappers.initMapper().createObjectNode()
                    option.put("type", type.asText())
                    options.add(option)
                }
                val matching = AirbyteJsonSchemaType.getMatchingValueForType(options, tree)
                visit(tree, matching)
                visitEndOfUnion(tree, schema)
            }

            AirbyteJsonSchemaType.UNION -> {
                visitUnion(tree, schema)
                val matching = AirbyteJsonSchemaType.getMatchingValueForType(schema["oneOf"] as ArrayNode, tree)
                visit(tree, matching)
                visitEndOfUnion(tree, schema)
            }

            AirbyteJsonSchemaType.BINARY_DATA -> {
                visitBinaryData(tree, schema)
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
