/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.NullValue
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
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter.Companion.formatTimeWithTimezone
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter.Companion.formatTimeWithoutTimezone
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter.Companion.formatTimestampWithTimezone
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter.Companion.formatTimestampWithoutTimezone
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter.Companion.validateAirbyteValue

class BigQueryCSVRowGenerator {
    fun generate(record: DestinationRecordRaw, schema: ObjectType): List<Any> {
        val enrichedRecord =
            record.asEnrichedDestinationRecordAirbyteValue(
                extractedAtAsTimestampWithTimezone = true,
                respectLegacyUnions = true,
            )

        enrichedRecord.declaredFields.values.forEach { value ->
            if (value.abValue is NullValue) {
                return@forEach
            }
            validateAirbyteValue(value)

            val actualValue = value.abValue
            when (value.type) {
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
                is UnknownType -> value.abValue = StringValue(actualValue.serializeToString())

                // non-legacy unions should be serialized.
                // But legacy unions are converted to an actual type by validateAirbyteValue(),
                // so leave them unchanged.
                is UnionType ->
                    if (!(value.type as UnionType).isLegacyUnion) {
                        value.abValue = StringValue(actualValue.serializeToString())
                    }
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
