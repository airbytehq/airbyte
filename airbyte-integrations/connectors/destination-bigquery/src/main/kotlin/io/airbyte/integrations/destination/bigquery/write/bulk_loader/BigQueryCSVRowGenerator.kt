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
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.integrations.destination.bigquery.BigQueryConsts
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter.Companion.formatTimeWithTimezone
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter.Companion.formatTimeWithoutTimezone
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter.Companion.formatTimestampWithTimezone
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter.Companion.formatTimestampWithoutTimezone
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import java.math.BigDecimal
import java.math.BigInteger

object LIMITS {
    val TRUE = IntegerValue(1)
    val FALSE = IntegerValue(0)

    fun validateNumber(value: EnrichedAirbyteValue): BigDecimal? {
        val numValue = (value.abValue as NumberValue).value
        return if (
            numValue < BigQueryRecordFormatter.MIN_NUMERIC ||
                BigQueryRecordFormatter.MAX_NUMERIC < numValue
        ) {
            value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
            null
        } else {
            numValue
        }
    }

    fun validateInteger(value: EnrichedAirbyteValue): BigInteger? {
        val intValue = (value.abValue as IntegerValue).value
        return if (
            intValue < BigQueryRecordFormatter.INT64_MIN_VALUE ||
                BigQueryRecordFormatter.INT64_MAX_VALUE < intValue
        ) {
            value.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)
            null
        } else {
            intValue
        }
    }
}

class BigQueryCSVRowGenerator {
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
                    value.abValue = StringValue(formatTimestampWithTimezone(value))
                is TimestampTypeWithoutTimezone ->
                    value.abValue = StringValue(formatTimestampWithoutTimezone(value))
                is TimeTypeWithTimezone ->
                    value.abValue = StringValue(formatTimeWithTimezone(value))
                is TimeTypeWithoutTimezone ->
                    value.abValue = StringValue(formatTimeWithoutTimezone(value))

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
