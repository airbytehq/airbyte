/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.snowflake.sql.SNOWFLAKE_AB_EXTRACTED_AT
import io.airbyte.integrations.destination.snowflake.sql.SNOWFLAKE_AB_GENERATION_ID
import io.airbyte.integrations.destination.snowflake.sql.SNOWFLAKE_AB_META
import io.airbyte.integrations.destination.snowflake.sql.SNOWFLAKE_AB_RAW_ID

interface SnowflakeRecordFormatter {
    fun format(record: Map<String, AirbyteValue>): List<Any>
}

class SnowflakeSchemaRecordFormatter(
    val columnSchema: ColumnSchema,
) : SnowflakeRecordFormatter {
    override fun format(record: Map<String, AirbyteValue>): List<Any> {
        val result = mutableListOf<Any>()

        // Add meta columns in order
        result.add(record[SNOWFLAKE_AB_RAW_ID.lowercase()].toCsvValue())
        result.add(record[SNOWFLAKE_AB_EXTRACTED_AT.lowercase()].toCsvValue())
        result.add(record[SNOWFLAKE_AB_META.lowercase()].toCsvValue())
        result.add(record[SNOWFLAKE_AB_GENERATION_ID.lowercase()].toCsvValue())

        // Add user columns from the final schema
        columnSchema.finalSchema.keys.forEach { columnName ->
            result.add(record[columnName].toCsvValue())
        }

        return result
    }
}

class SnowflakeRawRecordFormatter : SnowflakeRecordFormatter {

    override fun format(record: Map<String, AirbyteValue>): List<Any> =
        toOutputRecord(record.toMutableMap())

    private fun toOutputRecord(record: MutableMap<String, AirbyteValue>): List<Any> {
        val outputRecord = mutableListOf<Any>()
        val mutableRecord = record.toMutableMap()

        // Add meta columns in order (except _airbyte_data which we handle specially)
        outputRecord.add(mutableRecord.remove(Meta.COLUMN_NAME_AB_RAW_ID)?.toCsvValue() ?: "")
        outputRecord.add(mutableRecord.remove(Meta.COLUMN_NAME_AB_EXTRACTED_AT)?.toCsvValue() ?: "")
        outputRecord.add(mutableRecord.remove(Meta.COLUMN_NAME_AB_META)?.toCsvValue() ?: "")
        outputRecord.add(
            mutableRecord.remove(Meta.COLUMN_NAME_AB_GENERATION_ID)?.toCsvValue() ?: ""
        )
        outputRecord.add(mutableRecord.remove(Meta.COLUMN_NAME_AB_LOADED_AT)?.toCsvValue() ?: "")

        // Do not output null values in the JSON raw output
        val filteredRecord = mutableRecord.filter { (_, v) -> v !is NullValue }

        // Convert all the remaining columns to a JSON document stored in the "data" column
        outputRecord.add(StringValue(Jsons.writeValueAsString(filteredRecord)).toCsvValue())

        return outputRecord
    }
}
