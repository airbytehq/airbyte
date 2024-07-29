package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers

class JsonRecordTransformer: JsonRecordVisitor() {
    private var recordOut: ObjectNode? = null
    private val contextStack: MutableList<Context> = mutableListOf()

    sealed class Context {
        data class PopulatingObject(
            val objectNode: ObjectNode,
        ) : Context()

        data class SettingObjectProperty(
            val objectNode: ObjectNode,
            val fieldName: String,
        ) : Context()
    }

    private fun pushContext(context: Context) {
        contextStack.add(context)
    }

    fun add(value: JsonNode) {
        if (recordOut == null) {
            recordOut = node
        }
    }

    fun accept(recordIn: JsonNode, schema: ObjectNode): ObjectNode {
        visit(recordIn, schema)
        return schema
    }

    override fun visitObjectWithProperties(tree: JsonNode, schema: ObjectNode) {
        val objectNode = MoreMappers.initMapper().createObjectNode()
        pushContext(Context.PopulatingObject(objectNode))
    }

    override fun visitObjectProperty(tree: JsonNode, name: String, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitEndOfObjectWithProperties(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitObjectWithoutProperties(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitArrayWithSingleItem(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitArrayItemUnionTyped(tree: JsonNode, schema: ArrayNode) {
        TODO("Not yet implemented")
    }

    override fun visitEndOfArrayWithSingleItem(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitArrayWithItems(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitArrayItemTyped(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitEndOfArrayWithItems(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitArrayWithoutItems(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitArrayItemUntyped(tree: JsonNode) {
        TODO("Not yet implemented")
    }

    override fun visitEndOfArrayWithoutItems(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitUnion(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitUnionItem(tree: JsonNode, schema: ArrayNode) {
        TODO("Not yet implemented")
    }

    override fun visitEndOfUnion(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitString(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitBoolean(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitInteger(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitNumber(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitDate(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitTimestampWithTimezone(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitTimestampWithoutTimezone(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitTimeWithTimezone(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

    override fun visitTimeWithoutTimezone(tree: JsonNode, schema: ObjectNode) {
        TODO("Not yet implemented")
    }

}
