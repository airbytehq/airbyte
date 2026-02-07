/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping.direct_load_tables

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
import io.airbyte.cdk.load.orchestration.db.direct_load_table.ColumnAdd
import io.airbyte.cdk.load.orchestration.db.direct_load_table.ColumnChange
import io.airbyte.integrations.destination.bigquery.spec.BatchedStandardInsertConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryRegion
import io.airbyte.integrations.destination.bigquery.spec.CdcDeletionMode
import io.airbyte.integrations.destination.bigquery.spec.PartitioningGranularity
import io.airbyte.integrations.destination.bigquery.stream.StreamConfigProvider
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadNativeTableOperations
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadNativeTableOperations.Companion.clusteringMatches
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadNativeTableOperations.Companion.partitioningMatches
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadSqlGenerator.Companion.toDialectType
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.Mockito.RETURNS_DEEP_STUBS
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever

class BigqueryDirectLoadNativeTableOperationsTest {
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
        val streamConfigProvider = mock<StreamConfigProvider>()
        whenever(streamConfigProvider.getPartitioningField(any())).thenReturn(null)
        val alterTableReport =
            BigqueryDirectLoadNativeTableOperations(
                    Mockito.mock(),
                    Mockito.mock(),
                    Mockito.mock(),
                    projectId = "unused",
                    tempTableNameGenerator = DefaultTempTableNameGenerator("unused"),
                    streamConfigProvider = streamConfigProvider
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
        val streamConfigProvider = mock<StreamConfigProvider>()
        whenever(streamConfigProvider.getPartitioningField(any())).thenReturn(null)
        val alterTableReport =
            BigqueryDirectLoadNativeTableOperations(
                    Mockito.mock(),
                    Mockito.mock(),
                    Mockito.mock(),
                    projectId = "unused",
                    tempTableNameGenerator = DefaultTempTableNameGenerator("unused"),
                    streamConfigProvider = streamConfigProvider
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

        val streamConfigProvider = mock<StreamConfigProvider>()
        whenever(streamConfigProvider.getClusteringField(any())).thenReturn(null)

        // Clustering is null
        val existingTable = Mockito.mock(StandardTableDefinition::class.java)
        Mockito.`when`(existingTable.clustering).thenReturn(null)
        Assertions.assertFalse(
            clusteringMatches(stream, columnNameMapping, existingTable, streamConfigProvider)
        )

        // Clustering does not contain all fields
        Mockito.`when`(existingTable.clustering)
            .thenReturn(Clustering.newBuilder().setFields(listOf("_airbyte_extracted_at")).build())
        Assertions.assertFalse(
            clusteringMatches(stream, columnNameMapping, existingTable, streamConfigProvider)
        )

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
        Assertions.assertTrue(
            clusteringMatches(stream, columnNameMapping, existingTable, streamConfigProvider)
        )

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
        Assertions.assertTrue(
            clusteringMatches(stream, columnNameMapping, existingTable, streamConfigProvider)
        )
    }

    @Test
    fun testPartitioningMatches() {
        val existingTable = Mockito.mock(StandardTableDefinition::class.java)
        val stream =
            DestinationStream(
                "foo",
                "bar",
                Append,
                ObjectType(linkedMapOf()),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 0,
                namespaceMapper = NamespaceMapper()
            )
        val columnNameMapping = ColumnNameMapping(mapOf())
        val streamConfigProvider =
            StreamConfigProvider(
                BigqueryConfiguration(
                    projectId = "unused",
                    datasetLocation = BigqueryRegion.US,
                    datasetId = "unused_dataset",
                    loadingMethod = BatchedStandardInsertConfiguration,
                    credentialsJson = null,
                    cdcDeletionMode = CdcDeletionMode.HARD_DELETE,
                    internalTableDataset = "unused_internal",
                    legacyRawTablesOnly = false,
                    defaultPartitioningField = null,
                    defaultClusteringField = null,
                    defaultTableSuffix = null,
                    defaultPartitioningGranularity = PartitioningGranularity.DAY,
                    streamConfigMap = emptyMap(),
                )
            )

        // Partitioning is null
        Mockito.`when`(existingTable.timePartitioning).thenReturn(null)
        Assertions.assertFalse(
            partitioningMatches(stream, columnNameMapping, existingTable, streamConfigProvider)
        )
        // incorrect field
        Mockito.`when`(existingTable.timePartitioning)
            .thenReturn(
                TimePartitioning.newBuilder(TimePartitioning.Type.DAY).setField("_foo").build()
            )
        Assertions.assertFalse(
            partitioningMatches(stream, columnNameMapping, existingTable, streamConfigProvider)
        )
        // incorrect partitioning scheme
        Mockito.`when`(existingTable.timePartitioning)
            .thenReturn(
                TimePartitioning.newBuilder(TimePartitioning.Type.YEAR)
                    .setField("_airbyte_extracted_at")
                    .build()
            )
        Assertions.assertFalse(
            partitioningMatches(stream, columnNameMapping, existingTable, streamConfigProvider)
        )

        // partitioning matches
        Mockito.`when`(existingTable.timePartitioning)
            .thenReturn(
                TimePartitioning.newBuilder(TimePartitioning.Type.DAY)
                    .setField("_airbyte_extracted_at")
                    .build()
            )
        Assertions.assertTrue(
            partitioningMatches(stream, columnNameMapping, existingTable, streamConfigProvider)
        )
    }
}
