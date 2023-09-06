/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
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
import java.nio.file.Path;
import java.util.List;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;

public abstract class AbstractSnowflakeTypingDedupingTest extends BaseTypingDedupingTest {

  private String databaseName;
  private JdbcDatabase database;
  private DataSource dataSource;

  protected abstract String getConfigPath();

  @Override
  protected String getImageName() {
    return "airbyte/destination-snowflake:dev";
  }

  @Override
  protected JsonNode generateConfig() {
    final JsonNode config = Jsons.deserialize(IOs.readFile(Path.of(getConfigPath())));
    ((ObjectNode) config).put("schema", "typing_deduping_default_schema" + getUniqueSuffix());
    databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    dataSource = SnowflakeDatabase.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS);
    database = SnowflakeDatabase.getDatabase(dataSource);
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
  protected List<JsonNode> dumpFinalTableRecords(String streamNamespace, final String streamName) throws Exception {
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
  protected SqlGenerator<?> getSqlGenerator() {
    return new SnowflakeSqlGenerator();
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
                  .withNamespace(streamNamespace)
                  .withName(streamName)
                  .withJsonSchema(SCHEMA))));

      // First sync
      final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");
      runSync(catalog, messages1, "airbyte/destination-snowflake:3.0.0");
      // We no longer have the code to dump a lowercased table, so just move on directly to the new sync

      // Second sync
      final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");

      runSync(catalog, messages2);

      final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_fullrefresh_append_raw.jsonl");
      final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl");
      verifySyncResult(expectedRawRecords2, expectedFinalRecords2);
    } finally {
      // manually drop the lowercased schema, since we no longer have the code to do it automatically
      // (the raw table is still in lowercase "airbyte_internal"."whatever", so the auto-cleanup code
      // handles it fine)
      database.execute("DROP SCHEMA IF EXISTS \"" + streamNamespace + "\" CASCADE");
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
                  .withNamespace(streamNamespace)
                  .withName(streamName)
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
      verifySyncResult(expectedRawRecords2, expectedFinalRecords2);
    } finally {
      // manually drop the lowercased schema, since we no longer have the code to do it automatically
      // (the raw table is still in lowercase "airbyte_internal"."whatever", so the auto-cleanup code
      // handles it fine)
      database.execute("DROP SCHEMA IF EXISTS \"" + streamNamespace + "\" CASCADE");
    }
  }

  private String getDefaultSchema() {
    return getConfig().get("schema").asText();
  }

}
