/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.File;
import java.nio.file.Files;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeStagingSqlOperations extends SnowflakeSqlOperations implements SqlOperations {

  public static final String CREATE_STAGE_QUERY = "CREATE STAGE IF NOT EXISTS %s encryption = (type = 'SNOWFLAKE_SSE') copy_options = (on_error='skip_file');";
  public static final String COPY_QUERY = "COPY INTO %s.%s FROM @%s file_format = " +
      "(type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"')";
  public static final String DROP_STAGE_QUERY = "DROP STAGE IF EXISTS %s;";
  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSqlOperations.class);

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
                                    final List<AirbyteRecordMessage> records,
                                    final String schemaName,
                                    final String stage) {
    LOGGER.info("Writing {} records to {}", records.size(), stage);

    if (records.isEmpty()) {
      return;
    }
    try {
      loadDataIntoStage(database, stage, records);
    } catch (final Exception e) {
      LOGGER.error("Failed to upload records into stage {}", stage, e);
      throw new RuntimeException(e);
    }
  }

  private void loadDataIntoStage(final JdbcDatabase database, final String stage, final List<AirbyteRecordMessage> partition) throws Exception {
    final File tempFile = Files.createTempFile(UUID.randomUUID().toString(), ".csv").toFile();
    writeBatchToFile(tempFile, partition);
    database.execute(String.format("PUT file://%s @%s PARALLEL = %d", tempFile.getAbsolutePath(), stage, Runtime.getRuntime().availableProcessors()));
    Files.delete(tempFile.toPath());
  }

  public void createStageIfNotExists(final JdbcDatabase database, final String stageName) throws SQLException {
    AirbyteSentry.executeWithTracing("CreateStageIfNotExists",
        () -> database.execute(getCreateStageQuery(stageName)),
        Map.of("stage", stageName));
  }

  String getCreateStageQuery(String stageName) {
    return String.format(CREATE_STAGE_QUERY, stageName);
  }

  public void copyIntoTmpTableFromStage(final JdbcDatabase database, final String stageName, final String dstTableName, final String schemaName)
      throws SQLException {
    AirbyteSentry.executeWithTracing("CopyIntoTableFromStage",
        () -> database.execute(getCopyQuery(stageName, dstTableName, schemaName)),
        Map.of("schema", schemaName, "stage", stageName, "table", dstTableName));
  }

  String getCopyQuery(String stageName, String dstTableName, String schemaName) {
    return String.format(COPY_QUERY, schemaName, dstTableName, stageName);
  }

  public void dropStageIfExists(final JdbcDatabase database, final String stageName) throws SQLException {
    AirbyteSentry.executeWithTracing("DropStageIfExists",
        () -> database.execute(getDropQuery(stageName)),
        Map.of("stage", stageName));
  }

  String getDropQuery(String stageName) {
    return String.format(DROP_STAGE_QUERY, stageName);
  }

  public void cleanUpStage(final JdbcDatabase database, final String path) throws SQLException {
    AirbyteSentry.executeWithTracing("CleanStage",
        () -> database.execute(String.format("REMOVE @%s;", path)),
        Map.of("path", path));
  }

}
