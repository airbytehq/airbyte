/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.commons.string.Strings;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeBulkLoadSqlOperations extends SnowflakeInternalStagingSqlOperations {

  public static final int UPLOAD_RETRY_LIMIT = 3;
  public static final String BULK_LOAD_FILE_FORMAT = "bulk_load_file_format";
  public static final String BULK_LOAD_S3_STAGES = "bulk_load_s3_stages";

  private static final String PUT_FILE_QUERY = "PUT file://%s @%s/%s PARALLEL = %d;";
  // the 1s1t copy query explicitly quotes the raw table+schema name.
  private static final String COPY_QUERY_EXTERNAL_STAGE =
      """
      COPY INTO "%s"."%s" FROM '@%s/'
      file_format = %s
      """;

  // The name of the file format and stage to use for the BULK LOAD operation
  private String bulkLoadFileFormatName;
  private String bulkLoadStageName;

  // The name of the record property that contains the file paths
  private String bulkLoadFilePropertyNameInRecord;
  private List<String> bulkLoadFilesList = new ArrayList<>();

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeBulkLoadSqlOperations.class);

  public SnowflakeBulkLoadSqlOperations(
                                        final NamingConventionTransformer nameTransformer,
                                        final String bulkFileFormatName,
                                        final String bulkFilePropertyNameInRecord) {
    super(nameTransformer);
    this.bulkLoadFileFormatName = bulkFileFormatName;
    this.bulkLoadStageName = bulkFilePropertyNameInRecord;
  }

  public void initialize(final JsonNode config) {
    this.bulkLoadFileFormatName = config.get(BULK_LOAD_FILE_FORMAT).asText();
    this.bulkLoadFilePropertyNameInRecord = config.get(BULK_LOAD_S3_STAGES).asText();
    this.bulkLoadFilesList.clear();
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
        appendBulkLoadFiles(recordsData);
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

  private List<String> appendBulkLoadFiles(final SerializableBuffer recordsData) {
    final List<String> filesListFromRecords = new ArrayList<>();
    // Get the list of files from each items in the recordsData 'files' field:
    // Declare the csvFile
    try {
      String csvFilePath = recordsData.getFile().getAbsolutePath();
      Reader reader = new FileReader(csvFilePath);
      CSVParser parser = new CSVParser(reader, CSVFormat.DEFAULT);

      // Iterate through the CSV records
      for (CSVRecord record : parser) {
        // Access individual fields by index or header name
        String bulkLoadFilePath = record.get(this.bulkLoadFilePropertyNameInRecord);
        System.out.println("Found file path: " + bulkLoadFilePath);
        this.bulkLoadFilesList.add(bulkLoadFilePath);
      }
      parser.close();
      reader.close();
    } catch (Exception e) {
      e.printStackTrace();
    }
    return filesListFromRecords;
  }

  private void bulkUploadRecordFilesToSecondaryTable(
                                                     final JdbcDatabase database,
                                                     final String stageName,
                                                     final List<String> filesList,
                                                     final String tableName,
                                                     final String schemaName)
      throws SQLException {
    try {
      final String query = getCopyQuery(stageName, filesList, tableName, schemaName, this.bulkLoadFileFormatName);
      LOGGER.debug("Executing query: {}", query);
      database.execute(query);
    } catch (final SQLException e) {
      throw checkForKnownConfigExceptions(e).orElseThrow(() -> e);
    }
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
      bulkUploadRecordFilesToSecondaryTable(database, this.bulkLoadStageName, this.bulkLoadFilesList, tableName + "_bulk", schemaName);
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
