/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping.direct_load_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.Clustering
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.FieldList
import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.cloud.bigquery.StandardTableDefinition
import com.google.cloud.bigquery.TimePartitioning
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.ColumnAdd
import io.airbyte.cdk.load.orchestration.db.direct_load_table.ColumnChange
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigQueryDatabaseHandler
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadNativeTableOperations
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadNativeTableOperations.Companion.clusteringMatches
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadNativeTableOperations.Companion.partitioningMatches
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadSqlGenerator.Companion.toDialectType
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadSqlTableOperations
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.Mockito.RETURNS_DEEP_STUBS
import org.mockito.Mockito.never
import org.mockito.Mockito.verify

class BigqueryDirectLoadNativeTableOperationsTest {
    // Helper to work around Mockito.any() returning null in Kotlin
    @Suppress("UNCHECKED_CAST")
    private fun <T> anyNonNull(): T {
        Mockito.any<T>()
        return null as T
    }
    @Test
    fun testToDialectType() {
        val s = ObjectType(linkedMapOf())
        val a = ArrayType(FieldType(BooleanType, nullable = true))

        Assertions.assertEquals(StandardSQLTypeName.INT64, toDialectType(IntegerType))
        Assertions.assertEquals(StandardSQLTypeName.JSON, toDialectType(s))
        Assertions.assertEquals(StandardSQLTypeName.JSON, toDialectType(a))
        Assertions.assertEquals(
            StandardSQLTypeName.JSON,
            toDialectType(UnionType(emptySet(), isLegacyUnion = false))
        )

        var u = UnionType(setOf(s), isLegacyUnion = true)
        Assertions.assertEquals(StandardSQLTypeName.JSON, toDialectType(u))
        u = UnionType(setOf(a), isLegacyUnion = true)
        Assertions.assertEquals(StandardSQLTypeName.JSON, toDialectType(u))
        u = UnionType(setOf(BooleanType, NumberType), isLegacyUnion = true)
        Assertions.assertEquals(StandardSQLTypeName.NUMERIC, toDialectType(u))
    }

    @Test
    fun testColumnsMatch() {
        val stream =
            DestinationStream(
                "foo",
                "bar",
                Append,
                ObjectType(linkedMapOf("a1" to FieldType(IntegerType, nullable = true))),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 0,
                namespaceMapper = NamespaceMapper()
            )
        val columnNameMapping = ColumnNameMapping(mapOf("a1" to "a2"))
        val existingTable = Mockito.mock(StandardTableDefinition::class.java, RETURNS_DEEP_STUBS)
        Mockito.`when`(existingTable.schema!!.fields)
            .thenReturn(FieldList.of(Field.of("a2", StandardSQLTypeName.INT64)))
        val alterTableReport =
            BigqueryDirectLoadNativeTableOperations(
                    Mockito.mock(),
                    Mockito.mock(),
                    Mockito.mock(),
                    projectId = "unused",
                    tempTableNameGenerator = DefaultTempTableNameGenerator("unused"),
                )
                .buildAlterTableReport(stream, columnNameMapping, existingTable)
        Assertions.assertAll(
            {
                Assertions.assertEquals(
                    emptyList<Pair<String, StandardSQLTypeName>>(),
                    alterTableReport.columnsToAdd
                )
            },
            { Assertions.assertEquals(emptyList<String>(), alterTableReport.columnsToRemove) },
            {
                Assertions.assertEquals(
                    emptyList<ColumnChange<StandardSQLTypeName>>(),
                    alterTableReport.columnsToChangeType
                )
            },
            // NB: column names in AlterTableReport are all _after_ destination name transform
            { Assertions.assertEquals(listOf("a2"), alterTableReport.columnsToRetain) },
        )
    }

    @Test
    fun testColumnsNotMatch() {
        val stream =
            DestinationStream(
                "foo",
                "bar",
                Append,
                ObjectType(
                    linkedMapOf(
                        "a1" to FieldType(IntegerType, nullable = true),
                        "c1" to FieldType(IntegerType, nullable = true),
                    )
                ),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 0,
                namespaceMapper = NamespaceMapper()
            )
        val columnNameMapping = ColumnNameMapping(mapOf("a1" to "a2", "c1" to "c2"))
        val existingTable = Mockito.mock(StandardTableDefinition::class.java, RETURNS_DEEP_STUBS)
        Mockito.`when`(existingTable.schema!!.fields)
            .thenReturn(
                FieldList.of(
                    listOf(
                        Field.of("a2", StandardSQLTypeName.STRING),
                        Field.of("b2", StandardSQLTypeName.INT64)
                    )
                )
            )
        val alterTableReport =
            BigqueryDirectLoadNativeTableOperations(
                    Mockito.mock(),
                    Mockito.mock(),
                    Mockito.mock(),
                    projectId = "unused",
                    tempTableNameGenerator = DefaultTempTableNameGenerator("unused"),
                )
                .buildAlterTableReport(stream, columnNameMapping, existingTable)
        // NB: column names in AlterTableReport are all _after_ destination name transform
        Assertions.assertAll(
            {
                Assertions.assertEquals(
                    listOf(ColumnAdd("c2", StandardSQLTypeName.INT64)),
                    alterTableReport.columnsToAdd
                )
            },
            { Assertions.assertEquals(listOf("b2"), alterTableReport.columnsToRemove) },
            {
                Assertions.assertEquals(
                    listOf(
                        ColumnChange(
                            name = "a2",
                            originalType = StandardSQLTypeName.STRING,
                            newType = StandardSQLTypeName.INT64,
                        )
                    ),
                    alterTableReport.columnsToChangeType,
                )
            },
            {
                Assertions.assertEquals(
                    emptyList<ColumnChange<StandardSQLTypeName>>(),
                    alterTableReport.columnsToRetain
                )
            }
        )
    }

    @Test
    fun testClusteringMatches() {
        var stream =
            DestinationStream(
                "foo",
                "bar",
                Dedupe(
                    listOf(listOf("bar")),
                    emptyList(),
                ),
                ObjectType(linkedMapOf("bar" to FieldType(IntegerType, nullable = true))),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 0,
                namespaceMapper = NamespaceMapper()
            )
        var columnNameMapping = ColumnNameMapping(mapOf("bar" to "foo"))

        // Clustering is null
        val existingTable = Mockito.mock(StandardTableDefinition::class.java)
        Mockito.`when`(existingTable.clustering).thenReturn(null)
        Assertions.assertFalse(clusteringMatches(stream, columnNameMapping, existingTable))

        // Clustering does not contain all fields
        Mockito.`when`(existingTable.clustering)
            .thenReturn(Clustering.newBuilder().setFields(listOf("_airbyte_extracted_at")).build())
        Assertions.assertFalse(clusteringMatches(stream, columnNameMapping, existingTable))

        // Clustering matches
        stream =
            DestinationStream(
                "foo",
                "bar",
                Append,
                ObjectTypeWithoutSchema,
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 0,
                namespaceMapper = NamespaceMapper()
            )
        Assertions.assertTrue(clusteringMatches(stream, columnNameMapping, existingTable))

        // Clustering only the first 3 PK columns (See
        // https://github.com/airbytehq/oncall/issues/2565)
        Mockito.`when`(existingTable.clustering)
            .thenReturn(
                Clustering.newBuilder()
                    .setFields(listOf("a2", "b2", "c2", "_airbyte_extracted_at"))
                    .build()
            )
        stream =
            DestinationStream(
                "foo",
                "bar",
                Dedupe(
                    listOf(listOf("a1"), listOf("b1"), listOf("c1"), listOf("d1"), listOf("e1")),
                    emptyList()
                ),
                ObjectType(
                    linkedMapOf(
                        "a1" to FieldType(IntegerType, nullable = true),
                        "b1" to FieldType(IntegerType, nullable = true),
                        "c1" to FieldType(IntegerType, nullable = true),
                        "d1" to FieldType(IntegerType, nullable = true),
                        "e1" to FieldType(IntegerType, nullable = true),
                    )
                ),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 0,
                namespaceMapper = NamespaceMapper()
            )
        columnNameMapping =
            ColumnNameMapping(
                mapOf(
                    "a1" to "a2",
                    "b1" to "b2",
                    "c1" to "c2",
                    "d1" to "d2",
                    "e1" to "e2",
                )
            )
        Assertions.assertTrue(clusteringMatches(stream, columnNameMapping, existingTable))
    }

    @Test
    fun testPartitioningMatches() {
        val existingTable = Mockito.mock(StandardTableDefinition::class.java)
        // Partitioning is null
        Mockito.`when`(existingTable.timePartitioning).thenReturn(null)
        Assertions.assertFalse(partitioningMatches(existingTable))
        // incorrect field
        Mockito.`when`(existingTable.timePartitioning)
            .thenReturn(
                TimePartitioning.newBuilder(TimePartitioning.Type.DAY).setField("_foo").build()
            )
        Assertions.assertFalse(partitioningMatches(existingTable))
        // incorrect partitioning scheme
        Mockito.`when`(existingTable.timePartitioning)
            .thenReturn(
                TimePartitioning.newBuilder(TimePartitioning.Type.YEAR)
                    .setField("_airbyte_extracted_at")
                    .build()
            )
        Assertions.assertFalse(partitioningMatches(existingTable))

        // partitioning matches
        Mockito.`when`(existingTable.timePartitioning)
            .thenReturn(
                TimePartitioning.newBuilder(TimePartitioning.Type.DAY)
                    .setField("_airbyte_extracted_at")
                    .build()
            )
        Assertions.assertTrue(partitioningMatches(existingTable))
    }

    /**
     * When the existing table has only columns that don't match the stream schema at all (no meta
     * columns, all user columns differ), buildAlterTableReport should return empty columnsToRetain
     * and empty columnsToChangeType.
     */
    @Test
    fun testBuildAlterTableReportAllColumnsRemoved() {
        // Stream expects columns "new_col1" and "new_col2"
        val stream =
            DestinationStream(
                "foo",
                "bar",
                Append,
                ObjectType(
                    linkedMapOf(
                        "new_col1" to FieldType(IntegerType, nullable = true),
                        "new_col2" to FieldType(BooleanType, nullable = true),
                    )
                ),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 0,
                namespaceMapper = NamespaceMapper()
            )
        val columnNameMapping =
            ColumnNameMapping(mapOf("new_col1" to "new_col1", "new_col2" to "new_col2"))
        val existingTable = Mockito.mock(StandardTableDefinition::class.java, RETURNS_DEEP_STUBS)
        // Existing table has only "old_col1" and "old_col2" - no overlap with expected columns
        Mockito.`when`(existingTable.schema!!.fields)
            .thenReturn(
                FieldList.of(
                    listOf(
                        Field.of("old_col1", StandardSQLTypeName.STRING),
                        Field.of("old_col2", StandardSQLTypeName.INT64)
                    )
                )
            )
        val alterTableReport =
            BigqueryDirectLoadNativeTableOperations(
                    Mockito.mock(),
                    Mockito.mock(),
                    Mockito.mock(),
                    projectId = "unused",
                    tempTableNameGenerator = DefaultTempTableNameGenerator("unused"),
                )
                .buildAlterTableReport(stream, columnNameMapping, existingTable)
        Assertions.assertAll(
            {
                Assertions.assertEquals(
                    listOf(
                        ColumnAdd("new_col1", StandardSQLTypeName.INT64),
                        ColumnAdd("new_col2", StandardSQLTypeName.BOOL),
                    ),
                    alterTableReport.columnsToAdd,
                )
            },
            {
                Assertions.assertEquals(
                    listOf("old_col1", "old_col2"),
                    alterTableReport.columnsToRemove,
                )
            },
            {
                Assertions.assertEquals(
                    emptyList<ColumnChange<StandardSQLTypeName>>(),
                    alterTableReport.columnsToChangeType,
                )
            },
            {
                Assertions.assertEquals(
                    emptyList<String>(),
                    alterTableReport.columnsToRetain,
                )
            },
        )
    }

    /**
     * When recreateTable is triggered with empty columnsToRetain and empty columnsToChange, the
     * INSERT INTO statement should be skipped to avoid generating invalid SQL with an empty column
     * list.
     */
    @Test
    fun testRecreateTableSkipsInsertWhenNoColumnsToRetain() {
        val bigquery = Mockito.mock(BigQuery::class.java, RETURNS_DEEP_STUBS)
        val sqlOperations = Mockito.mock(BigqueryDirectLoadSqlTableOperations::class.java)
        val databaseHandler = Mockito.mock(BigQueryDatabaseHandler::class.java)

        val stream =
            DestinationStream(
                "test_ns",
                "test_stream",
                Append,
                ObjectType(
                    linkedMapOf(
                        "new_col" to FieldType(IntegerType, nullable = true),
                    )
                ),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 0,
                namespaceMapper = NamespaceMapper()
            )
        val columnNameMapping = ColumnNameMapping(mapOf("new_col" to "new_col"))
        val tableName = TableName("test_ns", "test_table")

        // Mock bigquery.getTable() to return a StandardTableDefinition with:
        // - wrong partitioning (to trigger shouldRecreateTable=true)
        // - schema fields that don't overlap with the stream (to get empty columnsToRetain)
        val existingTable = Mockito.mock(StandardTableDefinition::class.java, RETURNS_DEEP_STUBS)
        // No clustering -> clusteringMatches=false -> shouldRecreateTable=true
        Mockito.`when`(existingTable.clustering).thenReturn(null)
        // Partitioning doesn't matter if clustering already fails, but set it anyway
        Mockito.`when`(existingTable.timePartitioning).thenReturn(null)
        // Existing table has only "old_col" - no overlap with expected "new_col"
        Mockito.`when`(existingTable.schema!!.fields)
            .thenReturn(FieldList.of(listOf(Field.of("old_col", StandardSQLTypeName.STRING))))

        Mockito.`when`(bigquery.getTable(Mockito.any()).getDefinition<StandardTableDefinition>())
            .thenReturn(existingTable)

        val operations =
            BigqueryDirectLoadNativeTableOperations(
                bigquery,
                sqlOperations,
                databaseHandler,
                projectId = "test_project",
                tempTableNameGenerator = DefaultTempTableNameGenerator("test_project"),
            )

        runBlocking { operations.ensureSchemaMatches(stream, tableName, columnNameMapping) }

        // Verify that databaseHandler.execute was never called (INSERT was skipped)
        verify(databaseHandler, never()).execute(anyNonNull())
    }

    /**
     * When recreateTable is triggered with non-empty columnsToRetain, the INSERT INTO statement
     * should be executed.
     */
    @Test
    fun testRecreateTableExecutesInsertWhenColumnsToRetain() {
        val bigquery = Mockito.mock(BigQuery::class.java, RETURNS_DEEP_STUBS)
        val sqlOperations = Mockito.mock(BigqueryDirectLoadSqlTableOperations::class.java)
        val databaseHandler = Mockito.mock(BigQueryDatabaseHandler::class.java)

        val stream =
            DestinationStream(
                "test_ns",
                "test_stream",
                Append,
                ObjectType(
                    linkedMapOf(
                        "existing_col" to FieldType(IntegerType, nullable = true),
                        "new_col" to FieldType(BooleanType, nullable = true),
                    )
                ),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 0,
                namespaceMapper = NamespaceMapper()
            )
        val columnNameMapping =
            ColumnNameMapping(mapOf("existing_col" to "existing_col", "new_col" to "new_col"))
        val tableName = TableName("test_ns", "test_table")

        // Mock bigquery.getTable() to return a StandardTableDefinition with:
        // - wrong partitioning (to trigger shouldRecreateTable=true)
        // - "existing_col" that overlaps with the stream (columnsToRetain is non-empty)
        val existingTable = Mockito.mock(StandardTableDefinition::class.java, RETURNS_DEEP_STUBS)
        Mockito.`when`(existingTable.clustering).thenReturn(null)
        Mockito.`when`(existingTable.timePartitioning).thenReturn(null)
        Mockito.`when`(existingTable.schema!!.fields)
            .thenReturn(FieldList.of(listOf(Field.of("existing_col", StandardSQLTypeName.INT64))))

        Mockito.`when`(bigquery.getTable(Mockito.any()).getDefinition<StandardTableDefinition>())
            .thenReturn(existingTable)

        val operations =
            BigqueryDirectLoadNativeTableOperations(
                bigquery,
                sqlOperations,
                databaseHandler,
                projectId = "test_project",
                tempTableNameGenerator = DefaultTempTableNameGenerator("test_project"),
            )

        runBlocking { operations.ensureSchemaMatches(stream, tableName, columnNameMapping) }

        // Verify that databaseHandler.execute was called (INSERT was executed)
        verify(databaseHandler).execute(anyNonNull())
    }
}
