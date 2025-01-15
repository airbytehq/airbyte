/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.convert

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.data.TimestampValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownValue
import io.airbyte.cdk.load.util.TimeStringUtility.toLocalDate
import io.airbyte.cdk.load.util.TimeStringUtility.toLocalDateTime
import io.airbyte.cdk.load.util.TimeStringUtility.toOffset
import io.airbyte.integrations.destination.mssql.v2.MSSQLQueryBuilder
import io.airbyte.protocol.models.Jsons
import java.sql.Date
import java.sql.PreparedStatement
import java.sql.Time
import java.sql.Timestamp
import java.sql.Types

class AirbyteValueToStatement {
    companion object {
        private val toSqlType = AirbyteTypeToSqlType()
        private val toSqlValue = AirbyteValueToSqlValue()

        fun PreparedStatement.setValue(idx: Int, value: AirbyteValue?, field: MSSQLQueryBuilder.NamedField) {
            if (value != null && value !is NullValue && field.type.type is UnionType) {
                val objectValue = createUnionObject(field.type.type as UnionType, value)
                setAsJsonString(idx, objectValue)
            } else {
                when (value) {
                    is ArrayValue -> setAsJsonString(idx, value)
                    is BooleanValue -> setAsBooleanValue(idx, value)
                    is DateValue -> setAsDateValue(idx, value)
                    is IntegerValue -> setAsIntegerValue(idx, value)
                    NullValue -> setAsNullValue(idx, field.type.type)
                    is NumberValue -> setAsNumberValue(idx, value)
                    is ObjectValue -> setAsJsonString(idx, value)
                    is StringValue -> setAsStringValue(idx, value, field.type.type)
                    is TimeValue -> setAsTime(idx, value)
                    is TimestampValue -> setAsTimestamp(idx, value)
                    is UnknownValue -> setAsJsonString(idx, value)
                    null -> setAsNullValue(idx, field.type.type)
                }
            }
        }

        fun PreparedStatement.setAsNullValue(idx: Int, type: AirbyteType) {
            val sqlType = toSqlType.convert(type)
            setNull(idx, sqlType)
        }

        private fun PreparedStatement.setAsBooleanValue(idx: Int, value: BooleanValue) {
            setBoolean(idx, value.value)
        }

        private fun PreparedStatement.setAsDateValue(idx: Int, value: DateValue) {
            setDate(idx, Date.valueOf(toLocalDate(value.value)))
        }

        private fun PreparedStatement.setAsIntegerValue(idx: Int, value: IntegerValue) {
            setLong(idx, value.value.longValueExact())
        }

        private fun PreparedStatement.setAsJsonString(idx: Int, value: AirbyteValue) {
            setString(idx, Jsons.serialize(toSqlValue.convert(value)))
        }

        private fun PreparedStatement.setAsNumberValue(idx: Int, value: NumberValue) {
            setDouble(idx, value.value.toDouble())
        }

        private fun PreparedStatement.setAsStringValue(idx: Int, value: StringValue, type: AirbyteType) {
            val sqlType = toSqlType.convert(type)
            if (sqlType == Types.VARCHAR || sqlType == Types.LONGVARCHAR) {
                setString(idx, value.value)
            } else {
                throw IllegalArgumentException("$value isn't a $type")
            }
        }

        private fun PreparedStatement.setAsTime(idx: Int, value: TimeValue) {
            setTime(idx, Time.valueOf(toOffset(value.value)))
        }

        private fun PreparedStatement.setAsTimestamp(idx: Int, value: TimestampValue) {
            setTimestamp(idx, Timestamp.valueOf(toLocalDateTime(value.value)))
        }

        private fun createSimpleUnionObject(value: AirbyteValue): ObjectValue {
            val unionType = value.toTypeName()
            return ObjectValue.from(mapOf(
                "type" to StringValue(unionType),
                unionType to value
            ))
        }

        private fun createUnionObject(type: UnionType, value: AirbyteValue): AirbyteValue =
            if (type.options.all { it is ObjectType }) {
                val model = mutableMapOf<String, MutableSet<FieldType>>()
                    .withDefault { mutableSetOf() }

                type.options.map {
                    (it as ObjectType).properties.entries.forEach { objectEntry ->
                        if (model.containsKey(objectEntry.key)) {
                            model[objectEntry.key]!! += objectEntry.value
                        } else {
                            model[objectEntry.key] = mutableSetOf(objectEntry.value)
                        }
                    }
                }
                if (model.values.all { it.size == 1 }) {
                    value
                } else {
                    val valuesWithConflicts = (value as ObjectValue).values
                        .entries
                        .map { pair ->
                            if (model[pair.key]?.let { it.size > 1 } == true)
                                Pair(pair.key, createSimpleUnionObject(pair.value))
                            else
                                Pair(pair.key, pair.value)
                        }
                        .toMap()
                    ObjectValue.from(valuesWithConflicts)
                }
            } else {
                createSimpleUnionObject(value)
            }

        private fun AirbyteValue.toTypeName(): String = when (this) {
            is ArrayValue -> "array"
            is BooleanValue -> "boolean"
            is DateValue -> "string"
            is IntegerValue -> "integer"
            NullValue -> "null"
            is NumberValue -> "number"
            is ObjectValue -> "object"
            is StringValue -> "string"
            is TimeValue -> "string"
            is TimestampValue -> "string"
            is UnknownValue -> "oneOf"
        }
    }
}
