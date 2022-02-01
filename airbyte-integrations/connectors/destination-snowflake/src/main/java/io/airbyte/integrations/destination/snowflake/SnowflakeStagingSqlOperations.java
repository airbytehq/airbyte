/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
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

public class SnowflakeStagingSqlOperations extends JdbcSqlOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSqlOperations.class);

  @Override
  protected void insertRecordsInternal(final JdbcDatabase database,
                                       final List<AirbyteRecordMessage> records,
                                       final String schemaName,
                                       final String stage) {
    LOGGER.info("actual size of batch for staging: {}", records.size());

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
    final String query = "CREATE STAGE IF NOT EXISTS %s encryption = (type = 'SNOWFLAKE_SSE') copy_options = (on_error='skip_file');";
    AirbyteSentry.executeWithTracing("CreateStageIfNotExists",
        () -> database.execute(String.format(query, stageName)),
        Map.of("stage", stageName));
  }

  public void copyIntoTmpTableFromStage(final JdbcDatabase database, final String stageName, final String dstTableName, final String schemaName)
      throws SQLException {
    final String query = "COPY INTO %s.%s FROM @%s file_format = " +
        "(type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"')";
    AirbyteSentry.executeWithTracing("CopyIntoTableFromStage",
        () -> database.execute(String.format(query, schemaName, dstTableName, stageName)),
        Map.of("schema", schemaName, "stage", stageName, "table", dstTableName));
  }

  public void dropStageIfExists(final JdbcDatabase database, final String stageName) throws SQLException {
    AirbyteSentry.executeWithTracing("DropStageIfExists",
        () -> database.execute(String.format("DROP STAGE IF EXISTS %s;", stageName)),
        Map.of("stage", stageName));
  }

  @Override
  public void createTableIfNotExists(final JdbcDatabase database, final String schemaName, final String tableName) throws SQLException {
    AirbyteSentry.executeWithTracing("CreateTableIfNotExists",
        () -> database.execute(createTableQuery(database, schemaName, tableName)),
        Map.of("schema", schemaName, "table", tableName));
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s VARCHAR PRIMARY KEY,\n"
            + "%s VARIANT,\n"
            + "%s TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp()\n"
            + ") data_retention_time_in_days = 0;",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  public void cleanUpStage(final JdbcDatabase database, final String path) throws SQLException {
    AirbyteSentry.executeWithTracing("CleanStage",
        () -> database.execute(String.format("REMOVE @%s;", path)),
        Map.of("path", path));
  }

  @Override
  public boolean isSchemaExists(final JdbcDatabase database, final String outputSchema) throws Exception {
    return database.query(SHOW_SCHEMAS).map(schemas -> schemas.get(NAME).asText()).anyMatch(outputSchema::equalsIgnoreCase);
  }

}
