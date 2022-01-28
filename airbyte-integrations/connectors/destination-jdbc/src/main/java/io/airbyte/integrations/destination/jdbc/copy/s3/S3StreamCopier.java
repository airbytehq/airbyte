/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import com.amazonaws.services.s3.AmazonS3;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvWriter;
import io.airbyte.integrations.destination.s3.csv.StagingDatabaseCsvSheetGenerator;
import io.airbyte.integrations.destination.s3.writer.DestinationFileWriter;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.IOException;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.HashMap;
import java.util.Map;
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
  private final DestinationSyncMode destSyncMode;
  protected final String schemaName;
  protected final String streamName;
  protected final JdbcDatabase db;
  private final ExtendedNameTransformer nameTransformer;
  private final SqlOperations sqlOperations;
  private final ConfiguredAirbyteStream configuredAirbyteStream;
  private final Timestamp uploadTime;
  protected final String stagingFolder;
  protected final Map<String, DestinationFileWriter> stagingWritersByFile = new HashMap<>();
  private final boolean purgeStagingData;

  // The number of batches of records that will be inserted into each file.
  private final int maxPartsPerFile;
  // The number of batches inserted into the current file.
  private int partsAddedToCurrentFile;
  private String currentFile;

  /**
   * @param maxPartsPerFile The number of "chunks" of requests to add into each file. Each chunk can
   *        be up to 256 MiB (see CopyConsumerFactory#MAX_BATCH_SIZE_BYTES). For example, Redshift
   *        recommends at most 1 GiB per file, so you would want maxPartsPerFile = 4 (because 4 *
   *        256MiB = 1 GiB).
   *        {@link io.airbyte.integrations.destination.jdbc.constants.GlobalDataSizeConstants#DEFAULT_MAX_BATCH_SIZE_BYTES}
   */
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
      LOGGER.info("S3 upload part size: {} MB", s3Config.getPartSize());

      try {
        final S3CsvWriter writer = new S3CsvWriter.Builder(
            // The Flattening value is actually ignored, because we pass an explicit CsvSheetGenerator. So just
            // pass in null.
            s3Config.cloneWithFormatConfig(new S3CsvFormatConfig(null, (long) s3Config.getPartSize())),
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
    for (final Map.Entry<String, DestinationFileWriter> entry : stagingWritersByFile.entrySet()) {
      final String objectKey = entry.getValue().getOutputPath();
      copyS3CsvFileIntoTable(db, getFullS3Path(s3Config.getBucketName(), objectKey), schemaName, tmpTableName, s3Config);
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
    queries.append(sqlOperations.copyTableQuery(db, schemaName, tmpTableName, destTableName));
    return queries.toString();
  }

  @Override
  public void removeFileAndDropTmpTable() throws Exception {
    if (purgeStagingData) {
      for (final Map.Entry<String, DestinationFileWriter> entry : stagingWritersByFile.entrySet()) {
        final String suffix = entry.getKey();
        final String objectKey = entry.getValue().getOutputPath();

        LOGGER.info("Begin cleaning s3 staging file {}.", objectKey);
        if (s3Client.doesObjectExist(s3Config.getBucketName(), objectKey)) {
          s3Client.deleteObject(s3Config.getBucketName(), objectKey);
        }
        LOGGER.info("S3 staging file {} cleaned.", suffix);
      }
    }

    LOGGER.info("Begin cleaning {} tmp table in destination.", tmpTableName);
    sqlOperations.dropTableIfExists(db, schemaName, tmpTableName);
    LOGGER.info("{} tmp table in destination cleaned.", tmpTableName);
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

  public abstract void copyS3CsvFileIntoTable(JdbcDatabase database,
                                              String s3FileLocation,
                                              String schema,
                                              String tableName,
                                              S3DestinationConfig s3Config)
      throws SQLException;

}
