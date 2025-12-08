/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.client

import com.clickhouse.client.api.Client as ClickHouseClientRaw
import com.clickhouse.client.api.command.CommandResponse
import com.clickhouse.client.api.query.QueryResponse
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.clickhouse.config.ClickhouseFinalTableNameGenerator
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

    // Client
    private val clickhouseAirbyteClient =
        spyk(
            ClickhouseAirbyteClient(
                client,
                clickhouseSqlGenerator,
                tempTableNameGenerator,
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
        val columnChangeset =
            ColumnChangeset(
                columnsToAdd = mapOf("new_col" to ColumnType("String", true)),
                columnsToChange = emptyMap(),
                columnsToDrop = emptyMap(),
                columnsToRetain = emptyMap(),
            )

        val mockTableName = mockk<TableName>(relaxed = true)
        val alterTableStatement = "ALTER TABLE my_table ADD COLUMN new_col String"

        coEvery { clickhouseSqlGenerator.alterTable(columnChangeset, mockTableName) } returns
            alterTableStatement
        coEvery { clickhouseAirbyteClient.execute(alterTableStatement) } returns
            mockk(relaxed = true)
        every { clickhouseFinalTableNameGenerator.getTableName(any()) } returns mockTableName

        mockCHSchemaWithAirbyteColumns()

        val columnMapping = ColumnNameMapping(mapOf())
        val stream =
            mockk<DestinationStream> {
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
                every { tableSchema } returns
                    mockk(relaxed = true) {
                        every { columnSchema } returns
                            mockk(relaxed = true) {
                                every { inputSchema } returns LinkedHashMap.newLinkedHashMap(0)
                                every { inputToFinalColumnNames } returns emptyMap()
                            }
                        every { getPrimaryKey() } returns emptyList()
                        every { getCursor() } returns emptyList()
                    }
            }
        clickhouseAirbyteClient.applyChangeset(
            stream,
            columnMapping,
            mockTableName,
            mapOf("new_col" to ColumnType("String", true)),
            columnChangeset,
        )

        coVerifyOrder {
            clickhouseSqlGenerator.alterTable(columnChangeset, mockTableName)
            clickhouseAirbyteClient.execute(alterTableStatement)
        }
    }

    @Test
    fun `test ensure schema matches with dedup changes`() = runTest {
        val columnChangeset =
            ColumnChangeset(
                columnsToAdd = emptyMap(),
                // Note that we're changing the nullability of the column.
                // This will trigger the table-recreate logic.
                columnsToChange =
                    mapOf(
                        "something" to
                            ColumnTypeChange(
                                ColumnType("IrrelevantValue", false),
                                ColumnType("IrrelevantValue", true)
                            )
                    ),
                columnsToDrop = mapOf("test" to ColumnType("String", true)),
                columnsToRetain = emptyMap(),
            )

        val finalTableName = TableName("fin", "al")
        val tempTableName = TableName("temp", "orary")

        coEvery { clickhouseAirbyteClient.execute(any()) } returns mockk(relaxed = true)
        every { tempTableNameGenerator.generate(any()) } returns tempTableName
        every { clickhouseFinalTableNameGenerator.getTableName(any()) } returns finalTableName

        mockCHSchemaWithAirbyteColumns()

        val columnMapping = ColumnNameMapping(mapOf())
        val tableSchema1: StreamTableSchema =
            mockk(relaxed = true) {
                every { columnSchema } returns
                    mockk(relaxed = true) {
                        every { inputSchema } returns LinkedHashMap.newLinkedHashMap(0)
                        every { inputToFinalColumnNames } returns emptyMap()
                    }
                every { getPrimaryKey() } returns emptyList()
                every { getCursor() } returns emptyList()
            }
        val stream =
            mockk<DestinationStream> {
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
                every { tableSchema } returns tableSchema1
            }
        clickhouseAirbyteClient.applyChangeset(
            stream,
            columnMapping,
            finalTableName,
            emptyMap(),
            columnChangeset,
        )

        coVerify(exactly = 0) { clickhouseSqlGenerator.alterTable(any(), any()) }

        coVerifyOrder {
            clickhouseSqlGenerator.createNamespace(tempTableName.namespace)
            clickhouseSqlGenerator.createTable(tempTableName, tableSchema1, true)
            clickhouseSqlGenerator.copyTable(setOf("something"), finalTableName, tempTableName)
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
            mockk<DestinationStream> {
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
            mockk<DestinationStream> {
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
                every { tableSchema } returns
                    mockk(relaxed = true) {
                        every { columnSchema } returns
                            mockk(relaxed = true) {
                                every { inputSchema } returns columns
                                every { inputToFinalColumnNames } returns
                                    mapOf("field 1" to "field_1")
                                every { finalSchema } returns
                                    mapOf("field_1" to ColumnType("String", true))
                            }
                        every { getPrimaryKey() } returns emptyList()
                        every { getCursor() } returns emptyList()
                    }
            }

        val columnMapping = ColumnNameMapping(mapOf("field 1" to "field_1"))

        val expected =
            TableSchema(
                mapOf(
                    "field_1" to ColumnType("String", true),
                ),
            )
        val actual = clickhouseAirbyteClient.computeSchema(stream, columnMapping)
        Assertions.assertEquals(expected, actual)
    }

    companion object {
        // Constants
        private const val DUMMY_SENTENCE = "SELECT 1"
    }
}
