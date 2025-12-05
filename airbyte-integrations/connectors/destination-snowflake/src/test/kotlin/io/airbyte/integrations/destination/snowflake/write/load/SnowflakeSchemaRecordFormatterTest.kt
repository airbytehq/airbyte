/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.mockk.every
import io.mockk.mockk
import java.util.AbstractMap
import kotlin.collections.component1
import kotlin.collections.component2
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

private val AIRBYTE_COLUMN_TYPES_MAP =
    linkedMapOf(
            COLUMN_NAME_AB_RAW_ID to "VARCHAR(16777216)",
            COLUMN_NAME_AB_EXTRACTED_AT to "TIMESTAMP_TZ(9)",
            COLUMN_NAME_AB_META to "VARIANT",
            COLUMN_NAME_AB_GENERATION_ID to "NUMBER(38,0)",
        )
        .mapKeys { it.key.toSnowflakeCompatibleName() }

internal class SnowflakeSchemaRecordFormatterTest {

    private lateinit var snowflakeColumnUtils: SnowflakeColumnUtils

    @BeforeEach
    fun setup() {
        snowflakeColumnUtils = mockk {
            every { getFormattedDefaultColumnNames(any()) } returns
                AIRBYTE_COLUMN_TYPES_MAP.keys.toList()
        }
    }

    @Test
    fun testFormatting() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val columns =
            (AIRBYTE_COLUMN_TYPES_MAP + linkedMapOf(columnName to "VARCHAR(16777216)")).mapKeys {
                it.key.toSnowflakeCompatibleName()
            }
        val record = createRecord(columnName, columnValue)
        val formatter =
            SnowflakeSchemaRecordFormatter(
                columns = columns as LinkedHashMap<String, String>,
                snowflakeColumnUtils = snowflakeColumnUtils
            )
        val formattedValue = formatter.format(record)
        val expectedValue =
            createExpected(
                record = record,
                columns = columns,
            )
        assertEquals(expectedValue, formattedValue)
    }

    @Test
    fun testFormattingVariant() {
        val columnName = "test-column-name"
        val columnValue = "{\"test\": \"test-value\"}"
        val columns =
            (AIRBYTE_COLUMN_TYPES_MAP + linkedMapOf(columnName to "VARIANT")).mapKeys {
                it.key.toSnowflakeCompatibleName()
            }
        val record = createRecord(columnName, columnValue)
        val formatter =
            SnowflakeSchemaRecordFormatter(
                columns = columns as LinkedHashMap<String, String>,
                snowflakeColumnUtils = snowflakeColumnUtils
            )
        val formattedValue = formatter.format(record)
        val expectedValue =
            createExpected(
                record = record,
                columns = columns,
            )
        assertEquals(expectedValue, formattedValue)
    }

    @Test
    fun testFormattingMissingColumn() {
        val columnName = "test-column-name"
        val columnValue = "test-column-value"
        val columns =
            AIRBYTE_COLUMN_TYPES_MAP +
                linkedMapOf(
                    columnName to "VARCHAR(16777216)",
                    "missing-column" to "VARCHAR(16777216)"
                )
        val record = createRecord(columnName, columnValue)
        val formatter =
            SnowflakeSchemaRecordFormatter(
                columns = columns as LinkedHashMap<String, String>,
                snowflakeColumnUtils = snowflakeColumnUtils
            )
        val formattedValue = formatter.format(record)
        val expectedValue =
            createExpected(
                record = record,
                columns = columns,
                filterMissing = false,
            )
        assertEquals(expectedValue, formattedValue)
    }

    private fun createRecord(columnName: String, columnValue: String) = buildMap {
        put(columnName.toSnowflakeCompatibleName(), AirbyteValue.from(columnValue))
        put(COLUMN_NAME_AB_EXTRACTED_AT, IntegerValue(System.currentTimeMillis()))
        put(COLUMN_NAME_AB_RAW_ID, StringValue("raw-id"))
        put(COLUMN_NAME_AB_GENERATION_ID, IntegerValue(1223))
        put(COLUMN_NAME_AB_META, StringValue("{\"changes\":[],\"syncId\":43}"))
        put("${columnName}Null".toSnowflakeCompatibleName(), NullValue)
    }

    private fun createExpected(
        record: Map<String, AirbyteValue>,
        columns: Map<String, String>,
        filterMissing: Boolean = true,
    ) =
        record.entries
            .associate { entry -> entry.key.toSnowflakeCompatibleName() to entry.value }
            .map { entry -> AbstractMap.SimpleEntry(entry.key, entry.value.toCsvValue()) }
            .sortedBy { entry ->
                if (columns.keys.indexOf(entry.key) > -1) columns.keys.indexOf(entry.key)
                else Int.MAX_VALUE
            }
            .filter { (k, _) -> if (filterMissing) columns.contains(k) else true }
            .map { it.value }
}
