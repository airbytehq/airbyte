/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils

interface SnowflakeRecordFormatter {
    fun format(record: Map<String, AirbyteValue>): List<Any>
}

class SnowflakeSchemaRecordFormatter(
    private val columns: LinkedHashMap<String, String>,
    val snowflakeColumnUtils: SnowflakeColumnUtils,
) : SnowflakeRecordFormatter {

    private val airbyteColumnNames =
        snowflakeColumnUtils.getFormattedDefaultColumnNames(false).toSet()

    override fun format(record: Map<String, AirbyteValue>): List<Any> =
        columns.map { (columnName, _) ->
            /*
             * Meta columns are forced to uppercase for backwards compatibility with previous
             * versions of the destination.  Therefore, convert the column to lowercase so
             * that it can match the constants, which use the lowercase version of the meta
             * column names.
             */
            if (airbyteColumnNames.contains(columnName)) {
                record[columnName.lowercase()].toCsvValue()
            } else {
                record.keys
                    // The columns retrieved from Snowflake do not have any escaping applied.
                    // Therefore, re-apply the compatible name escaping to the name of the
                    // columns retrieved from Snowflake.  The record keys should already have
                    // been escaped by the CDK before arriving at the aggregate, so no need
                    // to escape again here.
                    .find { it == columnName.toSnowflakeCompatibleName() }
                    ?.let { record[it].toCsvValue() }
                    ?: ""
            }
        }
}

class SnowflakeRawRecordFormatter(
    columns: LinkedHashMap<String, String>,
    val snowflakeColumnUtils: SnowflakeColumnUtils,
) : SnowflakeRecordFormatter {
    private val columns = columns.keys

    private val airbyteColumnNames =
        snowflakeColumnUtils.getFormattedDefaultColumnNames(false).toSet()

    override fun format(record: Map<String, AirbyteValue>): List<Any> =
        toOutputRecord(record.toMutableMap())

    private fun toOutputRecord(record: MutableMap<String, AirbyteValue>): List<Any> {
        val outputRecord = mutableListOf<Any>()
        // Copy the Airbyte metadata columns to the raw output, removing each
        // one from the record to avoid duplicates in the "data" field
        columns
            .filter { airbyteColumnNames.contains(it) && it != Meta.COLUMN_NAME_DATA }
            .forEach { column -> safeAddToOutput(column, record, outputRecord) }
        // Do not output null values in the JSON raw output
        val filteredRecord = record.filter { (_, v) -> v !is NullValue }
        // Convert all the remaining columns in the record to a JSON document stored in the "data"
        // column.  Add it in the same position as the _airbyte_data column in the column list to
        // ensure it is inserted into the proper column in the table.
        insert(
            columns.indexOf(Meta.COLUMN_NAME_DATA),
            StringValue(Jsons.writeValueAsString(filteredRecord)).toCsvValue(),
            outputRecord
        )
        return outputRecord
    }

    private fun safeAddToOutput(
        key: String,
        record: MutableMap<String, AirbyteValue>,
        output: MutableList<Any>
    ) {
        val extractedValue = record.remove(key)
        // Ensure that the data is inserted into the list at the same position as the column
        insert(columns.indexOf(key), extractedValue?.toCsvValue() ?: "", output)
    }

    private fun insert(index: Int, value: Any, list: MutableList<Any>) {
        /*
         * Attempt to insert the value into the proper order in the list.  If the index
         * is already present in the list, use the add(index, element) method to insert it
         * into the proper order and push everything to the right.  If the index is at the
         * end of the list, just use add(element) to insert it at the end.  If the index
         * is further beyond the end of the list, throw an exception as that should not occur.
         */
        if (index < list.size) list.add(index, value)
        else if (index == list.size || index == list.size + 1) list.add(value)
        else throw IndexOutOfBoundsException()
    }
}
