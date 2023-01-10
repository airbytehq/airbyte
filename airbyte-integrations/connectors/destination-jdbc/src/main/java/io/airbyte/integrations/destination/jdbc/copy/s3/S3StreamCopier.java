/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import com.amazonaws.services.s3.AmazonS3;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvWriter;
import io.airbyte.integrations.destination.s3.csv.StagingDatabaseCsvSheetGenerator;
import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.integrations.destination.s3.writer.DestinationFileWriter;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.IOException;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class S3StreamCopier implements StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3StreamCopier.class);

  private static final int DEFAULT_UPLOAD_THREADS = 10; // The S3 cli uses 10 threads by default.
  private static final int DEFAULT_QUEUE_CAPACITY = DEFAULT_UPLOAD_THREADS;

  protected final AmazonS3 s3Client;
  protected final S3DestinationConfig s3Config;
  protected final String tmpTableName;
  protected final String schemaName;
  protected final String streamName;
  protected final JdbcDatabase db;
  protected final ConfiguredAirbyteStream configuredAirbyteStream;
  protected final String stagingFolder;
  protected final Map<String, DestinationFileWriter> stagingWritersByFile = new HashMap<>();
  private final DestinationSyncMode destSyncMode;
  private final ExtendedNameTransformer nameTransformer;
  private final SqlOperations sqlOperations;
  private final Timestamp uploadTime;
  protected final Set<String> activeStagingWriterFileNames = new HashSet<>();
  protected final Set<String> stagingFileNames = new LinkedHashSet<>();
  private final boolean purgeStagingData;

  // The number of batches of records that will be inserted into each file.
  private final int maxPartsPerFile;
  // The number of batches inserted into the current file.
  private int partsAddedToCurrentFile;
  private String currentFile;

  public S3StreamCopier(final String stagingFolder,
                        final String schema,
                        final AmazonS3 client,
                        final JdbcDatabase db,
                        final S3CopyConfig config,
                        final ExtendedNameTransformer nameTransformer,
                        final SqlOperations sqlOperations,
                        final ConfiguredAirbyteStream configuredAirbyteStream,
                        final Timestamp uploadTime,
                        final int maxPartsPerFile) {
    this.destSyncMode = configuredAirbyteStream.getDestinationSyncMode();
    this.schemaName = schema;
    this.streamName = configuredAirbyteStream.getStream().getName();
    this.stagingFolder = stagingFolder;
    this.db = db;
    this.nameTransformer = nameTransformer;
    this.sqlOperations = sqlOperations;
    this.configuredAirbyteStream = configuredAirbyteStream;
    this.uploadTime = uploadTime;
    this.tmpTableName = nameTransformer.getTmpTableName(this.streamName);
    this.s3Client = client;
    this.s3Config = config.s3Config();
    this.purgeStagingData = config.purgeStagingData();

    this.maxPartsPerFile = maxPartsPerFile;
    this.partsAddedToCurrentFile = 0;
  }

  @Override
  public String prepareStagingFile() {
    if (partsAddedToCurrentFile == 0) {

      try {
        // The Flattening value is actually ignored, because we pass an explicit CsvSheetGenerator. So just
        // pass in null.
        final S3FormatConfig csvFormatConfig = new S3CsvFormatConfig(null, CompressionType.NO_COMPRESSION);
        final S3DestinationConfig writerS3Config = S3DestinationConfig.create(s3Config).withFormatConfig(csvFormatConfig).get();
        final S3CsvWriter writer = new S3CsvWriter.Builder(
            writerS3Config,
            s3Client,
            configuredAirbyteStream,
            uploadTime)
                .uploadThreads(DEFAULT_UPLOAD_THREADS)
                .queueCapacity(DEFAULT_QUEUE_CAPACITY)
                .csvSettings(CSVFormat.DEFAULT)
                .withHeader(false)
                .csvSheetGenerator(new StagingDatabaseCsvSheetGenerator())
                .build();
        currentFile = writer.getOutputPath();
        stagingWritersByFile.put(currentFile, writer);
        activeStagingWriterFileNames.add(currentFile);
        stagingFileNames.add(currentFile);
      } catch (final IOException e) {
        throw new RuntimeException(e);
      }
    }
    partsAddedToCurrentFile = (partsAddedToCurrentFile + 1) % maxPartsPerFile;
    return currentFile;
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage, final String filename) throws Exception {
    if (stagingWritersByFile.containsKey(filename)) {
      stagingWritersByFile.get(filename).write(id, recordMessage);
    }
  }

  @Override
  public void closeNonCurrentStagingFileWriters() throws Exception {
    final Set<String> removedKeys = new HashSet<>();
    for (final String key : activeStagingWriterFileNames) {
      if (!key.equals(currentFile)) {
        stagingWritersByFile.get(key).close(false);
        stagingWritersByFile.remove(key);
        removedKeys.add(key);
      }
    }
    activeStagingWriterFileNames.removeAll(removedKeys);
  }

  @Override
  public void closeStagingUploader(final boolean hasFailed) throws Exception {
    for (final DestinationFileWriter writer : stagingWritersByFile.values()) {
      writer.close(hasFailed);
    }
  }

  @Override
  public void createDestinationSchema() throws Exception {
    LOGGER.info("Creating schema in destination if it doesn't exist: {}", schemaName);
    sqlOperations.createSchemaIfNotExists(db, schemaName);
  }

  @Override
  public void createTemporaryTable() throws Exception {
    LOGGER.info("Preparing tmp table in destination for stream: {}, schema: {}, tmp table name: {}.", streamName, schemaName, tmpTableName);
    sqlOperations.createTableIfNotExists(db, schemaName, tmpTableName);
  }

  @Override
  public void copyStagingFileToTemporaryTable() throws Exception {
    LOGGER.info("Starting copy to tmp table: {} in destination for stream: {}, schema: {}, .", tmpTableName, streamName, schemaName);
    for (final String fileName : stagingFileNames) {
      copyS3CsvFileIntoTable(db, getFullS3Path(s3Config.getBucketName(), fileName), schemaName, tmpTableName, s3Config);
    }
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  @Override
  public String createDestinationTable() throws Exception {
    final var destTableName = nameTransformer.getRawTableName(streamName);
    LOGGER.info("Preparing table {} in destination.", destTableName);
    sqlOperations.createTableIfNotExists(db, schemaName, destTableName);
    LOGGER.info("Table {} in destination prepared.", tmpTableName);

    return destTableName;
  }

  @Override
  public String generateMergeStatement(final String destTableName) {
    LOGGER.info("Preparing to merge tmp table {} to dest table: {}, schema: {}, in destination.", tmpTableName, destTableName, schemaName);
    final var queries = new StringBuilder();
    if (destSyncMode.equals(DestinationSyncMode.OVERWRITE)) {
      queries.append(sqlOperations.truncateTableQuery(db, schemaName, destTableName));
      LOGGER.info("Destination OVERWRITE mode detected. Dest table: {}, schema: {}, truncated.", destTableName, schemaName);
    }
    queries.append(sqlOperations.insertTableQuery(db, schemaName, tmpTableName, destTableName));
    return queries.toString();
  }

  @Override
  public void removeFileAndDropTmpTable() throws Exception {
    if (purgeStagingData) {
      for (final String fileName : stagingFileNames) {
        s3Client.deleteObject(s3Config.getBucketName(), fileName);
        LOGGER.info("S3 staging file {} cleaned.", fileName);
      }
    }

    LOGGER.info("Begin cleaning {} tmp table in destination.", tmpTableName);
    sqlOperations.dropTableIfExists(db, schemaName, tmpTableName);
    LOGGER.info("{} tmp table in destination cleaned.", tmpTableName);
  }

  @Override
  public String getCurrentFile() {
    return currentFile;
  }

  protected static String getFullS3Path(final String s3BucketName, final String s3StagingFile) {
    return String.join("/", "s3:/", s3BucketName, s3StagingFile);
  }

  @VisibleForTesting
  public String getTmpTableName() {
    return tmpTableName;
  }

  @VisibleForTesting
  public Map<String, DestinationFileWriter> getStagingWritersByFile() {
    return stagingWritersByFile;
  }

  @VisibleForTesting
  public Set<String> getStagingFiles() {
    return stagingFileNames;
  }

  public abstract void copyS3CsvFileIntoTable(JdbcDatabase database,
                                              String s3FileLocation,
                                              String schema,
                                              String tableName,
                                              S3DestinationConfig s3Config)
      throws SQLException;

}
