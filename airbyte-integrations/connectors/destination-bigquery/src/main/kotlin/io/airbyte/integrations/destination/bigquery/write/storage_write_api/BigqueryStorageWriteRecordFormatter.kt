/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.write.storage_write_api

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import com.google.cloud.bigquery.QueryParameterValue
import org.json.JSONObject
import java.util.concurrent.TimeUnit

/**
 * Formats records for BigQuery Storage Write API.
 * Converts DestinationRecordRaw to JSONObject for use with JsonStreamWriter.
 */
class BigqueryStorageWriteRecordFormatter(
    private val columnNameMapping: ColumnNameMapping,
    private val legacyRawTablesOnly: Boolean,
) {

    fun formatRecordToJson(record: DestinationRecordRaw): JSONObject {
        val enrichedRecord =
            record.asEnrichedDestinationRecordAirbyteValue(respectLegacyUnions = true)

        val outputRecord = JSONObject()
        val enrichedFieldsToIterate =
            if (legacyRawTablesOnly) {
                // In legacy raw tables mode, we only look at airbyte metadata fields
                // and dump actual data as JSON blob
                outputRecord.put(Meta.COLUMN_NAME_DATA, record.asJsonRecord().serializeToString())
                enrichedRecord.airbyteMetaFields
            } else {
                // In direct-load mode, process all fields
                enrichedRecord.allTypedFields
            }

        enrichedFieldsToIterate.forEach { (key, value) ->
            when (key) {
                Meta.COLUMN_NAME_AB_EXTRACTED_AT -> {
                    val extractedAtMillis = (value.abValue as IntegerValue).value.longValueExact()
                    val extractedAt = getExtractedAt(extractedAtMillis)
                    if (extractedAt != null) {
                        outputRecord.put(key, extractedAt)
                    }
                }
                Meta.COLUMN_NAME_AB_META -> {
                    // Defer meta field processing until after all other fields
                }
                Meta.COLUMN_NAME_AB_RAW_ID -> {
                    outputRecord.put(key, (value.abValue as StringValue).value)
                }
                Meta.COLUMN_NAME_AB_GENERATION_ID -> {
                    outputRecord.put(key, (value.abValue as IntegerValue).value.longValueExact())
                }
                else -> {
                    if (!legacyRawTablesOnly) {
                        BigQueryRecordFormatter.validateAirbyteValue(value)
                        if (value.abValue != NullValue) {
                            val formattedValue = when (value.type) {
                                TimestampTypeWithTimezone ->
                                    BigQueryRecordFormatter.formatTimestampWithTimezone(value)
                                TimestampTypeWithoutTimezone ->
                                    BigQueryRecordFormatter.formatTimestampWithoutTimezone(value)
                                TimeTypeWithoutTimezone ->
                                    BigQueryRecordFormatter.formatTimeWithoutTimezone(value)
                                TimeTypeWithTimezone ->
                                    BigQueryRecordFormatter.formatTimeWithTimezone(value)
                                else -> when (val abValue = value.abValue) {
                                    is StringValue -> abValue.value
                                    is IntegerValue -> abValue.value.longValueExact()
                                    is io.airbyte.cdk.load.data.NumberValue -> abValue.value.toDouble()
                                    is io.airbyte.cdk.load.data.BooleanValue -> abValue.value
                                    is ObjectValue -> abValue.values.serializeToString()
                                    is io.airbyte.cdk.load.data.ArrayValue ->
                                        abValue.values.map { it.serializeToString() }
                                    else -> abValue.serializeToString()
                                }
                            }
                            outputRecord.put(columnNameMapping[key]!!, formattedValue)
                        }
                    }
                }
            }
        }

        // Process airbyte_meta field
        val metaValue = if (legacyRawTablesOnly) {
            // In legacy mode, pass through original record's airbyte_meta
            val metaJson = JSONObject()
            record.rawData.sourceMeta?.changes?.forEach { change ->
                metaJson.put("changes", change.toString())
            }
            metaJson.put("sync_id", record.stream.syncId)
            metaJson.toString()
        } else {
            // In direct-load mode, use enriched meta
            (enrichedRecord.airbyteMeta.abValue as ObjectValue).values.serializeToString()
        }
        outputRecord.put(Meta.COLUMN_NAME_AB_META, metaValue)

        return outputRecord
    }

    private fun getExtractedAt(extractedAtMillis: Long): String? {
        // BigQuery TIMESTAMP has microsecond precision
        val emittedAtMicroseconds =
            TimeUnit.MICROSECONDS.convert(extractedAtMillis, TimeUnit.MILLISECONDS)
        return QueryParameterValue.timestamp(emittedAtMicroseconds).value
    }
}
