package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers

class JsonSchemaAvroPreprocessor: JsonSchemaIdentityMapper() {
    override fun mapObjectWithoutProperties(schema: ObjectNode): JsonNode {
        val stringType = MoreMappers.initMapper().createObjectNode()
        stringType.put("type", "string")
        return stringType
    }
}
