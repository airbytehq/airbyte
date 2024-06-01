/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;

import com.google.cloud.bigquery.Clustering;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TimePartitioning;
import com.google.common.collect.ImmutableList;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class BigqueryDestinationHandlerTest {

  @Test
  public void testToDialectType() {
    final Struct s = new Struct(new LinkedHashMap<>());
    final Array a = new Array(AirbyteProtocolType.BOOLEAN);

    assertEquals(StandardSQLTypeName.INT64, BigQuerySqlGenerator.toDialectType((AirbyteType) AirbyteProtocolType.INTEGER));
    assertEquals(StandardSQLTypeName.JSON, BigQuerySqlGenerator.toDialectType(s));
    assertEquals(StandardSQLTypeName.JSON, BigQuerySqlGenerator.toDialectType(a));
    assertEquals(StandardSQLTypeName.JSON, BigQuerySqlGenerator.toDialectType(new UnsupportedOneOf(new ArrayList<>())));

    Union u = new Union(ImmutableList.of(s));
    assertEquals(StandardSQLTypeName.JSON, BigQuerySqlGenerator.toDialectType(u));
    u = new Union(ImmutableList.of(a));
    assertEquals(StandardSQLTypeName.JSON, BigQuerySqlGenerator.toDialectType(u));
    u = new Union(ImmutableList.of(AirbyteProtocolType.BOOLEAN, AirbyteProtocolType.NUMBER));
    assertEquals(StandardSQLTypeName.NUMERIC, BigQuerySqlGenerator.toDialectType(u));
  }

  @Test
  public void testClusteringMatches() {
    StreamConfig stream = new StreamConfig(mock(),
        DestinationSyncMode.APPEND_DEDUP,
        List.of(new ColumnId("foo", "bar", "fizz")),
        Optional.empty(),
        new LinkedHashMap<>(), 0, 0, 0);

    // Clustering is null
    final StandardTableDefinition existingTable = mock(StandardTableDefinition.class);
    Mockito.when(existingTable.getClustering()).thenReturn(null);
    Assertions.assertFalse(BigQueryDestinationHandler.clusteringMatches(stream, existingTable));

    // Clustering does not contain all fields
    Mockito.when(existingTable.getClustering())
        .thenReturn(Clustering.newBuilder().setFields(List.of("_airbyte_extracted_at")).build());
    Assertions.assertFalse(BigQueryDestinationHandler.clusteringMatches(stream, existingTable));

    // Clustering matches
    stream = new StreamConfig(mock(),
        DestinationSyncMode.OVERWRITE,
        Collections.emptyList(),
        Optional.empty(),
        new LinkedHashMap<>(), 0, 0, 0);
    Assertions.assertTrue(BigQueryDestinationHandler.clusteringMatches(stream, existingTable));

    // Clustering only the first 3 PK columns (See https://github.com/airbytehq/oncall/issues/2565)
    final var expectedStreamColumnNames = List.of("a", "b", "c");
    Mockito.when(existingTable.getClustering())
        .thenReturn(Clustering.newBuilder().setFields(
            Stream.concat(expectedStreamColumnNames.stream(), Stream.of("_airbyte_extracted_at"))
                .collect(Collectors.toList()))
            .build());
    stream = new StreamConfig(mock(),
        DestinationSyncMode.APPEND_DEDUP,
        Stream.concat(expectedStreamColumnNames.stream(), Stream.of("d", "e"))
            .map(name -> new ColumnId(name, "foo", "bar"))
            .collect(Collectors.toList()),
        Optional.empty(),
        new LinkedHashMap<>(), 0, 0, 0);
    Assertions.assertTrue(BigQueryDestinationHandler.clusteringMatches(stream, existingTable));
  }

  @Test
  public void testPartitioningMatches() {
    final StandardTableDefinition existingTable = mock(StandardTableDefinition.class);
    // Partitioning is null
    Mockito.when(existingTable.getTimePartitioning()).thenReturn(null);
    Assertions.assertFalse(BigQueryDestinationHandler.partitioningMatches(existingTable));
    // incorrect field
    Mockito.when(existingTable.getTimePartitioning())
        .thenReturn(TimePartitioning.newBuilder(TimePartitioning.Type.DAY).setField("_foo").build());
    Assertions.assertFalse(BigQueryDestinationHandler.partitioningMatches(existingTable));
    // incorrect partitioning scheme
    Mockito.when(existingTable.getTimePartitioning())
        .thenReturn(TimePartitioning.newBuilder(TimePartitioning.Type.YEAR).setField("_airbyte_extracted_at").build());
    Assertions.assertFalse(BigQueryDestinationHandler.partitioningMatches(existingTable));

    // partitioning matches
    Mockito.when(existingTable.getTimePartitioning())
        .thenReturn(TimePartitioning.newBuilder(TimePartitioning.Type.DAY).setField("_airbyte_extracted_at").build());
    Assertions.assertTrue(BigQueryDestinationHandler.partitioningMatches(existingTable));
  }

  @Test
  public void testSchemaContainAllFinalTableV2AirbyteColumns() {
    Assertions.assertTrue(
        BigQueryDestinationHandler.schemaContainAllFinalTableV2AirbyteColumns(
            Set.of("_airbyte_meta", "_airbyte_generation_id", "_airbyte_extracted_at", "_airbyte_raw_id")));
    Assertions.assertFalse(BigQueryDestinationHandler.schemaContainAllFinalTableV2AirbyteColumns(Set.of("_airbyte_extracted_at", "_airbyte_raw_id")));
    Assertions.assertFalse(BigQueryDestinationHandler.schemaContainAllFinalTableV2AirbyteColumns(Set.of("_airbyte_meta", "_airbyte_raw_id")));
    Assertions.assertFalse(BigQueryDestinationHandler.schemaContainAllFinalTableV2AirbyteColumns(Set.of("_airbyte_meta", "_airbyte_extracted_at")));
    Assertions.assertFalse(BigQueryDestinationHandler.schemaContainAllFinalTableV2AirbyteColumns(Set.of()));
    Assertions.assertTrue(
        BigQueryDestinationHandler.schemaContainAllFinalTableV2AirbyteColumns(
            Set.of("_AIRBYTE_META", "_AIRBYTE_GENERATION_ID", "_AIRBYTE_EXTRACTED_AT", "_AIRBYTE_RAW_ID")));
  }

}
