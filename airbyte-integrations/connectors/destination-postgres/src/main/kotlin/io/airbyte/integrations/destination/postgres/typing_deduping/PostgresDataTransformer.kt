/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.function.Function
import java.util.function.Predicate

class PostgresDataTransformer : StreamAwareDataTransformer {
    /*
     * This class is copied in its entirety from DataAdapter class to unify logic into one single
     * transformer invocation before serializing to string in AsyncStreamConsumer.
     */
    val filterValueNode: Predicate<JsonNode> = Predicate { jsonNode: JsonNode ->
        jsonNode.isTextual && jsonNode.textValue().contains("\u0000")
    }
    val valueNodeAdapter: Function<JsonNode, JsonNode> = Function { jsonNode: JsonNode ->
        val textValue = jsonNode.textValue().replace("\\u0000".toRegex(), "")
        jsonNode(textValue)
    }

    override fun transform(
        streamDescriptor: StreamDescriptor?,
        data: JsonNode?,
        meta: AirbyteRecordMessageMeta?
    ): Pair<JsonNode?, AirbyteRecordMessageMeta?> {
        val metaChanges: MutableList<AirbyteRecordMessageMetaChange> = ArrayList()
        if (meta != null && meta.changes != null) {
            metaChanges.addAll(meta.changes)
        }
        // Does inplace changes in the actual JsonNode reference.
        adapt(data)
        return Pair(data, AirbyteRecordMessageMeta().withChanges(metaChanges))
    }

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
