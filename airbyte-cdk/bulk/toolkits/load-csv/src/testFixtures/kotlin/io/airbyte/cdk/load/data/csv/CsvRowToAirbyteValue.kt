/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.csv

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.data.UnknownValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.util.deserializeToNode
import org.apache.commons.csv.CSVRecord

class CsvRowToAirbyteValue {
    fun convert(row: CSVRecord, schema: AirbyteType): AirbyteValue {
        if (schema !is ObjectType) {
            throw IllegalArgumentException("Only object types are supported")
        }
        val asList = row.toList()
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
        if (value.isBlank()) {
            return NullValue
        }
        return try {
            when (field) {
                is ArrayType -> {
                    value
                        .deserializeToNode()
                        .elements()
                        .asSequence()
                        .map { it.toAirbyteValue(field.items.type) }
                        .toList()
                        .let(::ArrayValue)
                }
                is ArrayTypeWithoutSchema ->
                    value.deserializeToNode().toAirbyteValue(ArrayTypeWithoutSchema)
                is BooleanType -> BooleanValue(value.toBooleanStrict())
                is IntegerType -> IntegerValue(value.toBigInteger())
                is NumberType -> NumberValue(value.toBigDecimal())
                is ObjectType -> {
                    val properties = linkedMapOf<String, AirbyteValue>()
                    value
                        .deserializeToNode()
                        .fields()
                        .asSequence()
                        .map { entry ->
                            val type =
                                field.properties[entry.key]?.type
                                    ?: UnknownType(value.deserializeToNode())
                            entry.key to entry.value.toAirbyteValue(type)
                        }
                        .toMap(properties)
                    ObjectValue(properties)
                }
                is ObjectTypeWithEmptySchema ->
                    value.deserializeToNode().toAirbyteValue(ObjectTypeWithEmptySchema)
                is ObjectTypeWithoutSchema ->
                    value.deserializeToNode().toAirbyteValue(ObjectTypeWithoutSchema)
                is StringType -> StringValue(value)
                is UnionType -> {
                    // Use the options sorted with string last since it always works
                    field.options
                        .sortedBy { it is StringType }
                        .firstNotNullOfOrNull { option ->
                            try {
                                convertInner(value, option)
                            } catch (e: Exception) {
                                null
                            }
                        }
                        ?: NullValue
                }
                DateType -> DateValue(value)
                TimeTypeWithTimezone,
                TimeTypeWithoutTimezone -> TimeValue(value)
                TimestampTypeWithTimezone,
                TimestampTypeWithoutTimezone -> TimestampValue(value)
                is UnknownType -> UnknownValue(value.deserializeToNode())
            }
        } catch (e: Exception) {
            StringValue(value)
        }
    }
}

fun CSVRecord.toAirbyteValue(schema: AirbyteType): AirbyteValue {
    return CsvRowToAirbyteValue().convert(this, schema)
}
