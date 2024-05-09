/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.snowflake.OssCloudEnvVarConsts;
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabase;
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import io.airbyte.workers.exception.TestHarnessException;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;

public abstract class AbstractSnowflakeTypingDedupingTest extends BaseTypingDedupingTest {

  public static final Map<String, String> FINAL_METADATA_COLUMN_NAMES = Map.of(
      "_airbyte_raw_id", "_AIRBYTE_RAW_ID",
      "_airbyte_extracted_at", "_AIRBYTE_EXTRACTED_AT",
      "_airbyte_loaded_at", "_AIRBYTE_LOADED_AT",
      "_airbyte_data", "_AIRBYTE_DATA",
      "_airbyte_meta", "_AIRBYTE_META");
  private String databaseName;
  private JdbcDatabase database;
  private DataSource dataSource;

  private static volatile boolean cleanedAirbyteInternalTable = false;

  private static void cleanAirbyteInternalTable(JdbcDatabase database) throws SQLException {
    if (!cleanedAirbyteInternalTable) {
      synchronized (AbstractSnowflakeTypingDedupingTest.class) {
        if (!cleanedAirbyteInternalTable) {
          database.execute("DELETE FROM \"airbyte_internal\".\"_airbyte_destination_state\" WHERE \"updated_at\" < current_date() - 7");
          cleanedAirbyteInternalTable = true;
        }
      }
    }
  }

  protected abstract String getConfigPath();

  @Override
  protected String getImageName() {
    return "airbyte/destination-snowflake:dev";
  }

  @Override
  protected JsonNode generateConfig() throws SQLException {
    final JsonNode config = Jsons.deserialize(IOs.readFile(Path.of(getConfigPath())));
    ((ObjectNode) config).put("schema", "typing_deduping_default_schema" + getUniqueSuffix());
    databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    dataSource = SnowflakeDatabase.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS);
    database = SnowflakeDatabase.getDatabase(dataSource);
    cleanAirbyteInternalTable(database);
    return config;
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(String streamNamespace, final String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema();
    }
    final String tableName = StreamId.concatenateRawTableName(streamNamespace, streamName);
    final String schema = getRawSchema();
    return SnowflakeTestUtils.dumpRawTable(
        database,
        // Explicitly wrap in quotes to prevent snowflake from upcasing
        '"' + schema + "\".\"" + tableName + '"');
  }

  @Override
  public List<JsonNode> dumpFinalTableRecords(String streamNamespace, final String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema();
    }
    return SnowflakeTestUtils.dumpFinalTable(database, databaseName, streamNamespace.toUpperCase(), streamName.toUpperCase());
  }

  @Override
  protected void teardownStreamAndNamespace(String streamNamespace, final String streamName) throws Exception {
    if (streamNamespace == null) {
      streamNamespace = getDefaultSchema();
    }
    database.execute(
        String.format(
            """
            DROP TABLE IF EXISTS "%s"."%s";
            DROP SCHEMA IF EXISTS "%s" CASCADE
            """,
            getRawSchema(),
            // Raw table is still lowercase.
            StreamId.concatenateRawTableName(streamNamespace, streamName),
            streamNamespace.toUpperCase()));
  }

  @Override
  protected void globalTeardown() throws Exception {
    DataSourceFactory.close(dataSource);
  }

  @Override
  protected SqlGenerator getSqlGenerator() {
    return new SnowflakeSqlGenerator(0);
  }

  @Override
  public Map<String, String> getFinalMetadataColumnNames() {
    return FINAL_METADATA_COLUMN_NAMES;
  }

  /**
   * Subclasses using a config with a nonstandard raw table schema should override this method.
   */
  protected String getRawSchema() {
    return JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;
  }

  /**
   * Run a sync using 3.0.0 (which is the highest version that still creates v2 final tables with
   * lowercased+quoted names). Then run a sync using our current version.
   */
  @Test
  public void testFinalTableUppercasingMigration_append() throws Exception {
    try {
      final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
          new ConfiguredAirbyteStream()
              .withSyncMode(SyncMode.FULL_REFRESH)
              .withDestinationSyncMode(DestinationSyncMode.APPEND)
              .withStream(new AirbyteStream()
                  .withNamespace(getStreamNamespace())
                  .withName(getStreamName())
                  .withJsonSchema(SCHEMA))));

      // First sync
      final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");
      runSync(catalog, messages1, "airbyte/destination-snowflake:3.0.0");
      // We no longer have the code to dump a lowercased table, so just move on directly to the new sync

      // Second sync
      final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");

      runSync(catalog, messages2);

      final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw_mixed_tzs.jsonl");
      final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl");
      verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
    } finally {
      // manually drop the lowercased schema, since we no longer have the code to do it automatically
      // (the raw table is still in lowercase "airbyte_internal"."whatever", so the auto-cleanup code
      // handles it fine)
      database.execute("DROP SCHEMA IF EXISTS \"" + getStreamNamespace() + "\" CASCADE");
    }
  }

  @Test
  public void testFinalTableUppercasingMigration_overwrite() throws Exception {
    try {
      final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
          new ConfiguredAirbyteStream()
              .withSyncMode(SyncMode.FULL_REFRESH)
              .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
              .withStream(new AirbyteStream()
                  .withNamespace(getStreamNamespace())
                  .withName(getStreamName())
                  .withJsonSchema(SCHEMA))));

      // First sync
      final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");
      runSync(catalog, messages1, "airbyte/destination-snowflake:3.0.0");
      // We no longer have the code to dump a lowercased table, so just move on directly to the new sync

      // Second sync
      final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");

      runSync(catalog, messages2);

      final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_raw.jsonl");
      final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_fullrefresh_overwrite_final.jsonl");
      verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
    } finally {
      // manually drop the lowercased schema, since we no longer have the code to do it automatically
      // (the raw table is still in lowercase "airbyte_internal"."whatever", so the auto-cleanup code
      // handles it fine)
      database.execute("DROP SCHEMA IF EXISTS \"" + getStreamNamespace() + "\" CASCADE");
    }
  }

  @Test
  public void testRemovingPKNonNullIndexes() throws Exception {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(getStreamNamespace())
                .withName(getStreamName())
                .withJsonSchema(SCHEMA))));

    // First sync
    final List<AirbyteMessage> messages = readMessages("dat/sync_null_pk.jsonl");
    final TestHarnessException e = assertThrows(
        TestHarnessException.class,
        () -> runSync(catalog, messages, "airbyte/destination-snowflake:3.1.18")); // this version introduced non-null PKs to the final tables
    // ideally we would assert on the logged content of the original exception within e, but that is
    // proving to be tricky

    // Second sync
    runSync(catalog, messages); // does not throw with latest version
    assertEquals(1, dumpFinalTableRecords(getStreamNamespace(), getStreamName()).toArray().length);
  }

  @Test
  public void testExtractedAtUtcTimezoneMigration() throws Exception {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withCursorField(List.of("updated_at"))
            .withStream(new AirbyteStream()
                .withNamespace(getStreamNamespace())
                .withName(getStreamName())
                .withJsonSchema(SCHEMA))));

    // First sync
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");
    runSync(catalog, messages1, "airbyte/destination-snowflake:3.5.11");

    final List<JsonNode> expectedRawRecords1 = readRecords("dat/ltz_extracted_at_sync1_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords1 = readRecords("dat/ltz_extracted_at_sync1_expectedrecords_dedup_final.jsonl");
    verifySyncResult(expectedRawRecords1, expectedFinalRecords1, disableFinalTableComparison());

    // Second sync
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");

    runSync(catalog, messages2);

    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw_mixed_tzs.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_incremental_dedup_final_mixed_tzs.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
  }

  private String getDefaultSchema() {
    return getConfig().get("schema").asText();
  }

}
