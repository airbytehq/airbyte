/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.util.Jsons

internal val RAW_META_COLUMNS =
    listOf(
        Meta.COLUMN_NAME_AB_EXTRACTED_AT,
        Meta.COLUMN_NAME_AB_META,
        Meta.COLUMN_NAME_AB_RAW_ID,
        Meta.COLUMN_NAME_AB_GENERATION_ID
    )

interface PostgresRecordFormatter {
    fun format(record: Map<String, AirbyteValue>): List<Any>
}

class PostgresSchemaRecordFormatter(
    private val columns: List<String>,
) : PostgresRecordFormatter {
    override fun format(record: Map<String, AirbyteValue>): List<Any> =
        columns.map { columnName ->
            if (record.containsKey(columnName)) record[columnName].toCsvValue() else ""
        }
}

class PostgresRawRecordFormatter(
    private val columns: List<String>,
) : PostgresRecordFormatter {

    override fun format(record: Map<String, AirbyteValue>): List<Any> =
        toOutputRecord(record.toMutableMap())

    private fun toOutputRecord(record: MutableMap<String, AirbyteValue>): List<Any> {
        val outputRecord = mutableListOf<Any>()
        // Copy the Airbyte metadata columns to the raw output, removing each
        // one from the record to avoid duplicates in the "data" field
        columns
            .filter { RAW_META_COLUMNS.contains(it) }
            .forEach { column ->
                when (column) {
                    Meta.COLUMN_NAME_AB_EXTRACTED_AT,
                    Meta.COLUMN_NAME_AB_META,
                    Meta.COLUMN_NAME_AB_RAW_ID,
                    Meta.COLUMN_NAME_AB_GENERATION_ID ->
                        safeAddToOutput(column, record, outputRecord)
                }
            }
        // Do not output null values in the JSON raw output
        val filteredRecord = record.filter { (_, v) -> v !is NullValue }
        // Convert all the remaining columns in the record to a JSON document stored in the "data"
        // column
        outputRecord.add(StringValue(Jsons.writeValueAsString(filteredRecord)).toCsvValue())
        return outputRecord
    }

    private fun safeAddToOutput(
        key: String,
        record: MutableMap<String, AirbyteValue>,
        output: MutableList<Any>
    ) {
        val extractedValue = record.remove(key)
        output.add(extractedValue?.toCsvValue() ?: "")
    }
}
