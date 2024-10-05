/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.parquet

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.destination.s3.jsonschema.AirbyteJsonSchemaType
import io.airbyte.cdk.integrations.destination.s3.jsonschema.JsonSchemaIdentityMapper
import io.airbyte.commons.jackson.MoreMappers

class JsonSchemaParquetPreprocessor : JsonSchemaIdentityMapper() {
    companion object {
        fun typeFieldName(schema: ObjectNode): String {
            return when (AirbyteJsonSchemaType.fromJsonSchema(schema)) {
                AirbyteJsonSchemaType.NULL ->
                    throw IllegalStateException(
                        "Null typed fields in disjoint unions not supported"
                    )
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
                AirbyteJsonSchemaType.COMBINED ->
                    throw IllegalStateException("Nested unions are not supported")
                // Parquet has a native JSON type, which we would ideally use here.
                // Unfortunately, we're currently building parquet schemas via
                // Avro schemas, and Avro doesn't have a native JSON type.
                // So for now, we assume that the JsonSchemaAvroPreprocessor
                // was invoked before this preprocessor.
                AirbyteJsonSchemaType.UNKNOWN ->
                    throw IllegalStateException(
                        "JSON fields should be converted to string upstream of this processor"
                    )
            }
        }
    }

    private fun mapCommon(options: Sequence<JsonNode>): ObjectNode {
        val newSchema = MoreMappers.initMapper().createObjectNode()

        // Promote union to object
        newSchema.put("type", "object")

        // Add "type", a string field describing the type of the union
        val newProperties = MoreMappers.initMapper().createObjectNode()
        val typeObj = MoreMappers.initMapper().createObjectNode()
        // TODO: Temporary sentinel type to flag for the avro converter
        // that this should not be made optional. This is a hack and should
        // be replaced in the CDK by a first-class `optional` flag.
        typeObj.put("type", "type_name")
        newProperties.replace("type", typeObj)

        // Convert union options to named fields of the same type
        options.forEach { optionSchema ->
            val newOptionSchema = mapSchema(optionSchema as ObjectNode)
            val newFieldName = typeFieldName(newOptionSchema)
            newProperties.replace(newFieldName, newOptionSchema)
        }
        newSchema.replace("properties", newProperties)

        return newSchema
    }

    override fun mapUnion(schema: ObjectNode): ObjectNode {
        return mapCommon(schema["oneOf"].elements().asSequence())
    }

    override fun mapCombined(schema: ObjectNode): ObjectNode {
        val options =
            schema["type"].elements().asSequence().map {
                val typeObj = MoreMappers.initMapper().createObjectNode()
                typeObj.put("type", it.asText())
            }

        return mapCommon(options)
    }
}
