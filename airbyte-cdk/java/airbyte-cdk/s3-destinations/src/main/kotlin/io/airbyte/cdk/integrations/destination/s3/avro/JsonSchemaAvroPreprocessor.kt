/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.destination.s3.jsonschema.AirbyteJsonSchemaType
import io.airbyte.cdk.integrations.destination.s3.jsonschema.JsonSchemaIdentityMapper
import io.airbyte.commons.jackson.MoreMappers

class JsonSchemaAvroPreprocessor : JsonSchemaIdentityMapper() {
    companion object {
        val STRING_TYPE: ObjectNode =
            MoreMappers.initMapper().createObjectNode().put("type", "string")
    }

    override fun mapObjectWithoutProperties(schema: ObjectNode): ObjectNode {
        return STRING_TYPE
    }

    override fun mapArrayWithoutItems(schema: ObjectNode): ObjectNode {
        return STRING_TYPE
    }

    override fun mapArrayWithItem(schema: ObjectNode): ObjectNode {
        val items = schema["items"] as ObjectNode
        val itemType = AirbyteJsonSchemaType.fromJsonSchema(items)

        // Promote an array of unions (unsupported) to an array of mixed types (supported)
        // NOTE: There's no corresponding record mapping, because the data are the same in both
        // cases.
        if (itemType == AirbyteJsonSchemaType.UNION || itemType == AirbyteJsonSchemaType.COMBINED) {
            val newArrayObj = MoreMappers.initMapper().createObjectNode()
            newArrayObj.put("type", "array")
            val newItems = MoreMappers.initMapper().createArrayNode()
            val options =
                if (itemType == AirbyteJsonSchemaType.UNION) items["oneOf"] as ArrayNode
                else
                    items["type"].map { typeName ->
                        val typeObj = MoreMappers.initMapper().createObjectNode()
                        typeObj.put("type", typeName.asText())
                    }
            options.forEach { option -> newItems.add(option) }
            newArrayObj.replace("items", newItems)

            return newArrayObj
        }

        return super.mapArrayWithItem(schema)
    }

    override fun mapUnknown(schema: ObjectNode): ObjectNode {
        return STRING_TYPE
    }
}
