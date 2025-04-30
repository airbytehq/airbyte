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
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogFactory
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
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

        val stream1 = createTestStream("foobarfoo", "a")
        val stream2 = createTestStream("foofoo", "a")
        val catalog = DestinationCatalog(listOf(stream1, stream2))

        every { rawTableNameGenerator.getTableName(stream1.descriptor) } returns
            TableName("raw_a", "raw_foofoo")
        every { rawTableNameGenerator.getTableName(stream2.descriptor) } returns
            TableName("raw_a", "raw_foofoo")

        every { finalTableNameGenerator.getTableName(stream1.descriptor) } returns
            TableName("final_a", "final_foofoo")
        every { finalTableNameGenerator.getTableName(stream2.descriptor) } returns
            TableName("final_a", "final_foofoo")
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

        val tableNames1 = tableCatalog[stream1]!!.tableNames
        val tableNames2 = tableCatalog[stream2]!!.tableNames

        val rawTableNames = setOf(tableNames1.rawTableName!!.name, tableNames2.rawTableName!!.name)
        val finalTableNames =
            setOf(tableNames1.finalTableName!!.name, tableNames2.finalTableName!!.name)
        assertTrue(rawTableNames.contains("raw_foofoo"))
        val rawTableNameWithHash = rawTableNames.first { it != "raw_foofoo" }
        assertTrue(rawTableNameWithHash.startsWith("raw_foofoo_"))
        assertTrue(
            rawTableNameWithHash.substring("raw_foofoo_".length).matches(Regex("[0-9a-f]{3}"))
        )

        // Final table names: One should be the original, one should have a hash suffix
        assertTrue(finalTableNames.contains("final_foofoo"))
        val finalTableNameWithHash = finalTableNames.first { it != "final_foofoo" }
        assertTrue(finalTableNameWithHash.startsWith("final_foofoo_"))
        assertTrue(
            finalTableNameWithHash.substring("final_foofoo_".length).matches(Regex("[0-9a-f]{3}"))
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

        setupColumnNameGeneratorWithTruncation(columnNameGenerator)

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

    private fun setupColumnNameGeneratorWithTruncation(columnNameGenerator: ColumnNameGenerator) {
        every { columnNameGenerator.getColumnName(any()) } answers
            { call ->
                val input = call.invocation.args[0] as String
                val truncated = input.substring(0, 10.coerceAtMost(input.length))
                ColumnNameGenerator.ColumnName(truncated, truncated)
            }
    }

    @Test
    fun testMultipleColumnNameCollisions() {
        val rawTableNameGenerator = mockk<RawTableNameGenerator>()
        val finalTableNameGenerator = mockk<FinalTableNameGenerator>()
        val columnNameGenerator = mockk<ColumnNameGenerator>()

        val schema = createSchemaWithMultipleColumnCollisions()
        val stream = createTestStream("stream", "namespace", schema)
        val catalog = DestinationCatalog(listOf(stream))
        every { rawTableNameGenerator.getTableName(any()) } returns
            TableName("raw_dataset", "raw_stream")
        every { finalTableNameGenerator.getTableName(any()) } returns
            TableName("final_dataset", "final_stream")

        every { columnNameGenerator.getColumnName(any()) } answers
            { call ->
                val input = call.invocation.args[0] as String
                if (input.startsWith("column") && !input.contains("_")) {
                    ColumnNameGenerator.ColumnName("column", "column")
                } else if (input.matches(Regex("column_\\d+"))) {
                    val suffix = input.substring("column".length)
                    ColumnNameGenerator.ColumnName("column$suffix", "column$suffix")
                } else {
                    ColumnNameGenerator.ColumnName(input, input)
                }
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

        val columnNames = columnMapping.values.toSet()
        assertEquals(4, columnNames.size)

        assertEquals("column", columnMapping["column1"])

        assertTrue(columnMapping["column2"]!!.startsWith("column_"))
        assertTrue(columnMapping["column3"]!!.startsWith("column_"))
        assertTrue(columnMapping["column4"]!!.startsWith("column_"))
        val mappedNames =
            listOf(
                columnMapping["column1"]!!,
                columnMapping["column2"]!!,
                columnMapping["column3"]!!,
                columnMapping["column4"]!!
            )

        for (i in mappedNames.indices) {
            for (j in i + 1 until mappedNames.size) {
                assertNotEquals(mappedNames[i], mappedNames[j])
            }
        }
    }

    private fun createSchemaWithMultipleColumnCollisions(): AirbyteType {
        val schemaProperties = linkedMapOf<String, FieldType>()
        schemaProperties["column1"] = FieldType(io.airbyte.cdk.load.data.StringType, true)
        schemaProperties["column2"] = FieldType(io.airbyte.cdk.load.data.StringType, true)
        schemaProperties["column3"] = FieldType(io.airbyte.cdk.load.data.StringType, true)
        schemaProperties["column4"] = FieldType(io.airbyte.cdk.load.data.StringType, true)
        return ObjectType(schemaProperties)
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
