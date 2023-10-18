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
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.stream.Stream;
import org.joda.time.DateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeBulkLoadSqlOperations extends SnowflakeInternalStagingSqlOperations {

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

  public SnowflakeBulkLoadSqlOperations(final NamingConventionTransformer nameTransformer) {
    super(nameTransformer);
  }

  public String uploadRecordsToStage(final JdbcDatabase database,
                                     final SerializableBuffer recordsData,
                                     final String namespace,
                                     final String stageName,
                                     final String stagingPath)
      throws IOException {
    final List<Exception> exceptionsThrown = new ArrayList<>();
    boolean succeeded = false;
    final String query = getPutQuery(stageName, stagingPath, recordsData.getFile().getAbsolutePath());
    while (exceptionsThrown.size() < UPLOAD_RETRY_LIMIT && !succeeded) {
      try {
        LOGGER.debug("Executing query: {}", query);
        database.execute(query);
        if (!checkStageObjectExists(database, stageName, stagingPath, recordsData.getFilename())) {
          LOGGER.error(String.format("Failed to upload data into stage, object @%s not found",
              (stagingPath + "/" + recordsData.getFilename()).replaceAll("/+", "/")));
          throw new RuntimeException("Upload failed");
        }
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

  protected String getPutQuery(final String stageName, final String stagingPath, final String filePath) {
    return String.format(PUT_FILE_QUERY, filePath, stageName, stagingPath, Runtime.getRuntime().availableProcessors());
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
