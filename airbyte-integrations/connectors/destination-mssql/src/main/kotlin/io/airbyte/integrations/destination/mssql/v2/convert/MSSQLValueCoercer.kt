/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.convert

import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDateTime

/**
 * Centralises MSSQL-specific value coercion and validation that is shared across both the INSERT
 * (PreparedStatement) and BULK LOAD (CSV) data paths.
 */
object MSSQLValueCoercer {

    // Maximum value for BIGINT in SQL Server
    val MAX_BIGINT: BigInteger = BigInteger("9223372036854775807")
    val MIN_BIGINT: BigInteger = BigInteger("-9223372036854775808")

    // See [MssqlType.DECIMAL]. We currently use precision=38, scale=8.
    private val NUMERIC_SCALE = BigDecimal("1e8")
    val MAX_NUMERIC: BigDecimal = BigDecimal("1e38").minus(BigDecimal.ONE).divide(NUMERIC_SCALE)
    val MIN_NUMERIC: BigDecimal = BigDecimal("-1e38").plus(BigDecimal.ONE).divide(NUMERIC_SCALE)

    // Minimum value for DATETIME in SQL Server (1753-01-01 00:00:00.000)
    val MIN_DATETIME: LocalDateTime = LocalDateTime.of(1753, 1, 1, 0, 0, 0)

    /** Coerces a single [EnrichedAirbyteValue] to be MSSQL-compatible **in place */
    fun coerce(value: EnrichedAirbyteValue) {
        if (value.abValue is NullValue) return

        when (value.type) {
            IntegerType -> validateInteger(value)
            NumberType -> validateNumber(value)

            // Validate pre-1753 range; value stays as TimestampWithoutTimezoneValue
            TimestampTypeWithoutTimezone -> validateTimestamp(value)

            // Serialise complex types to a JSON string
            is ArrayType,
            ArrayTypeWithoutSchema,
            is ObjectType,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema,
            is UnionType,
            is UnknownType -> value.abValue = StringValue(value.abValue.serializeToString())

            // All other types (Boolean, Date, String, Time*) need no coercion
            else -> {}
        }
    }

    /**
     * Validates that the integer value fits in an MSSQL BIGINT. If not, the value is nullified and
     * `null` is returned.
     */
    fun validateInteger(value: EnrichedAirbyteValue): BigInteger? {
        val intValue = (value.abValue as IntegerValue).value
        return if (intValue < MIN_BIGINT || MAX_BIGINT < intValue) {
            value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
            null
        } else {
            intValue
        }
    }

    /**
     * Validates that the number value fits in an MSSQL DECIMAL(38, 8). If not, the value is
     * nullified and `null` is returned.
     */
    fun validateNumber(value: EnrichedAirbyteValue): BigDecimal? {
        val numValue = (value.abValue as NumberValue).value
        return if (numValue < MIN_NUMERIC || MAX_NUMERIC < numValue) {
            value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
            null
        } else {
            numValue
        }
    }

    /**
     * Validates that the timestamp value is within the MSSQL DATETIME range (>= 1753-01-01). If
     * not, the value is nullified and `null` is returned.
     */
    fun validateTimestamp(value: EnrichedAirbyteValue): LocalDateTime? {
        val tsValue = (value.abValue as TimestampWithoutTimezoneValue).value
        return if (tsValue < MIN_DATETIME) {
            value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
            null
        } else {
            tsValue
        }
    }
}
