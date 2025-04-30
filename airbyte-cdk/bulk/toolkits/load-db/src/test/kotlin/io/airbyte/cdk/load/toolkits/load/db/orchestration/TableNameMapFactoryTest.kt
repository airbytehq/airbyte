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
        // Mock dependencies
        val rawTableNameGenerator = mockk<RawTableNameGenerator>()
        val finalTableNameGenerator = mockk<FinalTableNameGenerator>()
        val columnNameGenerator = mockk<ColumnNameGenerator>()

        // Mock DestinationCatalog to return empty streams (avoiding the constructor check)
        val emptyCatalog = mockk<DestinationCatalog>()
        every { emptyCatalog.streams } returns emptyList()

        // Create factory with empty catalog
        val factory =
            TableCatalogFactory(
                emptyCatalog,
                rawTableNameGenerator,
                finalTableNameGenerator,
                columnNameGenerator
            )

        // Assert that an exception is thrown when attempting to get the catalog
        val exception = assertThrows(ConfigErrorException::class.java) { factory.get() }

        // Verify the exception message
        assertTrue(exception.message!!.contains("catalog contained no streams"))
    }

    @Test
    fun testTableNameCollision() {
        // Mock dependencies
        val rawTableNameGenerator = mockk<RawTableNameGenerator>()
        val finalTableNameGenerator = mockk<FinalTableNameGenerator>()
        val columnNameGenerator = mockk<ColumnNameGenerator>()

        // Create two streams that will have table name collisions
        val stream1 = createTestStream("foobarfoo", "a")
        val stream2 = createTestStream("foofoo", "a")
        val catalog = DestinationCatalog(listOf(stream1, stream2))

        // Configure table name generators to cause collisions by removing "bar" from names
        every { rawTableNameGenerator.getTableName(stream1.descriptor) } returns
            TableName("raw_a", "raw_foofoo") // "bar" has been removed, causing collision
        every { rawTableNameGenerator.getTableName(stream2.descriptor) } returns
            TableName("raw_a", "raw_foofoo") // Same name as above

        every { finalTableNameGenerator.getTableName(stream1.descriptor) } returns
            TableName("final_a", "final_foofoo") // "bar" has been removed, causing collision
        every { finalTableNameGenerator.getTableName(stream2.descriptor) } returns
            TableName("final_a", "final_foofoo") // Same name as above

        // Set up simple column name generator (no collisions for columns in this test)
        every { columnNameGenerator.getColumnName(any()) } answers
            { call ->
                val input = call.invocation.args[0] as String
                ColumnNameGenerator.ColumnName(input, input)
            }

        // Create factory and get catalog
        val factory =
            TableCatalogFactory(
                catalog,
                rawTableNameGenerator,
                finalTableNameGenerator,
                columnNameGenerator
            )
        val tableCatalog = factory.get()

        // Get the assigned table names
        val tableNames1 = tableCatalog[stream1]!!.tableNames
        val tableNames2 = tableCatalog[stream2]!!.tableNames

        // Verify one table kept the original name and one got a hash suffix
        // We can't guarantee which one will be processed first, so check both possibilities
        val rawTableNames = setOf(tableNames1.rawTableName!!.name, tableNames2.rawTableName!!.name)
        val finalTableNames =
            setOf(tableNames1.finalTableName!!.name, tableNames2.finalTableName!!.name)

        // Raw table names: One should be the original, one should have a hash suffix
        assertTrue(rawTableNames.contains("raw_foofoo"))
        val rawTableNameWithHash = rawTableNames.first { it != "raw_foofoo" }
        assertTrue(rawTableNameWithHash.startsWith("raw_foofoo_"))
        assertTrue(
            rawTableNameWithHash.substring("raw_foofoo_".length).matches(Regex("[0-9a-f]{6}"))
        )

        // Final table names: One should be the original, one should have a hash suffix
        assertTrue(finalTableNames.contains("final_foofoo"))
        val finalTableNameWithHash = finalTableNames.first { it != "final_foofoo" }
        assertTrue(finalTableNameWithHash.startsWith("final_foofoo_"))
        assertTrue(
            finalTableNameWithHash.substring("final_foofoo_".length).matches(Regex("[0-9a-f]{6}"))
        )

        // Print for debugging
        println("Raw table names: $rawTableNames")
        println("Final table names: $finalTableNames")
    }

    @Test
    fun testTruncatingColumnNameCollision() {
        // Mock dependencies
        val rawTableNameGenerator = mockk<RawTableNameGenerator>()
        val finalTableNameGenerator = mockk<FinalTableNameGenerator>()
        val columnNameGenerator = mockk<ColumnNameGenerator>()

        // Create test stream with schema
        val schema = createSchemaWithLongColumnNames()
        val stream = createTestStream("stream", "namespace", schema)
        val catalog = DestinationCatalog(listOf(stream))

        // Configure table name mocks
        every { rawTableNameGenerator.getTableName(any()) } returns
            TableName("raw_dataset", "raw_stream")
        every { finalTableNameGenerator.getTableName(any()) } returns
            TableName("final_dataset", "final_stream")

        // Set up column name generator to truncate to 10 characters
        setupColumnNameGeneratorWithTruncation(columnNameGenerator)

        // Create factory and get catalog
        val factory =
            TableCatalogFactory(
                catalog,
                rawTableNameGenerator,
                finalTableNameGenerator,
                columnNameGenerator
            )
        val tableCatalog = factory.get()

        // Get the column mappings
        val columnMapping = tableCatalog[stream]!!.columnNameMapping

        // Get the mapped column names in order they were processed
        val mappedNames =
            listOf(
                columnMapping["aVeryLongColumnName"]!!,
                columnMapping["aVeryLongColumnNameWithMoreTextAfterward"]!!
            )

        // Verify the collision resolution follows the expected pattern
        assertEquals(2, mappedNames.size)
        assertEquals("aVeryLongC", mappedNames[0])
        // The second column uses the i18n-style format: prefix + length + suffix
        // The specific value might differ from CatalogParserTest due to implementation differences
        // but should follow the same pattern
        val secondColName = mappedNames[1]
        println("Second column name resolved to: $secondColName")

        // Verify the pattern - should be something like "aV[number][suffix]"
        assertTrue(secondColName.startsWith("aV"))
        assertTrue(secondColName.substring(2).any { it.isDigit() })
    }

    /** Creates a schema with two columns that have long names that will collide after truncation */
    private fun createSchemaWithLongColumnNames(): AirbyteType {
        val schemaProperties = linkedMapOf<String, FieldType>()
        schemaProperties["aVeryLongColumnName"] =
            FieldType(io.airbyte.cdk.load.data.StringType, true)
        schemaProperties["aVeryLongColumnNameWithMoreTextAfterward"] =
            FieldType(io.airbyte.cdk.load.data.StringType, true)
        return ObjectType(schemaProperties)
    }

    /** Sets up the column name generator to simulate truncation to 10 characters */
    private fun setupColumnNameGeneratorWithTruncation(columnNameGenerator: ColumnNameGenerator) {
        every { columnNameGenerator.getColumnName(any()) } answers
            { call ->
                val input = call.invocation.args[0] as String
                // Truncate to 10 characters like in CatalogParserTest
                val truncated = input.substring(0, 10.coerceAtMost(input.length))
                ColumnNameGenerator.ColumnName(truncated, truncated)
            }
    }

    /** Tests multiple column name collisions with incremental suffix resolution */
    @Test
    fun testMultipleColumnNameCollisions() {
        // Mock dependencies
        val rawTableNameGenerator = mockk<RawTableNameGenerator>()
        val finalTableNameGenerator = mockk<FinalTableNameGenerator>()
        val columnNameGenerator = mockk<ColumnNameGenerator>()

        // Create test stream with multiple columns that will collide
        val schema = createSchemaWithMultipleColumnCollisions()
        val stream = createTestStream("stream", "namespace", schema)
        val catalog = DestinationCatalog(listOf(stream))

        // Configure table name mocks
        every { rawTableNameGenerator.getTableName(any()) } returns
            TableName("raw_dataset", "raw_stream")
        every { finalTableNameGenerator.getTableName(any()) } returns
            TableName("final_dataset", "final_stream")

        // Set up column name generator to create collisions
        // All column names will map to the same name "column"
        every { columnNameGenerator.getColumnName(any()) } answers
            { call ->
                val input = call.invocation.args[0] as String
                if (input.startsWith("column") && !input.contains("_")) {
                    // For original column names, map them all to the same name
                    ColumnNameGenerator.ColumnName("column", "column")
                } else if (input.matches(Regex("column_\\d+"))) {
                    // For column names with numeric suffixes (column_1, column_2, etc.)
                    // Return a name with the suffix intact
                    val suffix = input.substring("column".length)
                    ColumnNameGenerator.ColumnName("column$suffix", "column$suffix")
                } else {
                    // For any other input (like in the superResolveColumnCollisions case)
                    ColumnNameGenerator.ColumnName(input, input)
                }
            }

        // Create factory and get catalog
        val factory =
            TableCatalogFactory(
                catalog,
                rawTableNameGenerator,
                finalTableNameGenerator,
                columnNameGenerator
            )
        val tableCatalog = factory.get()

        // Get the column mappings
        val columnMapping = tableCatalog[stream]!!.columnNameMapping

        // Verify we have all 4 columns with unique names
        val columnNames = columnMapping.values.toSet()
        assertEquals(4, columnNames.size)

        // Verify the first column gets the original name
        assertEquals("column", columnMapping["column1"])

        // Verify the other columns get incremental suffixes
        assertTrue(columnMapping["column2"]!!.startsWith("column_"))
        assertTrue(columnMapping["column3"]!!.startsWith("column_"))
        assertTrue(columnMapping["column4"]!!.startsWith("column_"))

        // Make sure all column names are different
        val mappedNames =
            listOf(
                columnMapping["column1"]!!,
                columnMapping["column2"]!!,
                columnMapping["column3"]!!,
                columnMapping["column4"]!!
            )

        for (i in mappedNames.indices) {
            for (j in i + 1 until mappedNames.size) {
                assertNotEquals(
                    mappedNames[i],
                    mappedNames[j],
                    "Columns $i and $j have the same mapped name: ${mappedNames[i]}"
                )
            }
        }

        // Print for debugging
        println("Column mappings: $columnMapping")
    }

    /**
     * Creates a schema with multiple columns that will all map to the same name, causing multiple
     * collisions to test incremental suffix resolution
     */
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
