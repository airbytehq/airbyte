/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_LOADED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.util.Jsons

interface SnowflakeRecordFormatter {
    fun format(record: Map<String, AirbyteValue>, columnSchema: ColumnSchema): List<Any>
}

class SnowflakeSchemaRecordFormatter : SnowflakeRecordFormatter {
    override fun format(record: Map<String, AirbyteValue>, columnSchema: ColumnSchema): List<Any> {
        val result = mutableListOf<Any>()
        val userColumns = columnSchema.finalSchema.keys

        // WARNING:  MUST match the order defined in SnowflakeColumnManager#getTableColumnNames
        //
        // Why don't we just use that here? Well, unlike the user fields, the meta fields on the
        // record are not munged for the destination. So we must access the values for those columns
        // using the original lowercase meta key.
        result.add(record[COLUMN_NAME_AB_RAW_ID].toCsvValue())
        result.add(record[COLUMN_NAME_AB_EXTRACTED_AT].toCsvValue())
        result.add(record[COLUMN_NAME_AB_META].toCsvValue())
        result.add(record[COLUMN_NAME_AB_GENERATION_ID].toCsvValue())

        // Add user columns from the final schema
        userColumns.forEach { columnName -> result.add(record[columnName].toCsvValue()) }

        return result
    }
}

class SnowflakeRawRecordFormatter : SnowflakeRecordFormatter {

    override fun format(record: Map<String, AirbyteValue>, columnSchema: ColumnSchema): List<Any> =
        toOutputRecord(record.toMutableMap())

    private fun toOutputRecord(record: MutableMap<String, AirbyteValue>): List<Any> {
        val outputRecord = mutableListOf<Any>()
        val mutableRecord = record.toMutableMap()

        // Add meta columns in order (except _airbyte_data which we handle specially)
        outputRecord.add(mutableRecord.remove(COLUMN_NAME_AB_RAW_ID)?.toCsvValue() ?: "")
        outputRecord.add(mutableRecord.remove(COLUMN_NAME_AB_EXTRACTED_AT)?.toCsvValue() ?: "")
        outputRecord.add(mutableRecord.remove(COLUMN_NAME_AB_META)?.toCsvValue() ?: "")
        outputRecord.add(mutableRecord.remove(COLUMN_NAME_AB_GENERATION_ID)?.toCsvValue() ?: "")
        outputRecord.add(mutableRecord.remove(COLUMN_NAME_AB_LOADED_AT)?.toCsvValue() ?: "")

        // Do not output null values in the JSON raw output
        val filteredRecord = mutableRecord.filter { (_, v) -> v !is NullValue }

        // Convert all the remaining columns to a JSON document stored in the "data" column
        outputRecord.add(StringValue(Jsons.writeValueAsString(filteredRecord)).toCsvValue())

        return outputRecord
    }
}
