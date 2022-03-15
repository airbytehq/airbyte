/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.record_buffer.RecordBufferImplementation;
import io.airbyte.integrations.destination.staging.StagingOperations;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.StringJoiner;
import org.joda.time.DateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeInternalStagingSqlOperations extends SnowflakeSqlOperations implements StagingOperations {

  private static final int MAX_FILES_IN_LOADING_QUERY_LIMIT = 1000;
  public static final String CREATE_STAGE_QUERY =
      "CREATE STAGE IF NOT EXISTS %s encryption = (type = 'SNOWFLAKE_SSE') copy_options = (on_error='skip_file');";
  public static final String COPY_QUERY = "COPY INTO %s.%s FROM @%s file_format = " +
      "(type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"') ";
  public static final String DROP_STAGE_QUERY = "DROP STAGE IF EXISTS %s;";
  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSqlOperations.class);
  private final NamingConventionTransformer nameTransformer;

  public SnowflakeInternalStagingSqlOperations(final NamingConventionTransformer nameTransformer) {
    this.nameTransformer = nameTransformer;
  }

  @Override
  public String getStageName(final String namespace, final String streamName) {
    return nameTransformer.applyDefaultCase(String.join("_",
        nameTransformer.convertStreamName(namespace),
        nameTransformer.convertStreamName(streamName)));
  }

  @Override
  public String getStagingPath(final String connectionId, final String namespace, final String streamName, final DateTime writeDatetime) {
    // see https://docs.snowflake.com/en/user-guide/data-load-considerations-stage.html
    return nameTransformer.applyDefaultCase(String.format("%s/%s/%02d/%02d/%02d/%s/",
        getStageName(namespace, streamName),
        writeDatetime.year().get(),
        writeDatetime.monthOfYear().get(),
        writeDatetime.dayOfMonth().get(),
        writeDatetime.hourOfDay().get(),
        connectionId));
  }

  @Override
  public String uploadRecordsToStage(final JdbcDatabase database,
                                     final RecordBufferImplementation recordsData,
                                     final String schema,
                                     final String stage) {
    try {
      loadDataIntoStage(database, stage, recordsData);
      return recordsData.getFilename();
    } catch (final Exception e) {
      LOGGER.error("Failed to upload records into stage {}", stage, e);
      throw new RuntimeException(e);
    }
  }

  private void loadDataIntoStage(final JdbcDatabase database, final String stage, final RecordBufferImplementation recordsData) throws Exception {
    database.execute(
        String.format("PUT file://%s @%s PARALLEL = %d", recordsData.getFile().getAbsolutePath(), stage, Runtime.getRuntime().availableProcessors()));
  }

  @Override
  public void createStageIfNotExists(final JdbcDatabase database, final String stageName) throws Exception {
    AirbyteSentry.executeWithTracing("CreateStageIfNotExists",
        () -> database.execute(getCreateStageQuery(stageName)),
        Map.of("stage", stageName));
  }

  @Override
  public void copyIntoTmpTableFromStage(final JdbcDatabase database,
                                        final String stageName,
                                        final List<String> stagedFiles,
                                        final String dstTableName,
                                        final String schemaName)
      throws SQLException {
    AirbyteSentry.executeWithTracing("CopyIntoTableFromStage",
        () -> database.execute(getCopyQuery(stageName, stagedFiles, dstTableName, schemaName)),
        Map.of("schema", schemaName, "stage", stageName, "table", dstTableName));
  }

  protected String getCreateStageQuery(final String stageName) {
    return String.format(CREATE_STAGE_QUERY, stageName);
  }

  protected String getCopyQuery(final String stageName, final List<String> stagedFiles, final String dstTableName, final String schemaName) {
    return String.format(COPY_QUERY + generateFilesList(stagedFiles) + ";", schemaName, dstTableName, stageName);
  }

  private String generateFilesList(final List<String> files) {
    if (files.size() < MAX_FILES_IN_LOADING_QUERY_LIMIT) {
      // see https://docs.snowflake.com/en/user-guide/data-load-considerations-load.html#lists-of-files
      final StringJoiner joiner = new StringJoiner(",");
      files.forEach(filename -> joiner.add("'" + filename.substring(filename.lastIndexOf("/") + 1) + "'"));
      return "files = (" + joiner + ") ";
    } else {
      return "";
    }
  }

  @Override
  public void dropStageIfExists(final JdbcDatabase database, final String stageName) throws Exception {
    AirbyteSentry.executeWithTracing("DropStageIfExists",
        () -> database.execute(getDropQuery(stageName)),
        Map.of("stage", stageName));
  }

  protected String getDropQuery(final String stageName) {
    return String.format(DROP_STAGE_QUERY, stageName);
  }

  @Override
  public void cleanUpStage(final JdbcDatabase database, final String path, final List<String> stagedFiles) throws Exception {
    AirbyteSentry.executeWithTracing("CleanStage",
        () -> database.execute(String.format("REMOVE @%s;", path)),
        Map.of("path", path));
  }

}
