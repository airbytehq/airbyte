package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers

class ParquetJsonRecordPreprocessor(
    inputRecordSchema: ObjectNode
): JsonRecordTransformer(inputRecordSchema) {
    data class Context(
        val disjointObject: ObjectNode? = null
    )
    private val stack = mutableListOf<Context>()
    private val settingUnionItem = stack.lastOrNull()?.disjointObject != null

    override fun visitUnion(tree: JsonNode?, schema: ObjectNode) {
        val disjointObject = MoreMappers.initMapper().createObjectNode()
        stack.add(Context(disjointObject))
    }

    override fun visitEndOfUnion(tree: JsonNode?, schema: ObjectNode) {
        val context = stack.removeLast()
        add(context.disjointObject!!)
    }

    override fun visitObjectWithProperties(tree: JsonNode?, schema: ObjectNode) {
        stack.add(Context())
        super.visitObjectWithProperties(tree, schema)
    }

    override fun visitEndOfObjectWithProperties(tree: JsonNode?, schema: ObjectNode) {
        stack.removeLast()
        super.visitEndOfObjectWithProperties(tree, schema)
    }

    override fun visitArrayWithItems(tree: JsonNode?, schema: ObjectNode) {
        stack.add(Context())
        super.visitArrayWithItems(tree, schema)
    }

    override fun visitEndOfArrayWithItems(tree: JsonNode?, schema: ObjectNode) {
        stack.removeLast()
        super.visitEndOfArrayWithItems(tree, schema)
    }

    override fun visitArrayWithSingleItem(tree: JsonNode?, schema: ObjectNode) {
        stack.add(Context())
        super.visitArrayWithSingleItem(tree, schema)
    }

    override fun visitEndOfArrayWithSingleItem(tree: JsonNode?, schema: ObjectNode) {
        stack.removeLast()
        super.visitEndOfArrayWithSingleItem(tree, schema)
    }

    override fun add

    private fun setUnionItem(typeName: String, tree: JsonNode?) {
        val disjointObject = stack.last().disjointObject!!
        disjointObject.replace(typeName, tree)
    }

    override fun visitBoolean(tree: JsonNode?, schema: ObjectNode) {
        if (settingUnionItem) {
            setUnionItem("boolean", tree?.deepCopy())
        } else {
            super.visitBoolean(tree, schema)
        }
    }

    override fun visitNumber(tree: JsonNode?, schema: ObjectNode) {
        if (settingUnionItem) {
            setUnionItem("number", tree?.deepCopy())
        } else {
            super.visitNumber(tree, schema)
        }
    }

    override fun visitInteger(tree: JsonNode?, schema: ObjectNode) {
        if (settingUnionItem) {
            setUnionItem("integer", tree?.deepCopy())
        } else {
            super.visitInteger(tree, schema)
        }
    }

    override fun visitString(tree: JsonNode?, schema: ObjectNode) {
        if (settingUnionItem) {
            setUnionItem("string", tree?.deepCopy())
        } else {
            super.visitString(tree, schema)
        }
    }

    override fun visitBinaryData(tree: JsonNode?, schema: ObjectNode) {
        if (settingUnionItem) {
            setUnionItem("binary", tree?.deepCopy())
        } else {
            super.visitBinaryData(tree, schema)
        }
    }

    override fun visitObjectWithoutProperties(tree: JsonNode?, schema: ObjectNode) {
        if (settingUnionItem) {
            setUnionItem("object", tree?.deepCopy())
        } else {
            super.visitObjectWithoutProperties(tree, schema)
        }
    }
}
