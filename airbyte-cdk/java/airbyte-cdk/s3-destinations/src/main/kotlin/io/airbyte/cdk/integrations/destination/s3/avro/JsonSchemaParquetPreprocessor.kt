package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers

class JsonSchemaParquetPreprocessor: JsonSchemaIdentityMapper() {
    companion object {
        fun typeFieldName(schema: ObjectNode): String {
            return when (AirbyteJsonSchemaType.fromJsonSchema(schema)) {
                AirbyteJsonSchemaType.BOOLEAN -> "boolean"
                AirbyteJsonSchemaType.INTEGER -> "integer"
                AirbyteJsonSchemaType.NUMBER -> "number"
                AirbyteJsonSchemaType.STRING -> "string"
                AirbyteJsonSchemaType.BINARY_DATA -> "binary"
                AirbyteJsonSchemaType.DATE -> "date"
                AirbyteJsonSchemaType.TIMESTAMP_WITH_TIMEZONE -> "timestamp_with_timezone"
                AirbyteJsonSchemaType.TIMESTAMP_WITHOUT_TIMEZONE -> "timestamp_without_timezone"
                AirbyteJsonSchemaType.TIME_WITH_TIMEZONE -> "time_with_timezone"
                AirbyteJsonSchemaType.TIME_WITHOUT_TIMEZONE -> "time_without_timezone"
                AirbyteJsonSchemaType.ARRAY_WITHOUT_ITEMS,
                AirbyteJsonSchemaType.ARRAY_WITH_ITEM,
                AirbyteJsonSchemaType.ARRAY_WITH_ITEMS -> "array"

                AirbyteJsonSchemaType.OBJECT_WITHOUT_PROPERTIES,
                AirbyteJsonSchemaType.OBJECT_WITH_PROPERTIES -> "object"

                AirbyteJsonSchemaType.UNION,
                AirbyteJsonSchemaType.COMBINED -> throw IllegalStateException("Nested unions are not supported")
            }
        }
    }

    private fun mapCommon(options: Sequence<JsonNode>): ObjectNode {
        val newSchema = MoreMappers.initMapper().createObjectNode()

        // Promote union to object
        newSchema.put("type", "object")

        // Add _airbyte_type: string field
        val newProperties = MoreMappers.initMapper().createObjectNode()
        val typeObj = MoreMappers.initMapper().createObjectNode()
        typeObj.put("type", "string")
        newProperties.replace("_airbyte_type", typeObj)

        // Convert union options to named fields of the same type
        options.forEach { optionSchema ->
            val newOptionSchema = mapSchema(optionSchema as ObjectNode)
            val newFieldName = typeFieldName(newOptionSchema as ObjectNode)
            newProperties.replace(newFieldName, newOptionSchema)
        }
        newSchema.replace("properties", newProperties)

        return newSchema
    }

    override fun mapUnion(schema: ObjectNode): JsonNode {
        return mapCommon(schema["oneOf"].elements().asSequence())
    }

    override fun mapCombined(schema: ObjectNode): JsonNode {
        val options = schema["type"].elements().asSequence().map {
            val typeObj = MoreMappers.initMapper().createObjectNode()
            typeObj.put("type", it.asText())
        }

        return mapCommon(options)
    }
}
