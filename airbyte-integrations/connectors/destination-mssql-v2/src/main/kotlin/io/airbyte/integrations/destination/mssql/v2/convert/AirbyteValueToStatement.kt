/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.convert

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.data.TimestampValue
import io.airbyte.cdk.load.data.UnknownValue
import io.airbyte.cdk.load.util.TimeStringUtility.toLocalDate
import io.airbyte.cdk.load.util.TimeStringUtility.toLocalDateTime
import io.airbyte.cdk.load.util.TimeStringUtility.toOffset
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

        fun PreparedStatement.setValue(idx: Int, value: AirbyteValue?, type: AirbyteType) {
            when (value) {
                is ArrayValue -> setAsJsonString(idx, value)
                is BooleanValue -> setAsBooleanValue(idx, value)
                is DateValue -> setAsDateValue(idx, value)
                is IntegerValue -> setAsIntegerValue(idx, value)
                NullValue -> setAsNullValue(idx, type)
                is NumberValue -> setAsNumberValue(idx, value)
                is ObjectValue -> setAsJsonString(idx, value)
                is StringValue -> setAsStringValue(idx, value, type)
                is TimeValue -> setAsTime(idx, value)
                is TimestampValue -> setAsTimestamp(idx, value)
                is UnknownValue -> setAsJsonString(idx, value)
                null -> setAsNullValue(idx, type)
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
    }
}
