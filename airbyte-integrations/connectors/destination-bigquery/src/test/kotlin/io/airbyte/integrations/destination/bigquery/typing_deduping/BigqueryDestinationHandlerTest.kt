/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping

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
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator.Companion.toDialectType
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigqueryDatabaseInitialStatusGatherer.Companion.clusteringMatches
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigqueryDatabaseInitialStatusGatherer.Companion.partitioningMatches
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.Mockito.RETURNS_DEEP_STUBS

class BigqueryDestinationHandlerTest {
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
            BigqueryDatabaseInitialStatusGatherer(Mockito.mock())
                .buildAlterTableReport(stream, columnNameMapping, existingTable)
        Assertions.assertAll(
            { Assertions.assertEquals(emptySet<String>(), alterTableReport.columnsToAdd) },
            { Assertions.assertEquals(emptySet<String>(), alterTableReport.columnsToRemove) },
            { Assertions.assertEquals(emptySet<String>(), alterTableReport.columnsToChangeType) },
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
            BigqueryDatabaseInitialStatusGatherer(Mockito.mock())
                .buildAlterTableReport(stream, columnNameMapping, existingTable)
        Assertions.assertAll(
            { Assertions.assertEquals(setOf("c2"), alterTableReport.columnsToAdd) },
            { Assertions.assertEquals(setOf("b2"), alterTableReport.columnsToRemove) },
            { Assertions.assertEquals(setOf("a2"), alterTableReport.columnsToChangeType) },
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
                ObjectTypeWithoutSchema,
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
                ObjectTypeWithoutSchema,
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
}
