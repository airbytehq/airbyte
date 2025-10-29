/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write.load

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.util.Jsons

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

        // Do not output null values in the JSON raw output
        val filteredRecord = record.filter { (k, _) -> !RAW_META_COLUMNS.contains(k) }
        // Convert AirbyteValue to JsonNode to avoid double-encoding
        val jsonObject = JsonNodeFactory.instance.objectNode()
        filteredRecord.forEach { (key, value) ->
            jsonObject.replace(key, value.toJson())
        }
        val jsonData = Jsons.writeValueAsString(filteredRecord)

        // Iterate through columns in the exact order they appear in the table
        columns.forEach { column ->
            when (column) {
                Meta.COLUMN_NAME_AB_RAW_ID,
                Meta.COLUMN_NAME_AB_EXTRACTED_AT,
                Meta.COLUMN_NAME_AB_META,
                Meta.COLUMN_NAME_AB_GENERATION_ID -> {
                    // Extract metadata columns from the record
                    val extractedValue = record[column]
                    outputRecord.add(extractedValue?.toCsvValue() ?: "")
                }
                Meta.COLUMN_NAME_AB_LOADED_AT -> {
                    // _airbyte_loaded_at is nullable and not set during initial insert
                    outputRecord.add("")
                }
                Meta.COLUMN_NAME_DATA -> {
                    // _airbyte_data contains the JSON representation of the data
                    outputRecord.add(jsonData)
                }
                else -> {
                    // This shouldn't happen in raw mode, but handle it gracefully
                    outputRecord.add("")
                }
            }
        }

        return outputRecord
    }
}
