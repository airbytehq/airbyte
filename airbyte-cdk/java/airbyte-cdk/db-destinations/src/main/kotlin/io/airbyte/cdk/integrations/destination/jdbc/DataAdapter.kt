/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import java.util.function.Function
import java.util.function.Predicate

class DataAdapter
/**
 * Data adapter allows applying destination data rules. For example, Postgres destination can't
 * process text value with \u0000 unicode. You can describe filter condition for a value node and
 * function which adapts filtered value nodes.
 *
 * @param filterValueNode
 * - filter condition which decide which value node should be adapted
 * @param valueNodeAdapter
 * - transformation function which returns adapted value node
 */
(
    private val filterValueNode: Predicate<JsonNode>,
    private val valueNodeAdapter: Function<JsonNode, JsonNode>
) {
    fun adapt(messageData: JsonNode?) {
        if (messageData != null) {
            adaptAllValueNodes(messageData)
        }
    }

    private fun adaptAllValueNodes(rootNode: JsonNode) {
        adaptValueNodes(null, rootNode, null)
    }

    /**
     * The method inspects json node. In case, it's a value node we check the node by CheckFunction
     * and apply ValueNodeAdapter. Filtered nodes will be updated by adapted version. If element is
     * an array or an object, this we run the method recursively for them.
     *
     * @param fieldName Name of a json node
     * @param node Json node
     * @param parentNode Parent json node
     */
    private fun adaptValueNodes(fieldName: String?, node: JsonNode, parentNode: JsonNode?) {
        if (node.isValueNode && filterValueNode.test(node)) {
            if (fieldName != null) {
                val adaptedNode = valueNodeAdapter.apply(node)
                (parentNode as ObjectNode?)!!.set<JsonNode>(fieldName, adaptedNode)
            } else throw RuntimeException("Unexpected value node without fieldName. Node: $node")
        } else if (node.isArray) {
            node.elements().forEachRemaining { arrayNode: JsonNode ->
                adaptValueNodes(null, arrayNode, node)
            }
        } else {
            node.fields().forEachRemaining { stringJsonNodeEntry: Map.Entry<String?, JsonNode> ->
                adaptValueNodes(stringJsonNodeEntry.key, stringJsonNodeEntry.value, node)
            }
        }
    }
}
