/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.csv

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.util.deserializeToNode
import org.apache.commons.csv.CSVRecord

class CsvRowToAirbyteValue {
    fun convert(row: CSVRecord, schema: AirbyteType): AirbyteValue {
        if (schema !is ObjectType) {
            throw IllegalArgumentException("Only object types are supported")
        }
        val asList = row.toList()
        if (asList.size != schema.properties.size) {
            throw IllegalArgumentException("Row size does not match schema size")
        }
        val properties = linkedMapOf<String, AirbyteValue>()
        schema.properties
            .toList()
            .zip(asList)
            .map { (property, value) ->
                property.first to convertInner(value, property.second.type)
            }
            .toMap(properties)
        return ObjectValue(properties)
    }

    private fun convertInner(value: String, field: AirbyteType): AirbyteValue {
        return when (field) {
            is ArrayType ->
                value
                    .deserializeToNode()
                    .elements()
                    .asSequence()
                    .map { it.toAirbyteValue(field.items.type) }
                    .toList()
                    .let(::ArrayValue)
            is BooleanType -> BooleanValue(value.toBoolean())
            is IntegerType -> IntegerValue(value.toLong())
            is NumberType -> NumberValue(value.toBigDecimal())
            is ObjectType -> {
                val properties = linkedMapOf<String, AirbyteValue>()
                value
                    .deserializeToNode()
                    .fields()
                    .asSequence()
                    .map { entry ->
                        entry.key to entry.value.toAirbyteValue(field.properties[entry.key]!!.type)
                    }
                    .toMap(properties)
                ObjectValue(properties)
            }
            is ObjectTypeWithoutSchema ->
                value.deserializeToNode().toAirbyteValue(ObjectTypeWithoutSchema)
            is StringType -> StringValue(value)
            else -> throw IllegalArgumentException("Unsupported field type: $field")
        }
    }
}

fun CSVRecord.toAirbyteValue(schema: AirbyteType): AirbyteValue {
    return CsvRowToAirbyteValue().convert(this, schema)
}
