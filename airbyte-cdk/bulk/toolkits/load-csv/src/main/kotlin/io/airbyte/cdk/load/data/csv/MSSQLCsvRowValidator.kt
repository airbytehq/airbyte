/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.csv

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime

private object LIMITS {
    // Maximum value for BIGINT in SQL Server
    val MAX_BIGINT = BigInteger("9223372036854775807")

    val TRUE = IntegerValue(1)
    val FALSE = IntegerValue(0)
}

/**
 * Creates a validator for MSSQL CSV rows.
 *
 * @param validateValuesPreLoad Whether to validate string values before loading them into the csv
 * file.
 * ```
 *                             This is optional and disabled by default as it's a computationally
 *                             expensive operation that can significantly impact performance.
 *                             Only enable if strict data validation is required.
 * ```
 */
class MSSQLCsvRowValidator(private val validateValuesPreLoad: Boolean) {

    fun validate(
        record: DestinationRecordAirbyteValue,
        schema: ObjectType
    ): DestinationRecordAirbyteValue {
        val objectValue = record.data as? ObjectValue ?: return record
        val values = objectValue.values

        schema.properties.forEach { (columnName, fieldType) ->
            val oldValue = values[columnName]
            if (oldValue != null && oldValue !is NullValue && record.meta != null) {
                values[columnName] =
                    oldValue.validateAndReplace(columnName, fieldType, record.meta!!)
            }
        }
        return record
    }

    private fun AirbyteValue.validateAndReplace(
        columnName: String,
        fieldType: FieldType,
        meta: Meta
    ): AirbyteValue =
        when (this) {
            is StringValue -> validateStringValue(columnName, this, fieldType, meta)
            is IntegerValue -> validateIntegerValue(columnName, this, meta)
            is BooleanValue -> validateBooleanValue(this)
            is NumberValue -> validateNumberValue(this)
            is ObjectValue -> validateObjectValue(this, fieldType, meta)
            else -> this
        }

    private fun validateStringValue(
        columnName: String,
        value: StringValue,
        fieldType: FieldType,
        meta: Meta
    ): AirbyteValue {
        if (!validateValuesPreLoad || fieldType.isStringColumn()) {
            return value
        }

        val rawString = value.value

        if (fieldType.isNumericColumn()) {
            return runCatching { NumberValue(rawString.toBigDecimal()) }
                .fold(
                    onSuccess = { validateNumberValue(it) },
                    onFailure = {
                        meta.nullify(
                            columnName,
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
                        )
                        NullValue
                    }
                )
        } else if (fieldType.isBooleanColumn()) {
            val asIntValue = parseBooleanAsIntValue(rawString)
            if (asIntValue == null) {
                meta.nullify(
                    columnName,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
                )
                return NullValue
            }
            return asIntValue
        } else if (fieldType.isDateColumn()) {
            if (!safeParseDate(rawString)) {
                meta.nullify(
                    columnName,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
                )
                return NullValue
            }
        } else if (fieldType.isTimeColumn()) {
            if (!safeParseTime(rawString)) {
                meta.nullify(
                    columnName,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
                )
                return NullValue
            }
        } else if (fieldType.isTimestampColumn()) {
            if (!safeParseTimestamp(rawString)) {
                meta.nullify(
                    columnName,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
                )
                return NullValue
            }
        } else if (fieldType.isUnionColumn()) {
            return StringValue(Jsons.serialize(rawString))
        }
        return value
    }

    private fun validateIntegerValue(
        columnName: String,
        value: IntegerValue,
        meta: Meta
    ): AirbyteValue {
        // If the integer is bigger than BIGINT, then we must nullify it.
        if (value.value > LIMITS.MAX_BIGINT) {
            meta.nullify(
                columnName,
                AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
            )
            return NullValue
        }
        return value
    }

    private fun validateBooleanValue(value: BooleanValue): IntegerValue {
        return if (value.value) LIMITS.TRUE else LIMITS.FALSE
    }

    private fun validateNumberValue(value: NumberValue): NumberValue {
        // Force to BigDecimal -> re-box as NumberValue
        return NumberValue(value.value.toDouble().toBigDecimal())
    }

    private fun validateObjectValue(
        value: ObjectValue,
        fieldType: FieldType,
        meta: Meta
    ): ObjectValue {
        // If the schema says it's actually an object, we recursively validate.
        val actualObjType = fieldType.type
        if (actualObjType is ObjectType) {
            val convertedValues = LinkedHashMap<String, AirbyteValue>(value.values.size)
            value.values.forEach { (propName, propValue) ->
                val subType = actualObjType.properties[propName]
                val validated =
                    if (subType != null) propValue.validateAndReplace(propName, subType, meta)
                    else propValue
                convertedValues[propName] = validated
            }
            return ObjectValue(convertedValues)
        }
        return value
    }

    private fun parseBooleanAsIntValue(value: String): IntegerValue? {
        // Accept "1", "0", or strict booleans ("true"/"false")
        return when (value) {
            "1" -> LIMITS.TRUE
            "0" -> LIMITS.FALSE
            else -> {
                val bool = value.lowercase().toBooleanStrictOrNull() ?: return null
                if (bool) LIMITS.TRUE else LIMITS.FALSE
            }
        }
    }

    private fun safeParseDate(value: String): Boolean {
        return runCatching { LocalDate.parse(value) }.isSuccess
    }

    private fun safeParseTime(value: String): Boolean {
        if (runCatching { OffsetTime.parse(value) }.isSuccess) return true
        return runCatching { LocalTime.parse(value) }.isSuccess
    }

    private fun safeParseTimestamp(value: String): Boolean {
        if (runCatching { OffsetDateTime.parse(value) }.isSuccess) return true
        return runCatching { LocalDateTime.parse(value) }.isSuccess
    }

    private fun FieldType.isNumericColumn(): Boolean {
        return type is NumberType || type is IntegerType
    }

    private fun FieldType.isStringColumn(): Boolean {
        return type is StringType
    }

    private fun FieldType.isUnionColumn(): Boolean {
        return type is UnionType
    }

    private fun FieldType.isBooleanColumn(): Boolean {
        return type is BooleanType
    }

    private fun FieldType.isDateColumn(): Boolean {
        return type is DateType
    }

    private fun FieldType.isTimeColumn(): Boolean {
        return type is TimeTypeWithTimezone || type is TimeTypeWithoutTimezone
    }

    private fun FieldType.isTimestampColumn(): Boolean {
        return type is TimestampTypeWithTimezone || type is TimestampTypeWithoutTimezone
    }

    private fun Meta.nullify(fieldName: String, reason: AirbyteRecordMessageMetaChange.Reason) {
        val metaChange =
            Meta.Change(
                field = fieldName,
                change = AirbyteRecordMessageMetaChange.Change.NULLED,
                reason = reason
            )
        (this.changes as MutableList).add(metaChange)
    }
}
