/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.client

import com.clickhouse.client.api.Client as ClickHouseClientRaw
import com.clickhouse.data.ClickHouseColumn
import com.clickhouse.data.ClickHouseDataType
import io.airbyte.integrations.destination.clickhouse_v2.model.AlterationSummary
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class ClickhouseAirbyteClientTest {
    // Mocks
    private val client: ClickHouseClientRaw = mockk(relaxed = true)
    private val clickhouseSqlGenerator: ClickhouseSqlGenerator = mockk(relaxed = true)

    // Client
    private val clickhouseAirbyteClient = ClickhouseAirbyteClient(client, clickhouseSqlGenerator)

    // Constants
    private val COL1 = "col1"
    private val COL2 = "col2"
    private val COL3 = "col3"
    private val COL4 = "col4"
    private val COL5 = "col5"
    private val STRING_TYPE = "String"
    private val dummySentence = "SELECT 1"

    @Test
    fun testExecute() =
        runTest {
            // TODO: make this test to work with the coroutines

            // val completableFutureMock = mockk<CompletableFuture<CommandResponse>>()
            // coEvery { completableFutureMock.await() } returns mockk()
            // every { client.execute(dummySentence) } returns completableFutureMock
            //
            // clickhouseAirbyteClient.execute(dummySentence)
            //
            // coVerify { client.execute(dummySentence) }
        }

    @Test
    fun testQuery() =
        runTest {
            // TODO: Same than testExecute, make this test to work with the coroutines

            // clickhouseAirbyteClient.query(dummySentence)
            //
            // coVerify { client.query(dummySentence) }
        }

    private fun getMockColumn(
        columnName: String,
        columnType: ClickHouseDataType
    ): ClickHouseColumn {
        val mColumn = mockk<ClickHouseColumn>()

        every { mColumn.columnName } returns columnName
        every { mColumn.dataType } returns columnType

        return mColumn
    }

    @Test
    fun `test no changes`() {
        val tableColumns =
            listOf(
                getMockColumn(columnName = COL1, columnType = ClickHouseDataType.String),
                getMockColumn(columnName = COL2, columnType = ClickHouseDataType.Int32)
            )
        val catalogColumns = mapOf(COL1 to STRING_TYPE, COL2 to "Int32")
        val expected =
            AlterationSummary(added = emptyMap(), modified = emptyMap(), deleted = emptySet())
        val actual = clickhouseAirbyteClient.getChangedColumns(tableColumns, catalogColumns)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test added columns`() {
        val tableColumns = listOf(getMockColumn(COL1, ClickHouseDataType.String))
        val catalogColumns =
            mapOf(COL1 to STRING_TYPE, COL2 to "Int32", COL3 to "Float64") // Added col2 and col3
        val expected =
            AlterationSummary(
                added = mapOf(COL2 to "Int32", COL3 to "Float64"),
                modified = emptyMap(), // No modified columns
                deleted = emptySet()
            )
        val actual = clickhouseAirbyteClient.getChangedColumns(tableColumns, catalogColumns)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test modified columns`() {
        val tableColumns =
            listOf(
                getMockColumn(columnName = COL1, columnType = ClickHouseDataType.String),
                getMockColumn(columnName = COL2, columnType = ClickHouseDataType.Int32)
            )
        val catalogColumns = mapOf(COL1 to STRING_TYPE, COL2 to STRING_TYPE)
        val expected =
            AlterationSummary(
                added = emptyMap(), // No added columns
                modified = mapOf(COL2 to STRING_TYPE),
                deleted = emptySet()
            )
        val actual = clickhouseAirbyteClient.getChangedColumns(tableColumns, catalogColumns)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test deleted columns`() {
        val tableColumns =
            listOf(getMockColumn(columnName = COL1, columnType = ClickHouseDataType.String))
        val catalogColumns = mapOf(COL1 to STRING_TYPE)
        val expected =
            AlterationSummary(added = emptyMap(), modified = emptyMap(), deleted = emptySet())
        val actual = clickhouseAirbyteClient.getChangedColumns(tableColumns, catalogColumns)
        Assertions.assertEquals(expected, actual)

        val tableColumns2 =
            listOf(getMockColumn(columnName = COL1, columnType = ClickHouseDataType.String))
        val catalogColumns2 = mapOf(COL2 to STRING_TYPE, COL3 to "Int32")
        val expected2 =
            AlterationSummary(
                added = mapOf(COL2 to STRING_TYPE, COL3 to "Int32"),
                modified = emptyMap(), // No modified columns
                deleted = setOf(COL1)
            )
        val actual2 = clickhouseAirbyteClient.getChangedColumns(tableColumns2, catalogColumns2)
        Assertions.assertEquals(expected2, actual2)
    }

    @Test
    fun `test all changes`() {
        val tableColumns =
            listOf(
                getMockColumn(columnName = COL1, columnType = ClickHouseDataType.String),
                getMockColumn(columnName = COL3, columnType = ClickHouseDataType.Int32)
            )
        val catalogColumns =
            mapOf(COL1 to STRING_TYPE, COL2 to STRING_TYPE, COL3 to STRING_TYPE, COL4 to "Float64")
        val expected =
            AlterationSummary( // Added col2 and col4, modified col3
                added = mapOf(COL2 to STRING_TYPE, COL4 to "Float64"),
                modified = mapOf(COL3 to STRING_TYPE),
                deleted = emptySet()
            )
        val actual = clickhouseAirbyteClient.getChangedColumns(tableColumns, catalogColumns)
        Assertions.assertEquals(expected, actual)

        val tableColumns2 =
            listOf(
                getMockColumn(columnName = COL1, columnType = ClickHouseDataType.String),
                getMockColumn(columnName = COL3, columnType = ClickHouseDataType.Int32)
            )
        val catalogColumns2 = mapOf(COL1 to STRING_TYPE, COL3 to STRING_TYPE)
        val expected2 =
            AlterationSummary( // Modified col3
                added = emptyMap(),
                modified = mapOf(COL3 to STRING_TYPE),
                deleted = emptySet()
            )
        val actual2 = clickhouseAirbyteClient.getChangedColumns(tableColumns2, catalogColumns2)
        Assertions.assertEquals(expected2, actual2)

        val tableColumns3 =
            listOf(
                getMockColumn(columnName = COL1, columnType = ClickHouseDataType.String),
                getMockColumn(columnName = COL3, columnType = ClickHouseDataType.Int32)
            )
        val catalogColumns3 = mapOf(COL1 to STRING_TYPE, COL2 to STRING_TYPE, COL3 to "Int32")
        val expected3 =
            AlterationSummary( // Added col2
                added = mapOf(COL2 to STRING_TYPE),
                modified = emptyMap(),
                deleted = emptySet()
            )
        val actual3 = clickhouseAirbyteClient.getChangedColumns(tableColumns3, catalogColumns3)
        Assertions.assertEquals(expected3, actual3)

        val tableColumns4 =
            listOf(
                getMockColumn(columnName = "col1", columnType = ClickHouseDataType.String),
                getMockColumn(columnName = COL3, columnType = ClickHouseDataType.Int32),
                getMockColumn(columnName = COL5, columnType = ClickHouseDataType.DateTime64)
            )
        val catalogColumns4 =
            mapOf(
                COL1 to STRING_TYPE,
                COL2 to STRING_TYPE,
                COL3 to "Int32",
                COL5 to "DateTime64(3)"
            )
        val expected4 =
            AlterationSummary( // Added col2
                added = mapOf(COL2 to STRING_TYPE),
                modified = emptyMap(),
                deleted = emptySet()
            )
        val actual4 = clickhouseAirbyteClient.getChangedColumns(tableColumns4, catalogColumns4)
        Assertions.assertEquals(expected4, actual4)
    }
}
