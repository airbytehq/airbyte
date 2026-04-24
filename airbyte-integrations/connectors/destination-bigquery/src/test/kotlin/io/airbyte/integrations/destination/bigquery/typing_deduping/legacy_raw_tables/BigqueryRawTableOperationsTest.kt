/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping.legacy_raw_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.FieldValue
import com.google.cloud.bigquery.FieldValueList
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.TableResult
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.TableName
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers.any
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`

class BigqueryRawTableOperationsTest {

    private val bigquery = mock(BigQuery::class.java)
    private val operations = BigqueryRawTableOperations(bigquery)
    private val tableName = TableName("my_dataset", "my_table")

    @Test
    fun testGetRawTableGenerationReturnsNullForLegacyTable() {
        `when`(bigquery.query(any<QueryJobConfiguration>()))
            .thenThrow(
                BigQueryException(
                    400,
                    "Unrecognized name: _airbyte_generation_id at [1:8]"
                )
            )

        val result = operations.getRawTableGeneration(tableName, "")
        assertNull(result)
    }

    @Test
    fun testGetRawTableGenerationRethrowsUnrelatedBigQueryException() {
        `when`(bigquery.query(any<QueryJobConfiguration>()))
            .thenThrow(BigQueryException(403, "Access Denied"))

        assertThrows(BigQueryException::class.java) {
            operations.getRawTableGeneration(tableName, "")
        }
    }

    @Test
    fun testGetRawTableGenerationReturnsNullForEmptyTable() {
        val tableResult = mock(TableResult::class.java)
        `when`(tableResult.totalRows).thenReturn(0L)
        `when`(bigquery.query(any<QueryJobConfiguration>())).thenReturn(tableResult)

        val result = operations.getRawTableGeneration(tableName, "")
        assertNull(result)
    }

    @Test
    fun testGetRawTableGenerationReturnsValueWhenPresent() {
        val tableResult = mock(TableResult::class.java)
        `when`(tableResult.totalRows).thenReturn(1L)

        val fieldValue = mock(FieldValue::class.java)
        `when`(fieldValue.isNull).thenReturn(false)
        `when`(fieldValue.longValue).thenReturn(42L)

        val row = mock(FieldValueList::class.java)
        `when`(row.get(Meta.COLUMN_NAME_AB_GENERATION_ID)).thenReturn(fieldValue)
        `when`(tableResult.iterateAll()).thenReturn(listOf(row))

        `when`(bigquery.query(any<QueryJobConfiguration>())).thenReturn(tableResult)

        val result = operations.getRawTableGeneration(tableName, "")
        assertEquals(42L, result)
    }

    @Test
    fun testGetRawTableGenerationReturnsZeroForNullValue() {
        val tableResult = mock(TableResult::class.java)
        `when`(tableResult.totalRows).thenReturn(1L)

        val fieldValue = mock(FieldValue::class.java)
        `when`(fieldValue.isNull).thenReturn(true)

        val row = mock(FieldValueList::class.java)
        `when`(row.get(Meta.COLUMN_NAME_AB_GENERATION_ID)).thenReturn(fieldValue)
        `when`(tableResult.iterateAll()).thenReturn(listOf(row))

        `when`(bigquery.query(any<QueryJobConfiguration>())).thenReturn(tableResult)

        val result = operations.getRawTableGeneration(tableName, "")
        assertEquals(0L, result)
    }
}
