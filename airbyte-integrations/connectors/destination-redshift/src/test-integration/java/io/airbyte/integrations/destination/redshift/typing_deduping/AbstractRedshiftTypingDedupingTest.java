/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcTypingDedupingTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.destination.redshift.RedshiftInsertDestination;
import io.airbyte.integrations.destination.redshift.RedshiftSQLNameTransformer;
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGeneratorIntegrationTest.RedshiftSourceOperations;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;
import java.util.Random;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.conf.Settings;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Test;

public abstract class AbstractRedshiftTypingDedupingTest extends JdbcTypingDedupingTest {

  private static final Random RANDOM = new Random();

  @Override
  protected String getImageName() {
    return "airbyte/destination-redshift:dev";
  }

  @Override
  protected DataSource getDataSource(final JsonNode config) {
    return new RedshiftInsertDestination().getDataSource(config);
  }

  @Override
  protected JdbcCompatibleSourceOperations<?> getSourceOperations() {
    return new RedshiftSourceOperations();
  }

  @Override
  protected SqlGenerator getSqlGenerator() {
    return new RedshiftSqlGenerator(new RedshiftSQLNameTransformer()) {

      // Override only for tests to print formatted SQL. The actual implementation should use unformatted
      // to save bytes.
      @Override
      protected DSLContext getDslContext() {
        return DSL.using(getDialect(), new Settings().withRenderFormatted(true));
      }

    };
  }

  @Test
  public void testRawTableMetaMigration_append() throws Exception {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    // First sync without _airbyte_meta
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages_before_meta.jsonl");
    runSync(catalog, messages1, "airbyte/destination-redshift:2.1.10");
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
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));

    // First sync without _airbyte_meta
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages_before_meta.jsonl");
    runSync(catalog, messages1, "airbyte/destination-redshift:2.1.10");
    // Second sync
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages_after_meta.jsonl");
    runSync(catalog, messages2);

    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_mixed_meta_raw.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_incremental_dedup_meta_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
  }

  @Test
  public void testRawTableLoadWithSuperVarcharLimitation() throws Exception {
    final String record1 = """
                           {"type": "RECORD",
                             "record":{
                               "emitted_at": 1000,
                               "data": {
                                 "id1": 1,
                                 "id2": 200,
                                 "updated_at": "2000-01-01T00:00:00Z",
                                 "_ab_cdc_deleted_at": null,
                                 "name": "PLACE_HOLDER",
                                 "address": {"city": "San Francisco", "state": "CA"}}
                             }
                           }
                           """;
    final String record2 = """
                           {"type": "RECORD",
                             "record":{
                               "emitted_at": 1000,
                               "data": {
                                 "id1": 2,
                                 "id2": 201,
                                 "updated_at": "2000-01-01T00:00:00Z",
                                 "_ab_cdc_deleted_at": null,
                                 "name": "PLACE_HOLDER",
                                 "address": {"city": "New York", "state": "NY"}}
                             }
                           }
                           """;
    final String largeString1 = generateBigString(0);
    final String largeString2 = generateBigString(2);
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(new AirbyteStream()
                .withNamespace(streamNamespace)
                .withName(streamName)
                .withJsonSchema(SCHEMA))));
    final AirbyteMessage message1 = Jsons.deserialize(record1, AirbyteMessage.class);
    message1.getRecord().setNamespace(streamNamespace);
    message1.getRecord().setStream(streamName);
    ((ObjectNode) message1.getRecord().getData()).put("name", largeString1);
    final AirbyteMessage message2 = Jsons.deserialize(record2, AirbyteMessage.class);
    message2.getRecord().setNamespace(streamNamespace);
    message2.getRecord().setStream(streamName);
    ((ObjectNode) message2.getRecord().getData()).put("name", largeString2);

    // message1 should be preserved which is just on limit, message2 should be nulled.
    runSync(catalog, List.of(message1, message2));

    // Add verification.
    final List<JsonNode> expectedRawRecords = readRecords("dat/sync1_recordnull_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords = readRecords("dat/sync1_recordnull_expectedrecords_final.jsonl");
    // Only replace for first record, second record should be nulled by transformer.
    ((ObjectNode) expectedRawRecords.get(0).get("_airbyte_data")).put("name", largeString1);
    ((ObjectNode) expectedFinalRecords.get(0)).put("name", largeString1);
    verifySyncResult(expectedRawRecords, expectedFinalRecords, disableFinalTableComparison());

  }

  private String generateBigString(final int additionalChars) {
    // Generate exactly 2 chars over the limit
    final int length = RedshiftSuperLimitationTransformer.REDSHIFT_VARCHAR_MAX_BYTE_SIZE + additionalChars;
    return RANDOM
        .ints('a', 'z' + 1)
        .limit(length)
        .collect(StringBuilder::new, StringBuilder::appendCodePoint, StringBuilder::append)
        .toString();
  }

}
