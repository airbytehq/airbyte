/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.load.db.orchestration

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.RawTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogFactory
import org.junit.jupiter.api.Assertions.assertAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

class TableCatalogFactoryTest {
    @Test
    fun testTableNameCollision() {
        // Create the same streams as in the original test - "foobarfoo" and "foofoo"
        val stream1 = createTestStream("foobarfoo", "a")
        val stream2 = createTestStream("foofoo", "a")

        // Use SAM syntax with conditional logic in the lambda
        val rawTableNameGenerator = RawTableNameGenerator { descriptor ->
            TableName(
                "airbyte_internal",
                """${descriptor.namespace}_${descriptor.name.replace("bar", "")}""",
            )
        }

        val finalTableNameGenerator = FinalTableNameGenerator { descriptor ->
            TableName(
                descriptor.namespace!!,
                descriptor.name.replace("bar", ""),
            )
        }

        val columnNameGenerator = ColumnNameGenerator { input ->
            ColumnNameGenerator.ColumnName(input, input)
        }

        val catalog = DestinationCatalog(listOf(stream1, stream2))

        val tableCatalog =
            TableCatalogFactory()
                .getTableCatalog(
                    catalog,
                    rawTableNameGenerator,
                    finalTableNameGenerator,
                    columnNameGenerator
                )

        // Get the final table names for both streams
        val stream1TableInfo = tableCatalog[stream1]!!
        val stream2TableInfo = tableCatalog[stream2]!!

        assertAll(
            { assertEquals("foofoo", stream1TableInfo.tableNames.finalTableName!!.name) },
            { assertEquals("a", stream1TableInfo.tableNames.finalTableName!!.namespace) },
            { assertEquals("foofoo_3fd", stream2TableInfo.tableNames.finalTableName!!.name) },
            {
                assertEquals(
                    "a",
                    stream2TableInfo.tableNames.finalTableName!!.namespace,
                )
            }
        )

        // Now check raw table names with exact expected suffix
        assertAll(
            { assertEquals("a_foofoo", stream1TableInfo.tableNames.rawTableName!!.name) },
            {
                assertEquals(
                    DEFAULT_AIRBYTE_INTERNAL_NAMESPACE,
                    stream1TableInfo.tableNames.rawTableName!!.namespace
                )
            },
            { assertEquals("a_foofoo_3fd", stream2TableInfo.tableNames.rawTableName!!.name) },
            {
                assertEquals(
                    DEFAULT_AIRBYTE_INTERNAL_NAMESPACE,
                    stream2TableInfo.tableNames.rawTableName!!.namespace
                )
            }
        )
    }

    /**
     * Test two streams which don't collide in their final tables, and with no raw tables.
     *
     * We should leave both streams unchanged.
     */
    @Test
    fun testTableNameNoCollisionWithNoRawTableGenerator() {
        val stream1 = createTestStream("foo", "a")
        val stream2 = createTestStream("bar", "a")

        val finalTableNameGenerator = FinalTableNameGenerator { descriptor ->
            TableName(descriptor.namespace!!, descriptor.name)
        }

        val columnNameGenerator = ColumnNameGenerator { input ->
            ColumnNameGenerator.ColumnName(input, input)
        }

        val catalog = DestinationCatalog(listOf(stream1, stream2))

        val tableCatalog =
            TableCatalogFactory()
                .getTableCatalog(
                    catalog,
                    rawTableNameGenerator = null,
                    finalTableNameGenerator,
                    columnNameGenerator
                )

        // Get the final table names for both streams
        val stream1TableInfo = tableCatalog[stream1]!!
        val stream2TableInfo = tableCatalog[stream2]!!

        assertAll(
            { assertEquals("foo", stream1TableInfo.tableNames.finalTableName!!.name) },
            { assertEquals("a", stream1TableInfo.tableNames.finalTableName!!.namespace) },
            { assertEquals("bar", stream2TableInfo.tableNames.finalTableName!!.name) },
            {
                assertEquals(
                    "a",
                    stream2TableInfo.tableNames.finalTableName!!.namespace,
                )
            }
        )

        // Now check raw table names are null
        assertAll(
            { assertNull(stream1TableInfo.tableNames.rawTableName) },
            { assertNull(stream2TableInfo.tableNames.rawTableName) },
        )
    }

    @Test
    fun testTruncatingColumnNameCollision() {
        val schema =
            ObjectType(
                linkedMapOf(
                    "aVeryLongColumnName" to FieldType(StringType, true),
                    "aVeryLongColumnNameWithMoreTextAfterward" to FieldType(StringType, true),
                )
            )
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

        val tableCatalog =
            TableCatalogFactory()
                .getTableCatalog(
                    catalog,
                    rawTableNameGenerator,
                    finalTableNameGenerator,
                    columnNameGenerator
                )

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

    @Test
    fun testColumnNameCollision() {
        // Create a schema with columns that will have name collision after processing
        val schema =
            ObjectType(
                linkedMapOf(
                    "foobarfoo" to FieldType(StringType, true),
                    "foofoo" to FieldType(StringType, true),
                )
            )

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

        val tableCatalog =
            TableCatalogFactory()
                .getTableCatalog(
                    catalog,
                    rawTableNameGenerator,
                    finalTableNameGenerator,
                    columnNameGenerator
                )

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

    @Test
    fun testColumnNameCollisionRelyingOnCanonicalName() {
        val schema =
            ObjectType(
                linkedMapOf(
                    "FOO" to FieldType(StringType, true),
                    "foo" to FieldType(StringType, true),
                )
            )
        val stream = createTestStream("stream", "namespace", schema)
        val catalog = DestinationCatalog(listOf(stream))
        val rawTableNameGenerator = RawTableNameGenerator { _ ->
            TableName("raw_dataset", "raw_stream")
        }
        val finalTableNameGenerator = FinalTableNameGenerator { _ ->
            TableName("final_dataset", "final_stream")
        }

        // Simulate name collision by downcasing, while retaining the original name
        // as the display name
        val columnNameGenerator = ColumnNameGenerator { input ->
            ColumnNameGenerator.ColumnName(
                displayName = input,
                canonicalName = input.lowercase(),
            )
        }

        val tableCatalog =
            TableCatalogFactory()
                .getTableCatalog(
                    catalog,
                    rawTableNameGenerator,
                    finalTableNameGenerator,
                    columnNameGenerator,
                )

        val columnMapping = tableCatalog[stream]!!.columnNameMapping

        assertEquals(
            mapOf(
                "FOO" to "FOO",
                "foo" to "foo_1",
            ),
            columnMapping,
        )
    }

    private fun createTestStream(
        name: String,
        namespace: String,
        schema: AirbyteType = ObjectType(linkedMapOf())
    ): DestinationStream {
        return DestinationStream(
            unmappedNamespace = namespace,
            unmappedName = name,
            importType = Append,
            schema = schema,
            generationId = 1L,
            minimumGenerationId = 0L,
            syncId = 0L,
            namespaceMapper = NamespaceMapper()
        )
    }
}
