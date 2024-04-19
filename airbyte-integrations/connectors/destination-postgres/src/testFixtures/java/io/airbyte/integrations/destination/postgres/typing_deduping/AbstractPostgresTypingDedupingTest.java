/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcTypingDedupingTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.text.Names;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
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
import org.jooq.impl.DSL;
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
    return new PostgresSqlGenerator(new PostgresSQLNameTransformer(), false);
  }

  @Override
  protected JdbcCompatibleSourceOperations<?> getSourceOperations() {
    return new PostgresSourceOperations();
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
                .withJsonSchema(getSchema()))));

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
                .withJsonSchema(getSchema()))));

    // First sync
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");

    runSync(catalog, messages1, "airbyte/destination-postgres:0.6.3");
    // Special case to retrieve raw records pre DV2 using the same logic as actual code.
    final List<JsonNode> rawActualRecords = getDatabase().queryJsons(
        DSL.selectFrom(DSL.name(getStreamNamespace(), "_airbyte_raw_" + Names.toAlphanumericAndUnderscore(getStreamName()).toLowerCase())).getSQL());
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
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withNamespace(getStreamNamespace())
                .withName(getStreamName())
                .withJsonSchema(getSchema()))));

    // First sync without _airbyte_meta
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");
    runSync(catalog, messages1, "airbyte/destination-postgres:2.0.4");
    // Second sync
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages_after_meta.jsonl");
    runSync(catalog, messages2);

    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_mixed_meta_raw.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_fullrefresh_append_mixed_meta_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
  }

  @Test
  public void testRawTableMetaMigration_incrementalDedupe() throws Exception {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
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
    runSync(catalog, messages1, "airbyte/destination-postgres:2.0.4");
    // Second sync
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages_after_meta.jsonl");
    runSync(catalog, messages2);

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
                .withJsonSchema(getSchema()))));

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

}
