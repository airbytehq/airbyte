package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers

class AvroJsonRecordPreprocessor(
    inputRecordSchema: ObjectNode
): JsonRecordTransformer(inputRecordSchema) {
    override fun visitObjectWithoutProperties(tree: JsonNode?, schema: ObjectNode) {
        println("HERE TOO: $tree")
        if (tree == null) {
            return
        }

        val treeAsString = MoreMappers.initMapper().writeValueAsString(tree)
        val stringNode = JsonNodeFactory.instance.textNode(treeAsString)
        add(stringNode)
    }
}
