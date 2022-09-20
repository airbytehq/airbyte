/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static org.apache.logging.log4j.util.Strings.EMPTY;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3CopyConfig;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.util.S3OutputPathHelper;
import io.airbyte.integrations.destination.s3.writer.S3WriterFactory;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;

import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.HashSet;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This implementation extends {@link S3StreamCopier}. It bypasses some steps,
 * because databricks is able to load multiple staging files at once
 * <p>
 * </p>
 * It does the following operations:
 * <ul>
 * <li>1. {@link S3StreamCopier} writes CSV files in
 * s3://bucket-name/bucket-path/schema-name/stream-name .</li>
 * <li>2. Create a destination table with location s3://bucket-name/bucket-path/delta_tables/schema-name/stream-name </li>
 * <li>4. Copy the staging CSV files into the destination delta table.</li>
 * <li>5. Let the {@link S3StreamCopier} handle the files deleting </li>
 * </ul>
 */
public class DatabricksStreamCopier extends S3StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksStreamCopier.class);

  private final String schemaName;
  private final String streamName;
  private final DestinationSyncMode destinationSyncMode;
  private final S3DestinationConfig s3Config;
  private final JdbcDatabase database;
  private final DatabricksSqlOperations sqlOperations;

  private final String tmpTableName;
  private final String destTableName;
  private String tmpTableLocation;
  private final String destTableLocation;
  private final Set<String> filenames = new HashSet<>();

  public DatabricksStreamCopier(final String stagingFolder,
      final String schema,
      final ConfiguredAirbyteStream configuredStream,
      final AmazonS3 s3Client,
      final JdbcDatabase database,
      final DatabricksDestinationConfig databricksConfig,
      final ExtendedNameTransformer nameTransformer,
      final SqlOperations sqlOperations,
      final S3WriterFactory writerFactory,
      final Timestamp uploadTime,
      final S3CopyConfig copyConfig)
      throws Exception {
    super(stagingFolder, schema, s3Client, database, copyConfig, nameTransformer, sqlOperations, configuredStream,
        uploadTime, 10);
    this.schemaName = schema;
    this.streamName = configuredStream.getStream().getName();
    this.destinationSyncMode = configuredStream.getDestinationSyncMode();
    this.s3Config = databricksConfig.getS3DestinationConfig();
    this.database = database;
    this.sqlOperations = (DatabricksSqlOperations) sqlOperations;

    this.tmpTableName = nameTransformer.getTmpTableName(streamName);
    this.destTableName = nameTransformer.getRawTableName(streamName);
    this.tmpTableLocation = getFullS3Path(s3Config.getBucketName(), S3OutputPathHelper.getOutputPrefix(s3Config.getBucketPath(), configuredStream.getStream()));
    this.destTableLocation = String.format("s3://%s/%s/%s/%s/%s",
        s3Config.getBucketName(), s3Config.getBucketPath(), "delta_tables", schemaName, streamName);
    LOGGER.info("[Stream {}] Database schema: {}", streamName, schemaName);
    LOGGER.info("[Stream {}] Data table {} location: {}", streamName, destTableName, destTableLocation);
  }

  @Override
  public String prepareStagingFile() {
    final String file = super.prepareStagingFile();
    
    this.filenames.add(file);

    LOGGER.info("[Stream {}] File {} location: {}", streamName, tmpTableName,
        getFullS3Path(s3Config.getBucketName(), file));

    return file;
  }

  @Override
  public void createDestinationSchema() throws Exception {
    LOGGER.info("[Stream {}] Creating database schema if it does not exist: {}", streamName, schemaName);
    sqlOperations.createSchemaIfNotExists(database, schemaName);
  }

  @Override
  public void createTemporaryTable() throws Exception {
    // The dest table is created directly based on the staging file. So no separate
    // copying step is needed.
  }

  @Override
  public void copyStagingFileToTemporaryTable() {
    // The dest table is created directly based on the staging file. So no separate
    // copying step is needed.
  }

  /**
   * Creates a destination raw table with the specified location
   */
  @Override
  public String createDestinationTable() throws Exception {
    LOGGER.info("[Stream {}] Creating destination table if it does not exist: {}", streamName, destTableName);

    final String createStatement = destinationSyncMode == DestinationSyncMode.OVERWRITE
        // "create or replace" is the recommended way to replace existing table
        ? "CREATE OR REPLACE TABLE"
        : "CREATE TABLE IF NOT EXISTS";

    final String createTable = String.format(
        "%s %s.%s (%s STRING, %s STRING, %s TIMESTAMP) " +
            "COMMENT 'Created from stream %s' " +
            "TBLPROPERTIES ('airbyte.destinationSyncMode' = '%s', %s) ",
        createStatement,
        schemaName, destTableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
        streamName,
        destinationSyncMode.value(),
        String.join(", ", DatabricksConstants.DEFAULT_TBL_PROPERTIES));
    LOGGER.info(createTable);
    database.execute(createTable);

    return destTableName;
  }

  /**
   * Overrides the global generateMergeStatement in order to 
   * copy the staging data directly into the dest table
   */
  @Override
  public String generateMergeStatement(final String destTableName) {
    if (filenames.size() == 0) {
      LOGGER.info("[Stream: {}] No data to be written", streamName, destTableName);
      // Need to by pass merge if empty stream
      return "SELECT 0";
    }
    final String copyData = String.format(
        "COPY INTO %s.%s " +
            "FROM (SELECT _c0 as %s, _c1 as %s, _c2::TIMESTAMP as %s FROM '%s') " +
            "FILEFORMAT = CSV " +
            "FILES = (%s) " +
            "FORMAT_OPTIONS('quote' = '\"', 'escape' = '\"', 'enforceSchema' = 'false', 'multiLine' = 'true', 'header' = 'false', 'unescapedQuoteHandling' = 'STOP_AT_CLOSING_QUOTE')",
        schemaName, destTableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
        this.tmpTableLocation,
        String.join(",", filenames.stream().map(elem -> {
          final String[] uriParts = elem.split("/");
          return String.format("'%s'", uriParts[uriParts.length - 1]);
        }).toList()));
    LOGGER.info(copyData);
    return copyData;
  }

  public void copyS3CsvFileIntoTable(JdbcDatabase database,
      String s3FileLocation,
      String schema,
      String tableName,
      S3DestinationConfig s3Config) throws SQLException {
        // Needed to implement it for S3StreamCopier
        // Everything is handled in generateMergeStatement, since we just need to do one big copy with all the files
  }
}
