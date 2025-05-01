/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.load.db.orchestration

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.RawTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogFactory
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class TableNameMapFactoryTest {

    @Test
    fun testThrowOnEmptyCatalog() {
        val rawTableNameGenerator = mockk<RawTableNameGenerator>()
        val finalTableNameGenerator = mockk<FinalTableNameGenerator>()
        val columnNameGenerator = mockk<ColumnNameGenerator>()

        val emptyCatalog = mockk<DestinationCatalog>()
        every { emptyCatalog.streams } returns emptyList()

        val factory =
            TableCatalogFactory(
                emptyCatalog,
                rawTableNameGenerator,
                finalTableNameGenerator,
                columnNameGenerator
            )

        val exception = assertThrows(ConfigErrorException::class.java) { factory.get() }
        assertTrue(exception.message!!.contains("catalog contained no streams"))
    }

    @Test
    fun testTableNameCollision() {
        val rawTableNameGenerator = mockk<RawTableNameGenerator>()
        val finalTableNameGenerator = mockk<FinalTableNameGenerator>()
        val columnNameGenerator = mockk<ColumnNameGenerator>()

        // Create the same streams as in the original test - "foobarfoo" and "foofoo"
        val stream1 = createTestStream("foobarfoo", "a")
        val stream2 = createTestStream("foofoo", "a")
        val catalog = DestinationCatalog(listOf(stream1, stream2))

        // Mock the generators to simulate name collision by removing "bar" for both raw and final
        // table names
        every { rawTableNameGenerator.getTableName(stream1.descriptor) } returns
            TableName(
                "airbyte_internal",
                "foofoo"
            ) // foobarfoo becomes foofoo when "bar" is removed
        every { rawTableNameGenerator.getTableName(stream2.descriptor) } returns
            TableName("airbyte_internal", "foofoo")

        every { finalTableNameGenerator.getTableName(stream1.descriptor) } returns
            TableName("a", "foofoo") // foobarfoo becomes foofoo when "bar" is removed
        every { finalTableNameGenerator.getTableName(stream2.descriptor) } returns
            TableName("a", "foofoo")

        // Simple pass-through for column name generator (not needed for this test)
        every { columnNameGenerator.getColumnName(any()) } answers
            { call ->
                val input = call.invocation.args[0] as String
                ColumnNameGenerator.ColumnName(input, input)
            }

        val factory =
            TableCatalogFactory(
                catalog,
                rawTableNameGenerator,
                finalTableNameGenerator,
                columnNameGenerator
            )
        val tableCatalog = factory.get()

        // Get the final table names for both streams
        val stream1TableInfo = tableCatalog[stream1]!!
        val stream2TableInfo = tableCatalog[stream2]!!

        // One stream should get the original name, the other should get a hash suffix
        val finalTableNames =
            setOf(
                stream1TableInfo.tableNames.finalTableName!!.name,
                stream2TableInfo.tableNames.finalTableName!!.name
            )

        // Verify that one name is "final_foofoo" and the other has the expected hash suffix
        assertAll(
            { assertTrue(stream1TableInfo.tableNames.finalTableName!!.name == "foofoo") },
            { assertTrue(stream1TableInfo.tableNames.finalTableName!!.namespace == "a") },
            { assertTrue(stream2TableInfo.tableNames.finalTableName!!.name == "foofoo_3fd") },
            { assertTrue(stream2TableInfo.tableNames.finalTableName!!.namespace == "a") }
        )

        // Now check raw table names with exact expected suffix
        assertAll(
            { assertTrue(stream1TableInfo.tableNames.rawTableName!!.name == "foofoo") },
            {
                assertTrue(
                    stream1TableInfo.tableNames.rawTableName!!.namespace ==
                        DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
                )
            },
            { assertTrue(stream2TableInfo.tableNames.rawTableName!!.name == "foofoo_3fd") },
            {
                assertTrue(
                    stream2TableInfo.tableNames.rawTableName!!.namespace ==
                        DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
                )
            }
        )
    }

    @Test
    fun testTruncatingColumnNameCollision() {
        val rawTableNameGenerator = mockk<RawTableNameGenerator>()
        val finalTableNameGenerator = mockk<FinalTableNameGenerator>()
        val columnNameGenerator = mockk<ColumnNameGenerator>()

        val schema = createSchemaWithLongColumnNames()
        val stream = createTestStream("stream", "namespace", schema)
        val catalog = DestinationCatalog(listOf(stream))
        every { rawTableNameGenerator.getTableName(any()) } returns
            TableName("raw_dataset", "raw_stream")
        every { finalTableNameGenerator.getTableName(any()) } returns
            TableName("final_dataset", "final_stream")

        every { columnNameGenerator.getColumnName(any()) } answers
            { call ->
                val input = call.invocation.args[0] as String
                val truncated = input.substring(0, 10.coerceAtMost(input.length))
                ColumnNameGenerator.ColumnName(truncated, truncated)
            }

        val factory =
            TableCatalogFactory(
                catalog,
                rawTableNameGenerator,
                finalTableNameGenerator,
                columnNameGenerator
            )
        val tableCatalog = factory.get()

        val columnMapping = tableCatalog[stream]!!.columnNameMapping
        val mappedNames =
            listOf(
                columnMapping["aVeryLongColumnName"]!!,
                columnMapping["aVeryLongColumnNameWithMoreTextAfterward"]!!
            )

        assertEquals(2, mappedNames.size)
        assertEquals("aVeryLongC", mappedNames[0])
        assertEquals("aV36rd", mappedNames[1])
    }

    private fun createSchemaWithLongColumnNames(): AirbyteType {
        val schemaProperties = linkedMapOf<String, FieldType>()
        schemaProperties["aVeryLongColumnName"] =
            FieldType(io.airbyte.cdk.load.data.StringType, true)
        schemaProperties["aVeryLongColumnNameWithMoreTextAfterward"] =
            FieldType(io.airbyte.cdk.load.data.StringType, true)
        return ObjectType(schemaProperties)
    }

    @Test
    fun testColumnNameCollision() {
        val rawTableNameGenerator = mockk<RawTableNameGenerator>()
        val finalTableNameGenerator = mockk<FinalTableNameGenerator>()
        val columnNameGenerator = mockk<ColumnNameGenerator>()

        // Create a schema with columns that will have name collision after processing
        val schemaProperties = linkedMapOf<String, FieldType>()
        schemaProperties["foobarfoo"] = FieldType(io.airbyte.cdk.load.data.StringType, true)
        schemaProperties["foofoo"] = FieldType(io.airbyte.cdk.load.data.StringType, true)
        val schema = ObjectType(schemaProperties)

        val stream = createTestStream("stream", "namespace", schema)
        val catalog = DestinationCatalog(listOf(stream))

        every { rawTableNameGenerator.getTableName(any()) } returns
            TableName("raw_dataset", "raw_stream")
        every { finalTableNameGenerator.getTableName(any()) } returns
            TableName("final_dataset", "final_stream")

        // Mock the column name generator to simulate name collision by removing "bar"
        every { columnNameGenerator.getColumnName(any()) } answers
            { call ->
                val input = call.invocation.args[0] as String
                val processedName = input.replace("bar", "")
                ColumnNameGenerator.ColumnName(processedName, processedName)
            }

        val factory =
            TableCatalogFactory(
                catalog,
                rawTableNameGenerator,
                finalTableNameGenerator,
                columnNameGenerator
            )
        val tableCatalog = factory.get()

        val columnMapping = tableCatalog[stream]!!.columnNameMapping
        val mappedColumns = listOf(columnMapping["foobarfoo"]!!, columnMapping["foofoo"]!!)

        // Verify column name collision was properly resolved
        // One column should be "foofoo" and the other should be "foofoo_1"
        assertAll(
            { assertEquals(2, mappedColumns.size) },
            { assertEquals("foofoo", mappedColumns[0]) },
            { assertEquals("foofoo_1", mappedColumns[1]) }
        )
    }

    private fun createTestStream(
        name: String,
        namespace: String,
        schema: AirbyteType = ObjectType(linkedMapOf())
    ): DestinationStream {
        return DestinationStream(
            descriptor = DestinationStream.Descriptor(namespace, name),
            importType = Append,
            schema = schema,
            generationId = 1L,
            minimumGenerationId = 0L,
            syncId = 0L
        )
    }
}
