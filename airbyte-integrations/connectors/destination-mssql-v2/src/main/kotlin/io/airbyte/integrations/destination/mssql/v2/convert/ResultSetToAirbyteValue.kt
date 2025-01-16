/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.convert

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
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.integrations.destination.mssql.v2.MSSQLQueryBuilder
import io.airbyte.integrations.destination.mssql.v2.MSSQLQueryBuilder.NamedValue
import io.airbyte.protocol.models.Jsons
import java.sql.ResultSet
import java.sql.Timestamp
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter

class ResultSetToAirbyteValue {
    companion object {
        fun ResultSet.getAirbyteNamedValue(field: MSSQLQueryBuilder.NamedField): NamedValue =
            when (field.type.type) {
                is StringType -> getStringValue(field.name)
                is ArrayType -> getArrayValue(field.name)
                ArrayTypeWithoutSchema -> getArrayValue(field.name)
                BooleanType -> getBooleanValue(field.name)
                DateType -> getDateValue(field.name)
                IntegerType -> getIntegerValue(field.name)
                NumberType -> getNumberValue(field.name)
                is ObjectType -> getObjectValue(field.name)
                ObjectTypeWithEmptySchema -> getObjectValue(field.name)
                ObjectTypeWithoutSchema -> getObjectValue(field.name)
                TimeTypeWithTimezone -> getTimeWithTimezoneValue(field.name)
                TimeTypeWithoutTimezone -> getTimeWithoutTimezoneValue(field.name)
                TimestampTypeWithTimezone -> getTimestampWithTimezoneValue(field.name)
                TimestampTypeWithoutTimezone -> getTimestampWithoutTimezoneValue(field.name)
                is UnionType -> getObjectValue(field.name)
                is UnknownType -> getStringValue(field.name)
            }

        private fun ResultSet.getArrayValue(name: String): NamedValue =
            getNullable(name, this::getString)
                ?.let { ArrayValue.from(deserialize<List<Any?>>(it)) }
                .toNamedValue(name)

        private fun ResultSet.getBooleanValue(name: String): NamedValue =
            getNullable(name, this::getBoolean)?.let { BooleanValue(it) }.toNamedValue(name)

        private fun ResultSet.getDateValue(name: String): NamedValue =
            getNullable(name, this::getDate)?.let { DateValue(it.toString()) }.toNamedValue(name)

        private fun ResultSet.getIntegerValue(name: String): NamedValue =
            getNullable(name, this::getLong)?.let { IntegerValue(it) }.toNamedValue(name)

        private fun ResultSet.getNumberValue(name: String): NamedValue =
            getNullable(name, this::getDouble)
                ?.let { NumberValue(it.toBigDecimal()) }
                .toNamedValue(name)

        private fun ResultSet.getObjectValue(name: String): NamedValue =
            getNullable(name, this::getString)
                ?.let { ObjectValue.from(deserialize<Map<String, Any?>>(it)) }
                .toNamedValue(name)

        private fun ResultSet.getStringValue(name: String): NamedValue =
            getNullable(name, this::getString)?.let { StringValue(it) }.toNamedValue(name)

        private fun ResultSet.getTimeWithTimezoneValue(name: String): NamedValue =
            getNullable(name, this::getString)?.toTimeWithTimezone().toNamedValue(name)

        private fun ResultSet.getTimeWithoutTimezoneValue(name: String): NamedValue =
            getNullable(name, this::getString)?.toTimeWithoutTimezone().toNamedValue(name)

        private fun ResultSet.getTimestampWithTimezoneValue(name: String): NamedValue =
            getNullable(name, this::getString)?.toTimestampWithTimezone().toNamedValue(name)

        private fun ResultSet.getTimestampWithoutTimezoneValue(name: String): NamedValue =
            getNullable(name, this::getString)?.toTimestampWithoutTimezone().toNamedValue(name)

        private fun AirbyteValue?.toNamedValue(name: String): NamedValue =
            if (this != null) NamedValue(name, this) else NamedValue(name, NullValue)

        private fun <T> ResultSet.getNullable(name: String, getter: (String) -> T): T? {
            val value = getter(name)
            return if (wasNull()) null else value
        }

        private inline fun <reified T> deserialize(value: String): T =
            Jsons.deserialize(value, T::class.java)

        internal fun String.toTimeWithTimezone(): TimeWithTimezoneValue =
            TimeWithTimezoneValue(
                OffsetDateTime.parse(
                        this,
                        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSSSSSS XXX")
                    )
                    .toOffsetTime()
                    .toString()
            )

        internal fun String.toTimeWithoutTimezone(): TimeWithoutTimezoneValue =
            TimeWithoutTimezoneValue(LocalTime.parse(this).toString())

        internal fun String.toTimestampWithTimezone(): TimestampWithTimezoneValue =
            TimestampWithTimezoneValue(
                OffsetDateTime.parse(
                        this,
                        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSSSSSS XXX")
                    )
                    .toString()
            )

        internal fun String.toTimestampWithoutTimezone(): TimestampWithoutTimezoneValue =
            TimestampWithoutTimezoneValue(Timestamp.valueOf(this).toLocalDateTime().toString())
    }
}
