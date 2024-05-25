/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.redshift.RedshiftSQLNameTransformer;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSuperLimitationTransformer.TransformationInfo;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.IntStream;
import kotlin.Pair;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class RedshiftSuperLimitationTransformerTest {

  private RedshiftSuperLimitationTransformer transformer;
  private static final RedshiftSqlGenerator redshiftSqlGenerator = new RedshiftSqlGenerator(new RedshiftSQLNameTransformer(), false);

  @BeforeEach
  public void setup() {
    final ColumnId column1 = redshiftSqlGenerator.buildColumnId("column1");
    final ColumnId column2 = redshiftSqlGenerator.buildColumnId("column2");
    final List<ColumnId> primaryKey = List.of(column1, column2);
    final LinkedHashMap<ColumnId, AirbyteType> columns = new LinkedHashMap<>();
    // Generate columnIds from 3 to 1024 and add to columns map
    IntStream.range(3, 1025).forEach(i -> columns.put(redshiftSqlGenerator.buildColumnId("column" + i), AirbyteProtocolType.STRING));

    final StreamId streamId = new StreamId("test_schema", "users_final", "test_schema", "users_raw", "test_schema", "users_final");
    StreamConfig streamConfig = new StreamConfig(
        streamId,
        DestinationSyncMode.APPEND_DEDUP,
        primaryKey,
        Optional.empty(),
        columns, 0, 0, 0);
    final ParsedCatalog parsedCatalog = new ParsedCatalog(List.of(streamConfig));
    transformer = new RedshiftSuperLimitationTransformer(parsedCatalog, "test_schema");
  }

  @Test
  public void testVarcharNulling() throws IOException {
    final String jsonString = MoreResources.readResource("test.json");
    final JsonNode jsonNode = Jsons.deserializeExact(jsonString);
    // Calculate the size of the json before transformation, note that the original JsonNode is altered
    // so
    // serializing after transformation will return modified size.
    final int jacksonDeserializationSize = Jsons.serialize(jsonNode).getBytes(StandardCharsets.UTF_8).length;
    // Add a short length as predicate.
    final TransformationInfo transformationInfo =
        transformer.transformNodes(jsonNode, text -> text.length() > 10);
    // Calculate the size of the json after transformation
    final int jacksonDeserializeSizeAfterTransform = Jsons.serialize(jsonNode).getBytes(StandardCharsets.UTF_8).length;
    assertEquals(jacksonDeserializationSize, transformationInfo.originalBytes());
    assertEquals(jacksonDeserializeSizeAfterTransform, transformationInfo.originalBytes() - transformationInfo.removedBytes());
    System.out.println(transformationInfo.meta());
    System.out.println(Jsons.serialize(jsonNode));
  }

  @Test
  public void testRedshiftSuperLimit_ShouldRemovePartialRecord() throws IOException {
    // We generate 1020 16Kb strings and 1 64Kb string + 2 uuids.
    // Removing the 64kb will make it fall below the 16MB limit & offending varchar removed too.
    final Map<String, String> testData = new HashMap<>();
    testData.put("column1", UUID.randomUUID().toString());
    testData.put("column2", UUID.randomUUID().toString());
    testData.put("column3", getLargeString(64));
    // Add 16Kb strings from column 3 to 1024 in testData
    IntStream.range(4, 1025).forEach(i -> testData.put("column" + i, getLargeString(16)));

    AirbyteRecordMessageMeta upstreamMeta = new AirbyteRecordMessageMeta()
        .withChanges(List.of(
            new AirbyteRecordMessageMetaChange()
                .withField("upstream_field")
                .withChange(Change.NULLED)
                .withReason(Reason.PLATFORM_SERIALIZATION_ERROR)));
    final Pair<JsonNode, AirbyteRecordMessageMeta> transformed =
        transformer.transform(new StreamDescriptor().withNamespace("test_schema").withName("users_final"), Jsons.jsonNode(testData), upstreamMeta);
    assertTrue(
        Jsons.serialize(transformed.getFirst())
            .getBytes(StandardCharsets.UTF_8).length < RedshiftSuperLimitationTransformer.REDSHIFT_SUPER_MAX_BYTE_SIZE);
    assertEquals(2, transformed.getSecond().getChanges().size());
    // Assert that transformation added the change
    assertEquals("$.column3", transformed.getSecond().getChanges().getFirst().getField());
    assertEquals(Change.NULLED, transformed.getSecond().getChanges().getFirst().getChange());
    assertEquals(Reason.DESTINATION_FIELD_SIZE_LIMITATION, transformed.getSecond().getChanges().getFirst().getReason());
    // Assert that upstream changes are preserved (appended last)
    assertEquals("upstream_field", transformed.getSecond().getChanges().getLast().getField());
  }

  @Test
  public void testRedshiftSuperLimit_ShouldRemoveWholeRecord() {
    final Map<String, String> testData = new HashMap<>();
    // Add 16Kb strings from column 1 to 1024 in testData where total > 16MB
    IntStream.range(1, 1025).forEach(i -> testData.put("column" + i, getLargeString(16)));

    AirbyteRecordMessageMeta upstreamMeta = new AirbyteRecordMessageMeta()
        .withChanges(List.of(
            new AirbyteRecordMessageMetaChange()
                .withField("upstream_field")
                .withChange(Change.NULLED)
                .withReason(Reason.PLATFORM_SERIALIZATION_ERROR)));
    final Pair<JsonNode, AirbyteRecordMessageMeta> transformed =
        transformer.transform(new StreamDescriptor().withNamespace("test_schema").withName("users_final"), Jsons.jsonNode(testData), upstreamMeta);
    // Verify PKs are preserved.
    assertNotNull(transformed.getFirst().get("column1"));
    assertNotNull(transformed.getFirst().get("column1"));
    assertTrue(
        Jsons.serialize(transformed.getSecond())
            .getBytes(StandardCharsets.UTF_8).length < RedshiftSuperLimitationTransformer.REDSHIFT_SUPER_MAX_BYTE_SIZE);
    assertEquals(2, transformed.getSecond().getChanges().size());
    // Assert that transformation added the change
    assertEquals("all", transformed.getSecond().getChanges().getFirst().getField());
    assertEquals(Change.NULLED, transformed.getSecond().getChanges().getFirst().getChange());
    assertEquals(Reason.DESTINATION_RECORD_SIZE_LIMITATION, transformed.getSecond().getChanges().getFirst().getReason());
    // Assert that upstream changes are preserved (appended last)
    assertEquals("upstream_field", transformed.getSecond().getChanges().getLast().getField());
  }

  @Test
  public void testRedshiftSuperLimit_ShouldFailOnPKMissing() {
    final Map<String, String> testData = new HashMap<>();
    // Add 16Kb strings from column 3 to 1027 in testData, 1 & 2 are pks missing
    IntStream.range(3, 1028).forEach(i -> testData.put("column" + i, getLargeString(16)));

    AirbyteRecordMessageMeta upstreamMeta = new AirbyteRecordMessageMeta()
        .withChanges(List.of(
            new AirbyteRecordMessageMetaChange()
                .withField("upstream_field")
                .withChange(Change.NULLED)
                .withReason(Reason.PLATFORM_SERIALIZATION_ERROR)));
    final Exception ex = assertThrows(RuntimeException.class,
        () -> transformer.transform(
            new StreamDescriptor().withNamespace("test_schema").withName("users_final"), Jsons.jsonNode(testData),
            upstreamMeta));

    assertEquals("Record exceeds size limit, cannot transform without PrimaryKeys in DEDUPE sync", ex.getMessage());
  }

  private String getLargeString(int kbSize) {
    StringBuilder longString = new StringBuilder();
    while (longString.length() < 1024 * kbSize) { // Repeat until the given KB size
      longString.append("Lorem ipsum dolor sit amet, consectetur adipiscing elit. ");
    }
    return longString.toString();
  }

}
