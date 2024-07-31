package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers
import org.apache.avro.data.Json

open class JsonRecordTransformer(
    private val inputRecordSchema: ObjectNode
): JsonRecordVisitor() {
    private var recordOut: JsonNode? = null
    private val contextStack: MutableList<Context> = mutableListOf()

    sealed class Context {
        data class PopulatingObject(
            val objectNode: ObjectNode,
            val fieldName: String? = null
        ) : Context()

        data class PopulatingArray(
            val arrayNode: ArrayNode
        ) : Context()

        object NullContainer: Context()
    }

    private fun pushContext(context: Context) {
        contextStack.add(context)
    }

    protected fun add(value: JsonNode?) {
        if (contextStack.isEmpty()) {
            recordOut = value
            return
        }

        when (val context = contextStack.last()) {
            is Context.PopulatingObject -> {
                if (context.fieldName == null) {
                    throw IllegalStateException("Field name must be set")
                }
                context.objectNode.set(context.fieldName, value)
            }
            is Context.PopulatingArray -> {
                context.arrayNode.add(value)
            }
            is Context.NullContainer -> {
                throw IllegalStateException("Cannot add a field to a null container")
            }
        }
    }

    protected open fun addObject(value: ObjectNode) {
        add(value)
    }

    protected open fun addArray(value: ArrayNode) {
        add(value)
    }

    protected open fun addUnionElement(value: JsonNode) {
        add(value)
    }

    private fun reset() {
        recordOut = null
        contextStack.clear()
    }

    fun accept(recordIn: JsonNode): JsonNode {
        reset()
        visit(recordIn, inputRecordSchema)
        return recordOut ?: throw IllegalStateException("Record must be set")
    }

    override fun visitObjectWithProperties(tree: JsonNode?, schema: ObjectNode) {
        println("At least here? object with? $schema")
        if (tree == null || tree.isNull) {
            return
        }

        val objectNode = MoreMappers.initMapper().createObjectNode()
        pushContext(Context.PopulatingObject(objectNode))
    }

    override fun visitObjectPropertyName(name: String, schema: ObjectNode) {
        val oldContext = contextStack.removeLast() as Context.PopulatingObject
        pushContext(Context.PopulatingObject(oldContext.objectNode, name))
    }

    override fun visitObjectAdditionalProperty(name: String, value: JsonNode) {
        println("what? $name $value")
        val currentContext = contextStack.last() as Context.PopulatingObject
        // There's nothing else we can do here since we don't have a schema.
        currentContext.objectNode.replace(name, value.deepCopy())
    }

    override fun visitEndOfObjectWithProperties(tree: JsonNode?, schema: ObjectNode) {
        if (tree == null || tree.isNull) {
            add(null)
            return
        }

        val oldContext = contextStack.removeLast() as Context.PopulatingObject
        addObject(oldContext.objectNode)
    }

    override fun visitObjectWithoutProperties(tree: JsonNode?, schema: ObjectNode) {
        // Nothing to do here since we don't have a schema.
        println("object without?")
        add(tree?.deepCopy())
    }

    private fun visitArrayCommon(tree: JsonNode?) {
        if (tree == null || tree.isNull) {
            return
        }

        val arrayNode = MoreMappers.initMapper().createArrayNode()
        pushContext(Context.PopulatingArray(arrayNode))
    }

    private fun visitArrayEndCommon(tree: JsonNode?) {
        if (tree == null || tree.isNull) {
            add(null)
            return
        }

        val oldContext = contextStack.removeLast() as Context.PopulatingArray
        addArray(oldContext.arrayNode)
    }

    override fun visitArrayWithSingleItem(tree: JsonNode?, schema: ObjectNode) {
        visitArrayCommon(tree)
    }

    override fun visitArrayItemUnionTyped(tree: JsonNode?, schema: ArrayNode) {
        // Do nothing: add the item when it is visited by type with its schema
    }

    override fun visitEndOfArrayWithSingleItem(tree: JsonNode?, schema: ObjectNode) {
        visitArrayEndCommon(tree)
    }

    override fun visitArrayWithItems(tree: JsonNode?, schema: ObjectNode) {
        visitArrayCommon(tree)
    }

    override fun visitArrayItemTyped(tree: JsonNode?, schema: ObjectNode) {
        // Do nothing: add the item when it is visited by type with its schema
    }

    override fun visitEndOfArrayWithItems(tree: JsonNode?, schema: ObjectNode) {
        visitArrayEndCommon(tree)
    }

    override fun visitArrayWithoutItems(tree: JsonNode?, schema: ObjectNode) {
        visitArrayCommon(tree)
    }

    override fun visitArrayItemUntyped(tree: JsonNode?) {
        // Nothing else to do here since we don't have a schema.
        add(tree?.deepCopy())
    }

    override fun visitEndOfArrayWithoutItems(tree: JsonNode?, schema: ObjectNode) {
        visitArrayEndCommon(tree)
    }

    override fun visitUnion(tree: JsonNode?, schema: ObjectNode) {
        // Nothing to do here by default, since at the record level a union is just a field.
    }

    override fun visitUnionItem(tree: JsonNode?, schema: ArrayNode) {
        // Do nothing: add the item when it is visited by type with its schema
    }

    override fun visitEndOfUnion(tree: JsonNode?, schema: ObjectNode) {
        // Nothing to do here by default, since at the record level a union is just a field.
    }

    override fun visitBinaryData(tree: JsonNode?, schema: ObjectNode) {
        add(tree?.deepCopy())
    }

    override fun visitString(tree: JsonNode?, schema: ObjectNode) {
        add(tree?.deepCopy())
    }

    override fun visitBoolean(tree: JsonNode?, schema: ObjectNode) {
        add(tree?.deepCopy())
    }

    override fun visitInteger(tree: JsonNode?, schema: ObjectNode) {
        add(tree?.deepCopy())
    }

    override fun visitNumber(tree: JsonNode?, schema: ObjectNode) {
        add(tree?.deepCopy())
    }

    override fun visitDate(tree: JsonNode?, schema: ObjectNode) {
        add(tree?.deepCopy())
    }

    override fun visitTimestampWithTimezone(tree: JsonNode?, schema: ObjectNode) {
        add(tree?.deepCopy())
    }

    override fun visitTimestampWithoutTimezone(tree: JsonNode?, schema: ObjectNode) {
        add(tree?.deepCopy())
    }

    override fun visitTimeWithTimezone(tree: JsonNode?, schema: ObjectNode) {
        add(tree?.deepCopy())
    }

    override fun visitTimeWithoutTimezone(tree: JsonNode?, schema: ObjectNode) {
        add(tree?.deepCopy())
    }
}
