/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import java.io.IOException;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.stream.Stream;
import org.joda.time.DateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeBulkLoadSqlOperations extends SnowflakeSqlOperations {

  public static final int UPLOAD_RETRY_LIMIT = 3;

  private static final String PUT_FILE_QUERY = "PUT file://%s @%s/%s PARALLEL = %d;";
  private static final String LIST_STAGE_QUERY = "LIST @%s/%s/%s;";
  // the 1s1t copy query explicitly quotes the raw table+schema name.
  private static final String COPY_QUERY_EXTERNAL_STAGE =
      """
      COPY INTO "%s"."%s" FROM '@%s/'
      file_format = %s
      """;

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSqlOperations.class);

  private final NamingConventionTransformer nameTransformer;
  private final boolean use1s1t;

  public SnowflakeBulkLoadSqlOperations(final NamingConventionTransformer nameTransformer) {
    this.nameTransformer = nameTransformer;
    this.use1s1t = TypingAndDedupingFlag.isDestinationV2();
  }

  public String getStagingPath(final UUID connectionId, final String namespace, final String streamName, final DateTime writeDatetime) {
    // see https://docs.snowflake.com/en/user-guide/data-load-considerations-stage.html
    return nameTransformer.applyDefaultCase(String.format("%s/%02d/%02d/%02d/%s/",
        writeDatetime.year().get(),
        writeDatetime.monthOfYear().get(),
        writeDatetime.dayOfMonth().get(),
        writeDatetime.hourOfDay().get(),
        connectionId));
  }

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
                                     final SerializableBuffer recordsData) {
    // No-op;
    return;
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

  public void copyIntoTableFromStage(final JdbcDatabase database,
                                     final String stageName,
                                     final List<String> stagedFiles,
                                     final String tableName,
                                     final String schemaName,
                                     final String fileFormatName)
      throws SQLException {
    try {
      final String query = getCopyQuery(stageName, stagedFiles, tableName, schemaName, fileFormatName);
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
   * @param stagedFiles collection of the staging files
   * @param dstTableName name of destination table
   * @param schemaName name of schema
   * @param fileFormatName name of pre-created Snowflake file format
   * @return SQL query string
   */
  protected String getCopyQuery(final String stageName,
                                final List<String> stagedFiles,
                                final String dstTableName,
                                final String schemaName,
                                final String fileFormatName) {
    return String.format(COPY_QUERY_EXTERNAL_STAGE, schemaName, dstTableName, stageName, fileFormatName) + generateFilesList(stagedFiles) + ";";
  }

}
