/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.load.db.orchestration

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
import org.junit.jupiter.api.Assertions.assertAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class TableCatalogFactoryTest {
    @Test
    fun testTableNameCollision() {
        // Create the same streams as in the original test - "foobarfoo" and "foofoo"
        val stream1 = createTestStream("foobarfoo", "a")
        val stream2 = createTestStream("foofoo", "a")

        // Use SAM syntax with conditional logic in the lambda
        val rawTableNameGenerator = RawTableNameGenerator { descriptor ->
            // Check if this is a generated name with the hash suffix (for collision resolution)
            if (descriptor.name.contains("_3fd")) {
                TableName("airbyte_internal", "a_foofoo_3fd")
            } else {
                // Otherwise always return the same value to force collision
                TableName("airbyte_internal", "a_foofoo")
            }
        }

        val finalTableNameGenerator = FinalTableNameGenerator { descriptor ->
            // Check if this is a generated name with the hash suffix (for collision resolution)
            if (descriptor.name.contains("_3fd")) {
                TableName("a", "foofoo_3fd")
            } else {
                // Otherwise always return the same value to force collision
                TableName("a", "foofoo")
            }
        }

        val columnNameGenerator = ColumnNameGenerator { input ->
            ColumnNameGenerator.ColumnName(input, input)
        }

        val catalog = DestinationCatalog(listOf(stream1, stream2))

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

        assertAll(
            { assertTrue(stream1TableInfo.tableNames.finalTableName!!.name == "foofoo") },
            { assertTrue(stream1TableInfo.tableNames.finalTableName!!.namespace == "a") },
            { assertTrue(stream2TableInfo.tableNames.finalTableName!!.name == "foofoo_3fd") },
            { assertTrue(stream2TableInfo.tableNames.finalTableName!!.namespace == "a") }
        )

        // Now check raw table names with exact expected suffix
        assertAll(
            { assertTrue(stream1TableInfo.tableNames.rawTableName!!.name == "a_foofoo") },
            {
                assertTrue(
                    stream1TableInfo.tableNames.rawTableName!!.namespace ==
                        DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
                )
            },
            { assertTrue(stream2TableInfo.tableNames.rawTableName!!.name == "a_foofoo_3fd") },
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
        val schema = createSchemaWithLongColumnNames()
        val stream = createTestStream("stream", "namespace", schema)
        val catalog = DestinationCatalog(listOf(stream))

        val rawTableNameGenerator = RawTableNameGenerator { _ ->
            TableName("raw_dataset", "raw_stream")
        }

        val finalTableNameGenerator = FinalTableNameGenerator { _ ->
            TableName("final_dataset", "final_stream")
        }

        val columnNameGenerator = ColumnNameGenerator { input ->
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
        // Create a schema with columns that will have name collision after processing
        val schemaProperties = linkedMapOf<String, FieldType>()
        schemaProperties["foobarfoo"] = FieldType(io.airbyte.cdk.load.data.StringType, true)
        schemaProperties["foofoo"] = FieldType(io.airbyte.cdk.load.data.StringType, true)
        val schema = ObjectType(schemaProperties)

        val stream = createTestStream("stream", "namespace", schema)
        val catalog = DestinationCatalog(listOf(stream))

        val rawTableNameGenerator = RawTableNameGenerator { _ ->
            TableName("raw_dataset", "raw_stream")
        }

        val finalTableNameGenerator = FinalTableNameGenerator { _ ->
            TableName("final_dataset", "final_stream")
        }

        // Simulate name collision by removing "bar"
        val columnNameGenerator = ColumnNameGenerator { input ->
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
