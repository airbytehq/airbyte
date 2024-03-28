/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.commons.string.Strings;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeInternalStagingSqlOperations extends SnowflakeSqlStagingOperations {

  public static final int UPLOAD_RETRY_LIMIT = 3;

  private static final String CREATE_STAGE_QUERY =
      "CREATE STAGE IF NOT EXISTS %s encryption = (type = 'SNOWFLAKE_SSE') copy_options = (on_error='skip_file');";
  private static final String PUT_FILE_QUERY = "PUT file://%s @%s/%s PARALLEL = %d;";
  private static final String LIST_STAGE_QUERY = "LIST @%s/%s/%s;";
  // the 1s1t copy query explicitly quotes the raw table+schema name.
  // we set error_on_column_count_mismatch because (at time of writing), we haven't yet added
  // the airbyte_meta column to the raw table.
  // See also https://github.com/airbytehq/airbyte/issues/36410 for improved error handling.
  // TODO remove error_on_column_count_mismatch once snowflake has airbyte_meta in raw data.
  private static final String COPY_QUERY_1S1T =
      """
      COPY INTO "%s"."%s" FROM '@%s/%s'
      file_format = (
        type = csv
        compression = auto
        field_delimiter = ','
        skip_header = 0
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        NULL_IF=('')
        error_on_column_count_mismatch=false
      )""";
  private static final String DROP_STAGE_QUERY = "DROP STAGE IF EXISTS %s;";
  private static final String REMOVE_QUERY = "REMOVE @%s;";

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSqlOperations.class);

  private final NamingConventionTransformer nameTransformer;

  public SnowflakeInternalStagingSqlOperations(final NamingConventionTransformer nameTransformer) {
    this.nameTransformer = nameTransformer;
  }

  @Override
  public String getStageName(final String namespace, final String streamName) {
    return String.join(".",
        '"' + nameTransformer.convertStreamName(namespace) + '"',
        '"' + nameTransformer.convertStreamName(streamName) + '"');
  }

  @Override
  public String getStagingPath(final UUID connectionId,
                               final String namespace,
                               final String streamName,
                               final String outputTableName,
                               final Instant writeDatetime) {
    // see https://docs.snowflake.com/en/user-guide/data-load-considerations-stage.html
    final var zonedDateTime = ZonedDateTime.ofInstant(writeDatetime, ZoneOffset.UTC);
    return nameTransformer.applyDefaultCase(String.format("%s/%02d/%02d/%02d/%s/",
        zonedDateTime.getYear(),
        zonedDateTime.getMonthValue(),
        zonedDateTime.getDayOfMonth(),
        zonedDateTime.getHour(),
        connectionId));
  }

  @Override
  public String uploadRecordsToStage(final JdbcDatabase database,
                                     final SerializableBuffer recordsData,
                                     final String namespace,
                                     final String stageName,
                                     final String stagingPath)
      throws IOException {
    final List<Exception> exceptionsThrown = new ArrayList<>();
    boolean succeeded = false;
    while (exceptionsThrown.size() < UPLOAD_RETRY_LIMIT && !succeeded) {
      try {
        uploadRecordsToBucket(database, stageName, stagingPath, recordsData);
        succeeded = true;
      } catch (final Exception e) {
        LOGGER.error("Failed to upload records into stage {}", stagingPath, e);
        exceptionsThrown.add(e);
      }
      if (!succeeded) {
        LOGGER.info("Retrying to upload records into stage {} ({}/{}})", stagingPath, exceptionsThrown.size(), UPLOAD_RETRY_LIMIT);
      }
    }
    if (!succeeded) {
      throw new RuntimeException(
          String.format("Exceptions thrown while uploading records into stage: %s", Strings.join(exceptionsThrown, "\n")));
    }
    LOGGER.info("Successfully loaded records to stage {} with {} re-attempt(s)", stagingPath, exceptionsThrown.size());
    return recordsData.getFilename();
  }

  private void uploadRecordsToBucket(final JdbcDatabase database,
                                     final String stageName,
                                     final String stagingPath,
                                     final SerializableBuffer recordsData)
      throws Exception {
    final String query = getPutQuery(stageName, stagingPath, recordsData.getFile().getAbsolutePath());
    LOGGER.debug("Executing query: {}", query);
    database.execute(query);
    if (!checkStageObjectExists(database, stageName, stagingPath, recordsData.getFilename())) {
      LOGGER.error(String.format("Failed to upload data into stage, object @%s not found",
          (stagingPath + "/" + recordsData.getFilename()).replaceAll("/+", "/")));
      throw new RuntimeException("Upload failed");
    }
  }

  protected String getPutQuery(final String stageName, final String stagingPath, final String filePath) {
    return String.format(PUT_FILE_QUERY, filePath, stageName, stagingPath, Runtime.getRuntime().availableProcessors());
  }

  private boolean checkStageObjectExists(final JdbcDatabase database, final String stageName, final String stagingPath, final String filename)
      throws SQLException {
    final String query = getListQuery(stageName, stagingPath, filename);
    LOGGER.debug("Executing query: {}", query);
    final boolean result;
    try (final Stream<JsonNode> stream = database.unsafeQuery(query)) {
      result = stream.findAny().isPresent();
    }
    return result;
  }

  /**
   * Creates a SQL query to list all files that have been staged
   *
   * @param stageName name of staging folder
   * @param stagingPath path to the files within the staging folder
   * @param filename name of the file within staging area
   * @return SQL query string
   */
  protected String getListQuery(final String stageName, final String stagingPath, final String filename) {
    return String.format(LIST_STAGE_QUERY, stageName, stagingPath, filename).replaceAll("/+", "/");
  }

  @Override
  public void createStageIfNotExists(final JdbcDatabase database, final String stageName) throws Exception {
    final String query = getCreateStageQuery(stageName);
    LOGGER.debug("Executing query: {}", query);
    try {
      database.execute(query);
    } catch (final Exception e) {
      throw checkForKnownConfigExceptions(e).orElseThrow(() -> e);
    }
  }

  /**
   * Creates a SQL query to create a staging folder. This query will create a staging folder if one
   * previously did not exist
   *
   * @param stageName name of the staging folder
   * @return SQL query string
   */
  protected String getCreateStageQuery(final String stageName) {
    return String.format(CREATE_STAGE_QUERY, stageName);
  }

  @Override
  public void copyIntoTableFromStage(final JdbcDatabase database,
                                     final String stageName,
                                     final String stagingPath,
                                     final List<String> stagedFiles,
                                     final String tableName,
                                     final String schemaName)
      throws SQLException {
    try {
      final String query = getCopyQuery(stageName, stagingPath, stagedFiles, tableName, schemaName);
      LOGGER.debug("Executing query: {}", query);
      database.execute(query);
    } catch (final SQLException e) {
      throw checkForKnownConfigExceptions(e).orElseThrow(() -> e);
    }
  }

  /**
   * Creates a SQL query to bulk copy data into fully qualified destination table See
   * https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html for more context
   *
   * @param stageName name of staging folder
   * @param stagingPath path of staging folder to data files
   * @param stagedFiles collection of the staging files
   * @param dstTableName name of destination table
   * @param schemaName name of schema
   * @return SQL query string
   */
  protected String getCopyQuery(final String stageName,
                                final String stagingPath,
                                final List<String> stagedFiles,
                                final String dstTableName,
                                final String schemaName) {
    return String.format(COPY_QUERY_1S1T + generateFilesList(stagedFiles) + ";", schemaName, dstTableName, stageName, stagingPath);
  }

  @Override
  public void dropStageIfExists(final JdbcDatabase database, final String stageName, final String stagingPath) throws Exception {
    try {
      final String query = getDropQuery(stageName);
      LOGGER.debug("Executing query: {}", query);
      database.execute(query);
    } catch (final SQLException e) {
      throw checkForKnownConfigExceptions(e).orElseThrow(() -> e);
    }
  }

  /**
   * Creates a SQL query to drop staging area and all associated files within the staged area
   *
   * @param stageName name of staging folder
   * @return SQL query string
   */
  protected String getDropQuery(final String stageName) {
    return String.format(DROP_STAGE_QUERY, stageName);
  }

  /**
   * Creates a SQL query used to remove staging files that were just staged See
   * https://docs.snowflake.com/en/sql-reference/sql/remove.html for more context
   *
   * @param stageName name of staging folder
   * @return SQL query string
   */
  protected String getRemoveQuery(final String stageName) {
    return String.format(REMOVE_QUERY, stageName);
  }

}
