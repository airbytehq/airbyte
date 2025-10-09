/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcTypingDedupingTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.text.Names;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.postgres.PostgresSQLNameTransformer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public abstract class AbstractPostgresTypingDedupingTest extends JdbcTypingDedupingTest {

  private static final int DEFAULT_VARCHAR_LIMIT_IN_JDBC_GEN = 65535;

  private static final Random RANDOM = new Random();

  private String generateBigString() {
    // Generate exactly 2 chars over the limit
    final int length = DEFAULT_VARCHAR_LIMIT_IN_JDBC_GEN + 2;
    return RANDOM
        .ints('a', 'z' + 1)
        .limit(length)
        .collect(StringBuilder::new, StringBuilder::appendCodePoint, StringBuilder::append)
        .toString();
  }

  @Override
  protected SqlGenerator getSqlGenerator() {
    return new PostgresSqlGenerator(new PostgresSQLNameTransformer(), false, false);
  }

  @Override
  protected JdbcCompatibleSourceOperations<?> getSourceOperations() {
    return new PostgresSourceOperations();
  }

  @Disabled
  @Test
  @Override
  public void resumeAfterCancelledTruncate() throws Exception {
    super.resumeAfterCancelledTruncate();
  }

  @Test
  public void testMixedCasedSchema() throws Exception {
    setStreamName("MixedCaseSchema" + getStreamName());
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(new AirbyteStream()
                .withNamespace(getStreamNamespace())
                .withName(getStreamName())
                .withJsonSchema(getSchema()))
            .withMinimumGenerationId(0L)
            .withSyncId(42L)
            .withGenerationId(43L)));

    // First sync
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");

    runSync(catalog, messages1);

    final List<JsonNode> expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison());
  }

  @Test
  public void testMixedCaseRawTableV1V2Migration() throws Exception {
    setStreamName("Mixed Case Table" + getStreamName());
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withNamespace(getStreamNamespace())
                .withName(getStreamName())
                .withJsonSchema(getSchema()))
            .withGenerationId(43L)
            .withMinimumGenerationId(0L)
            .withSyncId(13L)));

    // First sync
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");

    runSync(catalog, messages1, "airbyte/destination-postgres:0.6.3", Function.identity(), null);
    // Special case to retrieve raw records pre DV2 using the same logic as actual code.
    final String rawTableName = "_airbyte_raw_" + Names.toAlphanumericAndUnderscore(getStreamName()).toLowerCase();
    final List<JsonNode> rawActualRecords = getDatabase().queryJsons(
        DSL.selectFrom(DSL.name(getStreamNamespace(), rawTableName)).getSQL());
    // Just verify the size of raw pre DV2, postgres was lower casing the MixedCaseSchema so above
    // retrieval should give 5 records from sync1
    assertEquals(5, rawActualRecords.size());
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");
    runSync(catalog, messages2);
    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_mixedcase_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_mixedcase_expectedrecords_fullrefresh_append_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
  }

  @Test
  public void testRawTableMetaMigration_append() throws Exception {
    final ConfiguredAirbyteCatalog catalog1 = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withNamespace(getStreamNamespace())
                .withName(getStreamName())
                .withJsonSchema(getSchema()))));

    // First sync without _airbyte_meta
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");
    runSync(catalog1, messages1, "airbyte/destination-postgres:2.0.4", Function.identity(), null);
    // Second sync
    final ConfiguredAirbyteCatalog catalog2 = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withNamespace(getStreamNamespace())
                .withName(getStreamName())
                .withJsonSchema(getSchema()))
            .withMinimumGenerationId(0L)
            .withSyncId(13L)
            .withGenerationId(42L)));
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages_after_meta.jsonl");
    runSync(catalog2, messages2);

    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_mixed_meta_raw.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_fullrefresh_append_mixed_meta_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
  }

  @Test
  public void testRawTableMetaMigration_incrementalDedupe() throws Exception {
    final ConfiguredAirbyteCatalog catalog1 = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(getStreamNamespace())
                .withName(getStreamName())
                .withJsonSchema(getSchema()))));

    // First sync without _airbyte_meta
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");
    runSync(catalog1, messages1, "airbyte/destination-postgres:2.0.4", Function.identity(), null);
    // Second sync
    final ConfiguredAirbyteCatalog catalog2 = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(getStreamNamespace())
                .withName(getStreamName())
                .withJsonSchema(getSchema()))
            .withMinimumGenerationId(0L)
            .withSyncId(13L)
            .withGenerationId(42L)));
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages_after_meta.jsonl");
    runSync(catalog2, messages2);

    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_mixed_meta_raw.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_incremental_dedup_meta_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(String streamNamespace, String streamName) throws Exception {
    return super.dumpRawTableRecords(streamNamespace, streamName.toLowerCase());
  }

  @Test
  public void testVarcharLimitOver64K() throws Exception {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(new AirbyteStream()
                .withNamespace(getStreamNamespace())
                .withName(getStreamName())
                .withJsonSchema(getSchema()))
            .withMinimumGenerationId(0L)
            .withSyncId(13L)
            .withGenerationId(42L)));

    final AirbyteMessage message = new AirbyteMessage();
    final String largeString = generateBigString();
    final Map<String, Object> data = ImmutableMap.of(
        "id1", 1,
        "id2", 200,
        "updated_at", "2021-01-01T00:00:00Z",
        "name", largeString);
    message.setType(Type.RECORD);
    message.setRecord(new AirbyteRecordMessage()
        .withNamespace(getStreamNamespace())
        .withStream(getStreamName())
        .withData(Jsons.jsonNode(data))
        .withEmittedAt(1000L));
    final List<AirbyteMessage> messages1 = new ArrayList<>();
    messages1.add(message);
    runSync(catalog, messages1);

    // Only assert on the large varchar string landing in final table.
    // Rest of the fields' correctness is tested by other means in other tests.
    final List<JsonNode> actualFinalRecords = dumpFinalTableRecords(getStreamNamespace(), getStreamName());
    assertEquals(1, actualFinalRecords.size());
    assertEquals(largeString, actualFinalRecords.get(0).get("name").asText());

  }

  @Test
  void testDropCascade() throws Exception {
    ConfiguredAirbyteCatalog catalog1 =
        new ConfiguredAirbyteCatalog()
            .withStreams(
                List.of(
                    new ConfiguredAirbyteStream()
                        .withSyncMode(SyncMode.FULL_REFRESH)
                        .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                        .withCursorField(List.of("updated_at"))
                        .withPrimaryKey(java.util.List.of(List.of("id1"), List.of("id2")))
                        .withStream(
                            new AirbyteStream()
                                .withNamespace(getStreamNamespace())
                                .withName(getStreamName())
                                .withJsonSchema(getSchema()))
                        .withMinimumGenerationId(43L)
                        .withSyncId(42L)
                        .withGenerationId(43L)));

    // First sync
    List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");
    runSync(catalog1, messages1);
    var expectedRawRecords1 = readRecords("dat/sync1_expectedrecords_raw.jsonl");
    var expectedFinalRecords1 = readRecords("dat/sync1_expectedrecords_nondedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison());

    String rawTableName = getRawSchema() + "." +
        getNameTransformer().convertStreamName(
            StreamId.concatenateRawTableName(
                getStreamNamespace(),
                Names.toAlphanumericAndUnderscore(getStreamName())));
    String finalTableName = getStreamNamespace() + "." + Names.toAlphanumericAndUnderscore(getStreamName());
    getDatabase().execute("CREATE VIEW " + getStreamNamespace() + ".v1 AS SELECT * FROM " + rawTableName);
    if (!disableFinalTableComparison()) {
      getDatabase().execute("CREATE VIEW " + getStreamNamespace() + ".v2 AS SELECT * FROM " + finalTableName);
    } // Second sync
    for (var message : messages1) {
      message.getRecord().setEmittedAt(2000L);
    }
    var catalog2 =
        new ConfiguredAirbyteCatalog()
            .withStreams(
                List.of(
                    new ConfiguredAirbyteStream()
                        .withSyncMode(SyncMode.FULL_REFRESH)
                        .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                        .withCursorField(List.of("updated_at"))
                        .withPrimaryKey(java.util.List.of(List.of("id1"), List.of("id2")))
                        .withStream(
                            new AirbyteStream()
                                .withNamespace(getStreamNamespace())
                                .withName(getStreamName())
                                .withJsonSchema(getSchema()))
                        .withMinimumGenerationId(44L)
                        .withSyncId(42L)
                        .withGenerationId(44L)));
    runSync(catalog2, messages1);

    for (var record : expectedRawRecords1) {
      ((ObjectNode) record).put(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, "1970-01-01T00:00:02.000000Z");
      ((ObjectNode) record).put(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID, 44);
    }
    for (var record : expectedFinalRecords1) {
      ((ObjectNode) record).put(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, "1970-01-01T00:00:02.000000Z");
      ((ObjectNode) record).put(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID, 44);
    }
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison());

  }

  @Test
  void testAirbyteMetaAndGenerationIdMigration() throws Exception {
    ConfiguredAirbyteCatalog catalog =
        new ConfiguredAirbyteCatalog()
            .withStreams(
                List.of(
                    new ConfiguredAirbyteStream()
                        .withSyncMode(SyncMode.FULL_REFRESH)
                        .withDestinationSyncMode(DestinationSyncMode.APPEND)
                        .withSyncId(42L)
                        .withGenerationId(43L)
                        .withMinimumGenerationId(0L)
                        .withStream(
                            new AirbyteStream()
                                .withNamespace(getStreamNamespace())
                                .withName(getStreamName())
                                .withJsonSchema(getSchema()))));

    // First sync
    List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");
    runSync(catalog, messages1, "airbyte/destination-postgres:2.0.15", Function.identity(), null);
    List<JsonNode> actualRawRecords1 = dumpRawTableRecords(getStreamNamespace(), getStreamName());
    Set<JsonNode> loadedAtValues1 =
        actualRawRecords1.stream()
            .map((JsonNode record) -> record.get(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT))
            .collect(Collectors.toSet());
    assertEquals(
        1,
        loadedAtValues1.size(),
        "Expected only one value for _airbyte_loaded_at after the 1st sync!");

    // Second sync
    List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");
    runSync(catalog, messages2);

    // The first 5 records in these files were written by the old version, and have
    // several differences with the new records:
    // In raw tables: _airbyte_generation_id at all. _airbyte_meta only contains the changes field
    // In final tables: no generation ID, and airbyte_meta still uses the old `{errors: [...]}`
    // structure
    // So modify the expected records to reflect those differences.
    List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl");
    for (int i = 0; i < 5; i++) {
      ObjectNode record = (ObjectNode) expectedRawRecords2.get(i);
      String originalChanges = record.get(JavaBaseConstants.COLUMN_NAME_AB_META).get("changes").toString();
      record.set(JavaBaseConstants.COLUMN_NAME_AB_META,
          Jsons.deserialize(
              "{\"changes\":" + originalChanges + "}"));
      record.remove(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID);
    }
    List<JsonNode> expectedFinalRecords2 =
        readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl");
    for (int i = 0; i < 5; i++) {
      ObjectNode record = (ObjectNode) expectedFinalRecords2.get(i);
      String originalChanges = record.get(JavaBaseConstants.COLUMN_NAME_AB_META).get("changes").toString();
      record.set(JavaBaseConstants.COLUMN_NAME_AB_META,
          Jsons.deserialize(
              "{\"changes\":" + originalChanges + "}"));
      record.remove(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID);
    }
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());

    // Verify that we didn't trigger a soft reset.
    // There should be two unique loaded_at values in the raw table.
    // (only do this if T+D is enabled to begin with; otherwise loaded_at will just be null)
    if (!disableFinalTableComparison()) {
      List<JsonNode> actualRawRecords2 = dumpRawTableRecords(getStreamNamespace(), getStreamName());
      Set<JsonNode> loadedAtValues2 =
          actualRawRecords2.stream()
              .map((JsonNode record) -> record.get(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT))
              .collect(Collectors.toSet());
      assertEquals(
          2,
          loadedAtValues2.size(),
          "Expected two different values for loaded_at. If there is only 1 value, then we incorrectly triggered a soft reset. If there are more than 2, then something weird happened?");
      assertTrue(
          loadedAtValues2.containsAll(loadedAtValues1),
          "expected the loaded_at value from the 1st sync. If it's not there, then we incorrectly triggered a soft reset.");

    }
  }

  @Test
  void testAirbyteMetaAndGenerationIdMigrationForOverwrite() throws Exception {
    ConfiguredAirbyteCatalog catalog =
        new ConfiguredAirbyteCatalog()
            .withStreams(
                List.of(
                    new ConfiguredAirbyteStream()
                        .withSyncMode(SyncMode.FULL_REFRESH)
                        .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
                        .withSyncId(42L)
                        .withGenerationId(43L)
                        .withMinimumGenerationId(43L)
                        .withStream(
                            new AirbyteStream()
                                .withNamespace(getStreamNamespace())
                                .withName(getStreamName())
                                .withJsonSchema(getSchema()))));

    // First sync
    List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");
    runSync(catalog, messages1, "airbyte/destination-postgres:2.0.15", Function.identity(), null);

    // Second sync
    List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");
    runSync(catalog, messages2);

    List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_overwrite_raw.jsonl");
    List<JsonNode> expectedFinalRecords2 =
        readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
  }

}
