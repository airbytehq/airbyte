/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.client

import com.clickhouse.client.api.Client as ClickHouseClientRaw
import com.clickhouse.client.api.command.CommandResponse
import com.clickhouse.client.api.query.QueryResponse
import com.clickhouse.data.ClickHouseColumn
import com.clickhouse.data.ClickHouseDataType
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.integrations.destination.clickhouse.config.ClickhouseFinalTableNameGenerator
import io.airbyte.integrations.destination.clickhouse.model.AlterationSummary
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.coVerifyOrder
import io.mockk.every
import io.mockk.mockk
import io.mockk.spyk
import io.mockk.verify
import java.util.concurrent.CompletableFuture
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class ClickhouseAirbyteClientTest {
    // Mocks
    private val client: ClickHouseClientRaw = mockk(relaxed = true)
    private val clickhouseSqlGenerator: ClickhouseSqlGenerator = mockk(relaxed = true)
    private val clickhouseFinalTableNameGenerator: ClickhouseFinalTableNameGenerator =
        mockk(relaxed = true)
    private val tempTableNameGenerator: TempTableNameGenerator = mockk(relaxed = true)
    private val clickhouseConfiguration: ClickhouseConfiguration = mockk(relaxed = true)
    private val columnNameMapping: ColumnNameMapping = ColumnNameMapping(emptyMap())

    // Client
    private val clickhouseAirbyteClient =
        spyk(
            ClickhouseAirbyteClient(
                client,
                clickhouseSqlGenerator,
                clickhouseFinalTableNameGenerator,
                tempTableNameGenerator,
                clickhouseConfiguration
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
            AlterationSummary(
                added = emptyMap(),
                modified = emptyMap(),
                deleted = emptySet(),
                hasDedupChange = false
            )
        val actual =
            clickhouseAirbyteClient.getChangedColumns(
                tableColumns,
                catalogColumns,
                listOf(),
                listOf(),
                columnNameMapping,
            )
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
                deleted = emptySet(),
                hasDedupChange = false,
            )
        val actual =
            clickhouseAirbyteClient.getChangedColumns(
                tableColumns,
                catalogColumns,
                listOf(),
                listOf(),
                columnNameMapping,
            )
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
                deleted = emptySet(),
                hasDedupChange = false,
            )
        val actual =
            clickhouseAirbyteClient.getChangedColumns(
                tableColumns,
                catalogColumns,
                listOf(),
                listOf(),
                columnNameMapping,
            )
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test deleted columns`() {
        val tableColumns =
            listOf(getMockColumn(columnName = COL1, columnType = ClickHouseDataType.String))
        val catalogColumns = mapOf(COL1 to STRING_TYPE)
        val expected =
            AlterationSummary(
                added = emptyMap(),
                modified = emptyMap(),
                deleted = emptySet(),
                hasDedupChange = false,
            )
        val actual =
            clickhouseAirbyteClient.getChangedColumns(
                tableColumns,
                catalogColumns,
                listOf(),
                listOf(),
                columnNameMapping,
            )
        Assertions.assertEquals(expected, actual)

        val tableColumns2 =
            listOf(getMockColumn(columnName = COL1, columnType = ClickHouseDataType.String))
        val catalogColumns2 = mapOf(COL2 to STRING_TYPE, COL3 to INT_TYPE)
        val expected2 =
            AlterationSummary(
                added = mapOf(COL2 to STRING_TYPE, COL3 to INT_TYPE),
                modified = emptyMap(), // No modified columns
                deleted = setOf(COL1),
                hasDedupChange = false,
            )
        val actual2 =
            clickhouseAirbyteClient.getChangedColumns(
                tableColumns2,
                catalogColumns2,
                listOf(),
                listOf(),
                columnNameMapping,
            )
        Assertions.assertEquals(expected2, actual2)
    }

    @Test
    fun `test dedup change columns`() {
        val tableColumns: List<ClickHouseColumn> = listOf()
        val catalogColumns: Map<String, String> = mapOf()
        val expected =
            AlterationSummary(
                added = emptyMap(), // No added columns
                modified = mapOf(),
                deleted = emptySet(),
                hasDedupChange = true,
            )
        var actual =
            clickhouseAirbyteClient.getChangedColumns(
                tableColumns,
                catalogColumns,
                listOf("col1"),
                listOf(),
                columnNameMapping,
            )
        Assertions.assertEquals(expected, actual)
        actual =
            clickhouseAirbyteClient.getChangedColumns(
                tableColumns,
                catalogColumns,
                listOf(),
                listOf("col2"),
                columnNameMapping,
            )
        Assertions.assertEquals(expected, actual)
        actual =
            clickhouseAirbyteClient.getChangedColumns(
                tableColumns,
                catalogColumns,
                listOf("col1"),
                listOf("col2"),
                columnNameMapping,
            )
        Assertions.assertEquals(expected, actual)
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
                deleted = emptySet(),
                hasDedupChange = false,
            )
        val actual =
            clickhouseAirbyteClient.getChangedColumns(
                tableColumns,
                catalogColumns,
                listOf(),
                listOf(),
                columnNameMapping,
            )
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
                deleted = emptySet(),
                hasDedupChange = false,
            )
        val actual2 =
            clickhouseAirbyteClient.getChangedColumns(
                tableColumns2,
                catalogColumns2,
                listOf(),
                listOf(),
                columnNameMapping,
            )
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
                deleted = emptySet(),
                hasDedupChange = false,
            )
        val actual3 =
            clickhouseAirbyteClient.getChangedColumns(
                tableColumns3,
                catalogColumns3,
                listOf(),
                listOf(),
                columnNameMapping,
            )
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
                deleted = emptySet(),
                hasDedupChange = false,
            )
        val actual4 =
            clickhouseAirbyteClient.getChangedColumns(
                tableColumns4,
                catalogColumns4,
                listOf(),
                listOf(),
                columnNameMapping,
            )
        Assertions.assertEquals(expected4, actual4)
    }

    private fun mockCHSchemaWithAirbyteColumns() {
        every { client.getTableSchema(any(), any()) } returns
            mockk {
                every { columns } returns
                    listOf(
                        mockk { every { columnName } returns Meta.COLUMN_NAME_AB_RAW_ID },
                        mockk { every { columnName } returns Meta.COLUMN_NAME_AB_EXTRACTED_AT },
                        mockk { every { columnName } returns Meta.COLUMN_NAME_AB_META },
                        mockk { every { columnName } returns Meta.COLUMN_NAME_AB_GENERATION_ID },
                    )
            }
    }

    @Test
    fun `test ensure schema matches`() = runTest {
        val alterationSummary =
            AlterationSummary(
                added = mapOf("new_col" to "String"),
                modified = emptyMap(),
                deleted = emptySet(),
                hasDedupChange = false
            )

        val mockTableName = mockk<TableName>(relaxed = true)
        val alterTableStatement = "ALTER TABLE my_table ADD COLUMN new_col String"

        coEvery {
            clickhouseAirbyteClient.getChangedColumns(any(), any(), any(), any(), any())
        } returns alterationSummary
        coEvery { clickhouseSqlGenerator.alterTable(alterationSummary, mockTableName) } returns
            alterTableStatement
        coEvery { clickhouseAirbyteClient.execute(alterTableStatement) } returns
            mockk(relaxed = true)
        every { clickhouseFinalTableNameGenerator.getTableName(any()) } returns mockTableName

        mockCHSchemaWithAirbyteColumns()

        val columnMapping = ColumnNameMapping(mapOf())
        val stream =
            mockk<DestinationStream>() {
                every { mappedDescriptor } returns
                    mockk(relaxed = true) {
                        every { name } returns "my_table"
                        every { namespace } returns "my_namespace"
                    }
                every { schema } returns
                    mockk(relaxed = true) {
                        every { isObject } returns true
                        every { asColumns() } returns LinkedHashMap.newLinkedHashMap(0)
                    }
                every { importType } returns Append
            }
        clickhouseAirbyteClient.ensureSchemaMatches(stream, mockTableName, columnMapping)

        coVerifyOrder {
            clickhouseAirbyteClient.getChangedColumns(any(), any(), any(), any(), any())
            clickhouseSqlGenerator.alterTable(alterationSummary, mockTableName)
            clickhouseAirbyteClient.execute(alterTableStatement)
        }
    }

    @Test
    fun `test ensure schema matches with dedup changes`() = runTest {
        val alterationSummary =
            AlterationSummary(
                added = emptyMap(),
                modified = emptyMap(),
                deleted = setOf("test"),
                hasDedupChange = true
            )

        val finalTableName = TableName("fin", "al")
        val tempTableName = TableName("temp", "orary")

        coEvery {
            clickhouseAirbyteClient.getChangedColumns(any(), any(), any(), any(), any())
        } returns alterationSummary
        coEvery { clickhouseAirbyteClient.execute(any()) } returns mockk(relaxed = true)
        every { tempTableNameGenerator.generate(any()) } returns tempTableName
        every { clickhouseFinalTableNameGenerator.getTableName(any()) } returns finalTableName

        mockCHSchemaWithAirbyteColumns()

        val columnMapping = ColumnNameMapping(mapOf())
        val stream =
            mockk<DestinationStream>() {
                every { mappedDescriptor } returns
                    mockk(relaxed = true) {
                        every { name } returns "my_table"
                        every { namespace } returns "my_namespace"
                    }
                every { schema } returns
                    mockk(relaxed = true) {
                        every { isObject } returns true
                        every { asColumns() } returns LinkedHashMap.newLinkedHashMap(0)
                    }
                every { importType } returns Append
            }
        clickhouseAirbyteClient.ensureSchemaMatches(stream, finalTableName, columnMapping)

        coVerify(exactly = 0) { clickhouseSqlGenerator.alterTable(any(), any()) }

        coVerifyOrder {
            clickhouseAirbyteClient.getChangedColumns(any(), any(), any(), any(), any())
            clickhouseSqlGenerator.createNamespace(tempTableName.namespace)
            clickhouseSqlGenerator.createTable(stream, tempTableName, columnMapping, true)
            clickhouseSqlGenerator.copyTable(columnMapping, finalTableName, tempTableName)
            clickhouseSqlGenerator.exchangeTable(tempTableName, finalTableName)
            clickhouseSqlGenerator.dropTable(tempTableName)
        }
        coVerify(exactly = 5) { clickhouseAirbyteClient.execute(any()) }
    }

    @Test
    fun `test ensure schema matches fails if no airbyte columns`() = runTest {
        val finalTableName = TableName("fin", "al")

        every { clickhouseFinalTableNameGenerator.getTableName(any()) } returns finalTableName

        val columnMapping = ColumnNameMapping(mapOf())
        val stream =
            mockk<DestinationStream>() {
                every { mappedDescriptor } returns
                    mockk(relaxed = true) {
                        every { name } returns "my_table"
                        every { namespace } returns "my_namespace"
                    }
            }

        assertThrows<ConfigErrorException> {
            clickhouseAirbyteClient.ensureSchemaMatches(stream, finalTableName, columnMapping)
        }
    }

    @Test
    fun `test overwrite table`() = runTest {
        val sourceTableName = TableName("source_db", "source_table")
        val targetTableName = TableName("target_db", "target_table")
        val exchangeTableSql =
            "EXCHANGE TABLES `source_db`.`source_table` AND `target_db`.`target_table`"
        val dropTableSql = "DROP TABLE `source_db`.`source_table`"

        every { clickhouseSqlGenerator.exchangeTable(sourceTableName, targetTableName) } returns
            exchangeTableSql
        every { clickhouseSqlGenerator.dropTable(sourceTableName) } returns dropTableSql
        coEvery { clickhouseAirbyteClient.execute(exchangeTableSql) } returns mockk()
        coEvery { clickhouseAirbyteClient.execute(dropTableSql) } returns mockk()

        clickhouseAirbyteClient.overwriteTable(sourceTableName, targetTableName)

        verify { clickhouseSqlGenerator.exchangeTable(sourceTableName, targetTableName) }
        verify { clickhouseSqlGenerator.dropTable(sourceTableName) }
        coVerifyOrder {
            clickhouseAirbyteClient.execute(exchangeTableSql)
            clickhouseAirbyteClient.execute(dropTableSql)
        }
    }

    @Test
    fun `test getAirbyteSchemaWithClickhouseType with simple schema`() {
        val columns = LinkedHashMap.newLinkedHashMap<String, FieldType>(1)
        columns["field 1"] = FieldType(StringType, true)

        val stream =
            mockk<DestinationStream>() {
                every { mappedDescriptor } returns
                    mockk(relaxed = true) {
                        every { name } returns "my_table"
                        every { namespace } returns "my_namespace"
                    }
                every { schema } returns
                    mockk(relaxed = true) {
                        every { isObject } returns true
                        every { asColumns() } returns columns
                    }
                every { importType } returns Append
            }

        val expected =
            mapOf(
                "field_1" to "String",
            )
        val actual = clickhouseAirbyteClient.getAirbyteSchemaWithClickhouseType(stream)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test copyIntersectionColumn`() = runTest {
        val chColumn1 = mockk<ClickHouseColumn>() { every { columnName } returns "column1" }
        val chColumn2 = mockk<ClickHouseColumn>() { every { columnName } returns "column2" }
        val tableSchemaWithoutAirbyteColumns =
            listOf(
                chColumn1,
                chColumn2,
            )
        val columnNameMapping = ColumnNameMapping(mapOf("2" to "column2", "3" to "column3"))
        val properTableName = TableName("table", "name")
        val tempTableName = TableName("table", "tmp")

        coEvery { clickhouseAirbyteClient.execute(any()) } returns mockk()

        clickhouseAirbyteClient.copyIntersectionColumn(
            tableSchemaWithoutAirbyteColumns,
            columnNameMapping,
            properTableName,
            tempTableName,
        )

        verify {
            clickhouseSqlGenerator.copyTable(
                ColumnNameMapping(mapOf("2" to "column2")),
                properTableName,
                tempTableName,
            )
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
