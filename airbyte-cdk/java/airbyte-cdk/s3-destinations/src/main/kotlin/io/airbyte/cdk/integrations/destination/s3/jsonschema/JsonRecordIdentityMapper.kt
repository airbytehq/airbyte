/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.jsonschema

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.commons.jackson.MoreMappers

open class JsonRecordIdentityMapper : JsonRecordMapper<JsonNode?>() {
    override fun mapNull(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }

    override fun mapBoolean(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }

    override fun mapInteger(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }

    override fun mapNumber(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }

    override fun mapString(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }

    override fun mapBinaryData(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }

    override fun mapDate(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }

    override fun mapDateTimeWithTimezone(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }

    override fun mapDateTimeWithoutTimezone(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }

    override fun mapTimeWithTimezone(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }

    override fun mapTimeWithoutTimezone(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }

    override fun mapArrayWithoutItems(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }

    override fun mapArrayWithItem(record: JsonNode?, schema: ObjectNode): JsonNode? {
        if (record == null || record.isNull) {
            return null
        }

        val newArray = MoreMappers.initMapper().createArrayNode()
        record.forEach { item ->
            val newItem = mapRecordWithSchema(item, schema["items"] as ObjectNode)
            newArray.add(newItem)
        }
        return newArray
    }

    override fun mapArrayWithItems(record: JsonNode?, schema: ObjectNode): JsonNode? {
        if (record == null || record.isNull) {
            return null
        }

        val newArray = MoreMappers.initMapper().createArrayNode()
        record.forEach { item ->
            if (item == null || item.isNull) {
                newArray.add(JsonNodeFactory.instance.nullNode())
            } else {
                val match =
                    AirbyteJsonSchemaType.getMatchingValueForType(
                        item,
                        schema["items"] as ArrayNode
                    )
                val newItem = mapRecordWithSchema(item, match)
                newArray.add(newItem)
            }
        }
        return newArray
    }

    override fun mapObjectWithoutProperties(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }

    override fun mapObjectWithProperties(record: JsonNode?, schema: ObjectNode): JsonNode? {
        if (record == null || record.isNull) {
            return null
        }

        val newRecord = MoreMappers.initMapper().createObjectNode()

        // TODO: Additional properties?
        schema["properties"].fields().forEach { (propertyName, propertySchema) ->
            if (record.has(propertyName)) {
                val oldValue = record[propertyName]
                val newValue = mapRecordWithSchema(oldValue, propertySchema as ObjectNode)
                newRecord.replace(propertyName, newValue)
            }
        }

        return newRecord
    }

    override fun mapUnion(record: JsonNode?, schema: ObjectNode): JsonNode? {
        if (record == null || record.isNull) {
            return null
        }

        val match =
            AirbyteJsonSchemaType.getMatchingValueForType(record, schema["oneOf"] as ArrayNode)
        return mapRecordWithSchema(record, match)
    }

    override fun mapCombined(record: JsonNode?, schema: ObjectNode): JsonNode? {
        if (record == null || record.isNull) {
            return null
        }

        val options =
            schema["type"]
                .elements()
                .asSequence()
                .map {
                    val typeObj = MoreMappers.initMapper().createObjectNode()
                    typeObj.put("type", it.asText())
                }
                .toList()
        val match = AirbyteJsonSchemaType.getMatchingValueForType(record, options)
        return mapRecordWithSchema(record, match)
    }

    override fun mapUnknown(record: JsonNode?, schema: ObjectNode): JsonNode? {
        return record?.deepCopy()
    }
}
