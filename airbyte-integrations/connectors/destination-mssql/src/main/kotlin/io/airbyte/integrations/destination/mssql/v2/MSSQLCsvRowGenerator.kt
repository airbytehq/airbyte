/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.integrations.destination.mssql.v2.convert.MSSQLValueCoercer
import java.time.format.DateTimeFormatter

/** Convenience constants for CSV boolean representation (MSSQL BIT expects 0 / 1). */
private val CSV_TRUE = IntegerValue(1)
private val CSV_FALSE = IntegerValue(0)

/** Generates CSV rows for the MSSQL BULK LOAD path. */
class MSSQLCsvRowGenerator {

    fun generate(record: DestinationRecordRaw, schema: ObjectType): List<Any> {
        val enrichedRecord = record.asEnrichedDestinationRecordAirbyteValue()

        enrichedRecord.declaredFields.values.forEach { value ->
            MSSQLValueCoercer.coerce(value)
            if (value.abValue is NullValue) return@forEach

            // CSV-specific coercions
            when (value.type) {
                // MSSQL BIT columns expect 0 / 1 in CSV
                is BooleanType ->
                    value.abValue =
                        if ((value.abValue as BooleanValue).value) CSV_TRUE else CSV_FALSE

                // MSSQL requires a fully-qualified ISO timestamp format in CSV.
                // e.g. "2000-01-01T00:00Z" must become "2000-01-01T00:00:00Z".
                is TimestampTypeWithTimezone ->
                    value.abValue =
                        StringValue(
                            (value.abValue as TimestampWithTimezoneValue)
                                .value
                                .format(DateTimeFormatter.ISO_OFFSET_DATE_TIME)
                        )
                is TimestampTypeWithoutTimezone ->
                    value.abValue =
                        StringValue(
                            (value.abValue as TimestampWithoutTimezoneValue)
                                .value
                                .format(DateTimeFormatter.ISO_DATE_TIME)
                        )
                else -> {}
            }
        }

        val values = enrichedRecord.allTypedFields
        return schema.properties.map { (columnName, _) ->
            val value = values[columnName]
            value?.abValue.toCsvValue()
        }
    }
}
