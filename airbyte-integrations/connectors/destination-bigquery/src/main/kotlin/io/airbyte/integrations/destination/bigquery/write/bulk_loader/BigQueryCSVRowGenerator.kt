/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
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
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.integrations.destination.bigquery.BigQueryConsts
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import java.math.BigDecimal
import java.math.BigInteger
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder

object LIMITS {
    // Maximum value for BIGINT in SQL Server
    private val MAX_BIGINT = BigInteger("9223372036854775807")
    private val MIN_BIGINT = BigInteger("-9223372036854775808")

    // see MssqlType. We currently use precision=38, scale=9.
    private val NUMERIC_SCALE = BigDecimal("1e9")
    private val MAX_NUMERIC: BigDecimal =
        BigDecimal("1e38").minus(BigDecimal.ONE).divide(NUMERIC_SCALE)
    private val MIN_NUMERIC: BigDecimal =
        BigDecimal("-1e38").plus(BigDecimal.ONE).divide(NUMERIC_SCALE)

    val TRUE = IntegerValue(1)
    val FALSE = IntegerValue(0)

    fun validateNumber(value: EnrichedAirbyteValue): BigDecimal? {
        val numValue = (value.abValue as NumberValue).value
        return if (numValue < MIN_NUMERIC || MAX_NUMERIC < numValue) {
            value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
            null
        } else {
            return numValue
        }
    }

    fun validateInteger(value: EnrichedAirbyteValue): BigInteger? {
        val intValue = (value.abValue as IntegerValue).value
        return if (intValue < MIN_BIGINT || MAX_BIGINT < intValue) {
            value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
            null
        } else {
            intValue
        }
    }
}

class BigQueryCSVRowGenerator {
    companion object {
        // BigQuery requires TIME values in HH:mm:ss format, even if seconds are zero
        private val BIGQUERY_TIME_FORMATTER =
            DateTimeFormatterBuilder().appendPattern("HH:mm:ss").toFormatter()

        private val BIGQUERY_TIME_WITH_TIMEZONE_FORMATTER =
            DateTimeFormatterBuilder().appendPattern("HH:mm:ss").appendOffsetId().toFormatter()
    }

    fun generate(record: DestinationRecordRaw, schema: ObjectType): List<Any> {
        val enrichedRecord =
            record.asEnrichedDestinationRecordAirbyteValue(
                extractedAtAsTimestampWithTimezone = true
            )

        enrichedRecord.declaredFields.values.forEach { value ->
            if (value.abValue is NullValue) {
                return@forEach
            }
            val actualValue = value.abValue
            when (value.type) {
                // Enforce numeric range
                is IntegerType -> LIMITS.validateInteger(value)
                is NumberType -> LIMITS.validateNumber(value)
                is BooleanType ->
                    value.abValue =
                        if ((actualValue as BooleanValue).value) LIMITS.TRUE else LIMITS.FALSE
                is TimestampTypeWithTimezone ->
                    value.abValue =
                        StringValue(
                            (actualValue as TimestampWithTimezoneValue)
                                .value
                                .format(DateTimeFormatter.ISO_OFFSET_DATE_TIME)
                        )
                is TimestampTypeWithoutTimezone ->
                    value.abValue =
                        StringValue(
                            (actualValue as TimestampWithoutTimezoneValue)
                                .value
                                .format(DateTimeFormatter.ISO_DATE_TIME)
                        )
                is TimeTypeWithTimezone ->
                    value.abValue =
                        StringValue(
                            (actualValue as TimeWithTimezoneValue)
                                .value
                                .format(DateTimeFormatter.ISO_OFFSET_TIME)
                        )
                is TimeTypeWithoutTimezone ->
                    value.abValue =
                        StringValue(
                            (actualValue as TimeWithoutTimezoneValue)
                                .value
                                .format((DateTimeFormatter.ISO_LOCAL_TIME))
                        )

                // serialize complex types to string
                is ArrayType,
                is ObjectType,
                is UnionType,
                is UnknownType -> value.abValue = StringValue(actualValue.serializeToString())
                else -> {}
            }
        }

        val values = enrichedRecord.allTypedFields
        return schema.properties.map { (columnName, _) ->
            val value = values[columnName]
            if (value == null || value.abValue is NullValue) {
                return@map BigQueryConsts.NULL_MARKER
            }
            value.abValue.toCsvValue()
        }
    }
}
