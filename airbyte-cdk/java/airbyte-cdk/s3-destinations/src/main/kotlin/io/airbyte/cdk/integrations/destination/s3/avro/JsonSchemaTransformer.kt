package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers

open class JsonSchemaTransformer: JsonSchemaVisitor() {
    sealed class Context {
        data class PopulatingObject(
            val parent: ObjectNode,
            val properties: ObjectNode,
            val fieldName: String?
        ) : Context()

        data class SettingArrayType(
            val parent: ObjectNode
        ) : Context()

        data class AppendingToArray(
            val parent: ObjectNode,
            val array: ArrayNode
        ) : Context()
    }

    private var schemaOut: ObjectNode? = null

    private val contextStack: MutableList<Context> = mutableListOf()

    fun accept(schema: ObjectNode): ObjectNode {
        visit(schema)

        return schemaOut ?: throw IllegalStateException("Schema must be set")
    }

    protected fun add(node: ObjectNode) {
        if (contextStack.isEmpty()) {
            schemaOut = node
            return
        }

        when (val context = contextStack.last()) {
            is Context.PopulatingObject -> {
                if (context.fieldName == null) {
                    throw IllegalStateException("Field name must be set")
                }
                context.properties.set(context.fieldName, node)
            }
            is Context.SettingArrayType -> {
                context.parent.replace("items", node)
            }
            is Context.AppendingToArray -> {
                context.array.add(node)
            }
        }
    }

    private fun pushContext(context: Context) {
        contextStack.add(context)
    }

    private fun popContext(): Context {
        return contextStack.removeLast()
    }

    override fun visitObjectWithProperties(node: ObjectNode) {
        val objectNode = MoreMappers.initMapper().createObjectNode()
        val propertiesNode = MoreMappers.initMapper().createObjectNode()

        objectNode.put("type", "object")
        objectNode.replace("properties", propertiesNode)

        pushContext(Context.PopulatingObject(objectNode, propertiesNode, null))
    }

    override fun visitObjectProperty(name: String, node: ObjectNode) {
        val oldContext = popContext() as Context.PopulatingObject
        pushContext(Context.PopulatingObject(oldContext.parent, oldContext.properties, name))
    }

    override fun visitEndOfObjectWithProperties(node: ObjectNode) {
        val context = popContext() as Context.PopulatingObject
        add(context.parent)
    }

    override fun visitObjectWithoutProperties(node: ObjectNode) {
        add(node.deepCopy())
    }

    override fun visitArrayWithSingleItem(node: ObjectNode) {
        val arrayObjectNode = MoreMappers.initMapper().createObjectNode()
        arrayObjectNode.put("type", "array")
        pushContext(Context.SettingArrayType(arrayObjectNode))
    }

    override fun visitEndOfArrayWithSingleItem(node: ObjectNode) {
        val oldContext = popContext() as Context.SettingArrayType
        add(oldContext.parent)
    }

    override fun visitArrayWithItems(node: ObjectNode) {
        val arrayObjectNode = MoreMappers.initMapper().createObjectNode()
        val arrayNode = MoreMappers.initMapper().createArrayNode()

        arrayObjectNode.put("type", "array")
        arrayObjectNode.replace("items", arrayNode)

        pushContext(Context.AppendingToArray(arrayObjectNode, arrayNode))
    }

    override fun visitEndOfArrayWithItems(node: ObjectNode) {
        val oldContext = popContext() as Context.AppendingToArray
        add(oldContext.parent)
    }

    override fun visitArrayWithoutItems(node: ObjectNode) {
        add(node.deepCopy())
    }

    override fun visitString(node: ObjectNode) {
        add(node.deepCopy())
    }

    override fun visitBoolean(node: ObjectNode) {
        add(node.deepCopy())
    }

    override fun visitInteger(node: ObjectNode) {
        add(node.deepCopy())
    }

    override fun visitNumber(node: ObjectNode) {
       add(node.deepCopy())
    }

    override fun visitStartOfUnion(node: ObjectNode) {
        val union = MoreMappers.initMapper().createObjectNode()
        val options = MoreMappers.initMapper().createArrayNode()

        union.replace("oneOf", options)
        pushContext(Context.AppendingToArray(union, options))
    }

    override fun visitEndOfUnion(node: ObjectNode) {
        val oldContext = popContext() as Context.AppendingToArray
        add(oldContext.parent)
    }

    override fun visitDate(node: ObjectNode) {
        add(node.deepCopy())
    }

    override fun visitTimeWithTimezone(node: ObjectNode) {
        add(node.deepCopy())
    }

    override fun visitTimeWithoutTimezone(node: ObjectNode) {
        add(node.deepCopy())
    }

    override fun visitDateTimeWithTimezone(node: ObjectNode) {
        add(node.deepCopy())
    }

    override fun visitDateTimeWithoutTimezone(node: ObjectNode) {
        add(node.deepCopy())
    }
}
