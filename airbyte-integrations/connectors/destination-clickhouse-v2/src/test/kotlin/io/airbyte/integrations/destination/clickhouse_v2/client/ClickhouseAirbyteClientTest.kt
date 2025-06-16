/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.client

import com.clickhouse.client.api.Client as ClickHouseClientRaw
import com.clickhouse.client.api.command.CommandResponse
import com.clickhouse.client.api.query.QueryResponse
import com.clickhouse.data.ClickHouseColumn
import com.clickhouse.data.ClickHouseDataType
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.clickhouse_v2.config.ClickhouseFinalTableNameGenerator
import io.airbyte.integrations.destination.clickhouse_v2.model.AlterationSummary
import io.airbyte.integrations.destination.clickhouse_v2.model.isEmpty
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.mockk.spyk
import java.util.concurrent.CompletableFuture
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class ClickhouseAirbyteClientTest {
    // Mocks
    private val client: ClickHouseClientRaw = mockk(relaxed = true)
    private val clickhouseSqlGenerator: ClickhouseSqlGenerator = mockk(relaxed = true)
    private val clickhouseFinalTableNameGenerator: ClickhouseFinalTableNameGenerator =
        mockk(relaxed = true)

    // Client
    private val clickhouseAirbyteClient =
        spyk(
            ClickhouseAirbyteClient(
                client,
                clickhouseSqlGenerator,
                clickhouseFinalTableNameGenerator
            )
        )

    @Test
    fun testExecute() = runTest {
        val expectedResponse = mockk<CommandResponse>(relaxed = true)
        val completableFuture = CompletableFuture.completedFuture(expectedResponse)
        coEvery { client.execute(DUMMY_SENTENCE) } returns completableFuture

        clickhouseAirbyteClient.execute(DUMMY_SENTENCE)

        coVerify { client.execute(DUMMY_SENTENCE) }
    }

    @Test
    fun testQuery() = runTest {
        val expectedResponse = mockk<QueryResponse>(relaxed = true)
        val completableFuture = CompletableFuture.completedFuture(expectedResponse)
        coEvery { client.query(DUMMY_SENTENCE) } returns completableFuture

        clickhouseAirbyteClient.query(DUMMY_SENTENCE)

        coVerify { client.query(DUMMY_SENTENCE) }
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
        val catalogColumns = mapOf(COL1 to STRING_TYPE, COL2 to INT_TYPE)
        val expected =
            AlterationSummary(added = emptyMap(), modified = emptyMap(), deleted = emptySet())
        val actual = clickhouseAirbyteClient.getChangedColumns(tableColumns, catalogColumns)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test added columns`() {
        val tableColumns = listOf(getMockColumn(COL1, ClickHouseDataType.String))
        val catalogColumns =
            mapOf(COL1 to STRING_TYPE, COL2 to INT_TYPE, COL3 to FLOAT_TYPE) // Added col2 and col3
        val expected =
            AlterationSummary(
                added = mapOf(COL2 to INT_TYPE, COL3 to FLOAT_TYPE),
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
        val catalogColumns2 = mapOf(COL2 to STRING_TYPE, COL3 to INT_TYPE)
        val expected2 =
            AlterationSummary(
                added = mapOf(COL2 to STRING_TYPE, COL3 to INT_TYPE),
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
            mapOf(COL1 to STRING_TYPE, COL2 to STRING_TYPE, COL3 to STRING_TYPE, COL4 to FLOAT_TYPE)
        val expected =
            AlterationSummary( // Added col2 and col4, modified col3
                added = mapOf(COL2 to STRING_TYPE, COL4 to FLOAT_TYPE),
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
        val catalogColumns3 = mapOf(COL1 to STRING_TYPE, COL2 to STRING_TYPE, COL3 to INT_TYPE)
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
                COL3 to INT_TYPE,
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

    @Test
    fun `test ensure schema matches`() = runTest {
        val mockAlterationSummary =
            mockk<AlterationSummary>(relaxed = true) { every { isEmpty() } returns false }

        val mockTableName = mockk<TableName>(relaxed = true)
        val alterTableStatement = "ALTER TABLE my_table ADD COLUMN new_col String"

        coEvery { clickhouseAirbyteClient.getChangedColumns(any(), any()) } returns
            mockAlterationSummary
        coEvery { clickhouseSqlGenerator.alterTable(mockAlterationSummary, mockTableName) } returns
            alterTableStatement
        coEvery { clickhouseAirbyteClient.execute(alterTableStatement) } returns
            mockk(relaxed = true)
        every { clickhouseFinalTableNameGenerator.getTableName(any()) } returns mockTableName

        val columnMapping = ColumnNameMapping(mapOf())
        val stream =
            mockk<DestinationStream>() {
                every { descriptor } returns
                    mockk(relaxed = true) {
                        every { name } returns "my_table"
                        every { namespace } returns "my_namespace"
                    }
                every { schema } returns
                    mockk(relaxed = true) {
                        every { isObject } returns true
                        every { asColumns() } returns LinkedHashMap.newLinkedHashMap(0)
                    }
            }
        clickhouseAirbyteClient.ensureSchemaMatches(stream, mockTableName, columnMapping)

        coVerify {
            clickhouseAirbyteClient.getChangedColumns(any(), any())
            clickhouseSqlGenerator.alterTable(mockAlterationSummary, mockTableName)
            clickhouseAirbyteClient.execute(alterTableStatement)
        }
    }

    companion object {
        // Constants
        private const val COL1 = "col1"
        private const val COL2 = "col2"
        private const val COL3 = "col3"
        private const val COL4 = "col4"
        private const val COL5 = "col5"
        private const val STRING_TYPE = "String"
        private const val INT_TYPE = "Int32"
        private const val FLOAT_TYPE = "Float64"
        private const val DUMMY_SENTENCE = "SELECT 1"
    }
}
