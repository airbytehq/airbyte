package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers

class JsonRecordParquetPreprocessor: JsonRecordIdentityMapper() {
    private fun mapCommon(record: JsonNode?, matchingOption: ObjectNode): JsonNode? {
        val newObj = MoreMappers.initMapper().createObjectNode()

        val propertyName = JsonSchemaParquetPreprocessor.typeFieldName(matchingOption)
        val propertyValue = mapRecordWithSchema(record, matchingOption)

        newObj.put("_airbyte_type", propertyName)
        newObj.replace(propertyName, propertyValue)

        return newObj
    }

    override fun mapUnion(record: JsonNode?, schema: ObjectNode): JsonNode? {
        if (record == null || record.isNull) {
            return null
        }

        val matchingOption = AirbyteJsonSchemaType.getMatchingValueForType(record, schema["oneOf"] as ArrayNode)

        return mapCommon(record, matchingOption)
    }

    override fun mapCombined(record: JsonNode?, schema: ObjectNode): JsonNode? {
        if (record == null || record.isNull) {
            return null
        }

        println("FINAL FORM: $record, $schema")
        val options = schema["type"].elements().asSequence().map {
            println("it: $it")
            val typeObj = MoreMappers.initMapper().createObjectNode()
            typeObj.put("type", it.asText()) as ObjectNode
        }.toList()
        val matchingOption = AirbyteJsonSchemaType.getMatchingValueForType(record, options)
        return mapCommon(record, matchingOption)
    }
}
