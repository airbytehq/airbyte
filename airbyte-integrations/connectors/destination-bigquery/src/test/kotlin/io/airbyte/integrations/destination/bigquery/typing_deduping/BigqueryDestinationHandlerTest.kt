/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping

import com.google.cloud.bigquery.Clustering
import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.cloud.bigquery.StandardTableDefinition
import com.google.cloud.bigquery.TimePartitioning
import com.google.common.collect.ImmutableList
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.base.destination.typing_deduping.Union
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler.Companion.clusteringMatches
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler.Companion.partitioningMatches
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler.Companion.schemaContainAllFinalTableV2AirbyteColumns
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator.Companion.toDialectType
import java.util.Optional
import java.util.stream.Collectors
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito

class BigqueryDestinationHandlerTest {
    @Test
    fun testToDialectType() {
        val s = Struct(LinkedHashMap())
        val a = Array(AirbyteProtocolType.BOOLEAN)

        Assertions.assertEquals(
            StandardSQLTypeName.INT64,
            toDialectType((AirbyteProtocolType.INTEGER as AirbyteType))
        )
        Assertions.assertEquals(StandardSQLTypeName.JSON, toDialectType(s))
        Assertions.assertEquals(StandardSQLTypeName.JSON, toDialectType(a))
        Assertions.assertEquals(
            StandardSQLTypeName.JSON,
            toDialectType(UnsupportedOneOf(ArrayList()))
        )

        var u = Union(ImmutableList.of(s))
        Assertions.assertEquals(StandardSQLTypeName.JSON, toDialectType(u))
        u = Union(ImmutableList.of(a))
        Assertions.assertEquals(StandardSQLTypeName.JSON, toDialectType(u))
        u = Union(ImmutableList.of(AirbyteProtocolType.BOOLEAN, AirbyteProtocolType.NUMBER))
        Assertions.assertEquals(StandardSQLTypeName.NUMERIC, toDialectType(u))
    }

    @Test
    fun testClusteringMatches() {
        var stream =
            StreamConfig(
                Mockito.mock(),
                ImportType.DEDUPE,
                listOf(ColumnId("foo", "bar", "fizz")),
                Optional.empty(),
                LinkedHashMap(),
                0,
                0,
                0
            )

        // Clustering is null
        val existingTable = Mockito.mock(StandardTableDefinition::class.java)
        Mockito.`when`(existingTable.clustering).thenReturn(null)
        Assertions.assertFalse(clusteringMatches(stream, existingTable))

        // Clustering does not contain all fields
        Mockito.`when`(existingTable.clustering)
            .thenReturn(Clustering.newBuilder().setFields(listOf("_airbyte_extracted_at")).build())
        Assertions.assertFalse(clusteringMatches(stream, existingTable))

        // Clustering matches
        stream =
            StreamConfig(
                Mockito.mock(),
                ImportType.APPEND,
                emptyList(),
                Optional.empty(),
                LinkedHashMap(),
                0,
                0,
                0
            )
        Assertions.assertTrue(clusteringMatches(stream, existingTable))

        // Clustering only the first 3 PK columns (See
        // https://github.com/airbytehq/oncall/issues/2565)
        val expectedStreamColumnNames = listOf("a", "b", "c")
        Mockito.`when`(existingTable.clustering)
            .thenReturn(
                Clustering.newBuilder()
                    .setFields(
                        Stream.concat(
                                expectedStreamColumnNames.stream(),
                                Stream.of("_airbyte_extracted_at")
                            )
                            .collect(Collectors.toList())
                    )
                    .build()
            )
        stream =
            StreamConfig(
                Mockito.mock(),
                ImportType.DEDUPE,
                Stream.concat(expectedStreamColumnNames.stream(), Stream.of("d", "e"))
                    .map { name: String -> ColumnId(name, "foo", "bar") }
                    .collect(Collectors.toList()),
                Optional.empty(),
                LinkedHashMap(),
                0,
                0,
                0
            )
        Assertions.assertTrue(clusteringMatches(stream, existingTable))
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

    @Test
    fun testSchemaContainAllFinalTableV2AirbyteColumns() {
        Assertions.assertTrue(
            schemaContainAllFinalTableV2AirbyteColumns(
                setOf(
                    "_airbyte_meta",
                    "_airbyte_generation_id",
                    "_airbyte_extracted_at",
                    "_airbyte_raw_id"
                )
            )
        )
        Assertions.assertFalse(
            schemaContainAllFinalTableV2AirbyteColumns(
                setOf("_airbyte_extracted_at", "_airbyte_raw_id")
            )
        )
        Assertions.assertFalse(
            schemaContainAllFinalTableV2AirbyteColumns(setOf("_airbyte_meta", "_airbyte_raw_id"))
        )
        Assertions.assertFalse(
            schemaContainAllFinalTableV2AirbyteColumns(
                setOf("_airbyte_meta", "_airbyte_extracted_at")
            )
        )
        Assertions.assertFalse(schemaContainAllFinalTableV2AirbyteColumns(setOf()))
        Assertions.assertTrue(
            schemaContainAllFinalTableV2AirbyteColumns(
                setOf(
                    "_AIRBYTE_META",
                    "_AIRBYTE_GENERATION_ID",
                    "_AIRBYTE_EXTRACTED_AT",
                    "_AIRBYTE_RAW_ID"
                )
            )
        )
    }
}
