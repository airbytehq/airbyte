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
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.Meta
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

class MSSQLCsvRowValidator {

    fun validate(
        record: DestinationRecordAirbyteValue,
        schema: ObjectType
    ): DestinationRecordAirbyteValue {
        val objectValue = record.data as? ObjectValue ?: return record
        val values = objectValue.values

        schema.properties.forEach { (columnName, fieldType) ->
            val oldValue = values[columnName]
            if (oldValue != null && oldValue !is NullValue) {
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
    ): AirbyteValue = when (this) {
        is StringValue -> validateStringValue(columnName, this, fieldType, meta)
        is IntegerValue -> validateIntegerValue(columnName, this, meta)
        is BooleanValue -> validateBooleanValue(this)
        // If it’s any other data type, we just skip validation logic here.
        else -> this
    }

    private fun validateStringValue(
        columnName: String,
        value: StringValue,
        fieldType: FieldType,
        meta: Meta
    ): AirbyteValue {
        if (fieldType.isStringColumn()) {
            return value
        }

        val rawString = value.value

        if (fieldType.isNumericColumn()) {
            if (!safeParseBigDecimal(rawString)) {
                meta.nullify(
                    columnName,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR,
                )
                return NullValue
            }
        }
        else if (fieldType.isBooleanColumn()) {
            val asIntValue = parseBooleanAsIntValue(rawString)
            if (asIntValue == null) {
                meta.nullify(
                    columnName,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR,
                )
                return NullValue
            }
            return asIntValue
        } else if (fieldType.isDateColumn()) {
            if (!safeParseDate(rawString)) {
                meta.nullify(
                    columnName,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR,
                )
                return NullValue
            }
        } else if (fieldType.isTimeColumn()) {
            if (!safeParseTime(rawString)) {
                meta.nullify(
                    columnName,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR,
                )
                return NullValue
            }
        } else if (fieldType.isTimestampColumn()) {
            if (!safeParseTimestamp(rawString)) {
                meta.nullify(
                    columnName,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR,
                )
                return NullValue
            }
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
                AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            )
            return NullValue
        }
        return value
    }

    private fun validateBooleanValue(value: BooleanValue): IntegerValue {
        return if (value.value) LIMITS.TRUE else LIMITS.FALSE
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

    private fun safeParseBigDecimal(value: String): Boolean {
        return runCatching { value.toBigDecimal() }.isSuccess
    }

    private fun safeParseDate(value: String): Boolean {
        return runCatching { LocalDate.parse(value) }.isSuccess
    }

    private fun safeParseTime(value: String): Boolean {
        // Attempt offset time, then local time
        if (runCatching { OffsetTime.parse(value) }.isSuccess) return true
        return runCatching { LocalTime.parse(value) }.isSuccess
    }

    private fun safeParseTimestamp(value: String): Boolean {
        // Attempt offset date-time, then local date-time
        if (runCatching { OffsetDateTime.parse(value) }.isSuccess) return true
        return runCatching { LocalDateTime.parse(value) }.isSuccess
    }

    private fun FieldType.isNumericColumn(): Boolean {
        return type is NumberType || type is IntegerType
    }

    private fun FieldType.isStringColumn(): Boolean {
        return type is StringType
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
        val metaChange = Meta.Change(
            field = fieldName,
            change = AirbyteRecordMessageMetaChange.Change.NULLED,
            reason = reason,
        )
        (this.changes as MutableList).add(metaChange)
    }
}
