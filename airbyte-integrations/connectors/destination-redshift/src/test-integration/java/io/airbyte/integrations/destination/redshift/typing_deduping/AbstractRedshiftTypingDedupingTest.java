/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcTypingDedupingTest;
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
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.conf.Settings;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Test;

public abstract class AbstractRedshiftTypingDedupingTest extends JdbcTypingDedupingTest {

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

}
