package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers

class JsonSchemaAvroPreprocessor: JsonSchemaTransformer() {
    override fun visitObjectWithoutProperties(node: ObjectNode) {
        val stringNode = MoreMappers.initMapper().createObjectNode()
        stringNode.put("type", "string")
        add(stringNode)
    }
}
