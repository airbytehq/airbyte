/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import io.airbyte.integrations.destination.s3.csv.S3CsvWriter;
import io.airbyte.integrations.destination.s3.writer.S3Writer;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.IOException;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class S3StreamCopier implements StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3StreamCopier.class);

  private static final int DEFAULT_UPLOAD_THREADS = 10; // The S3 cli uses 10 threads by default.
  private static final int DEFAULT_QUEUE_CAPACITY = DEFAULT_UPLOAD_THREADS;
  // 4 * 256MiB (see CopyConsumerFactory#MAX_BATCH_SIZE_BYTES) = 1GiB, which redshift wants
  // https://docs.aws.amazon.com/redshift/latest/dg/t_loading-tables-from-s3.html "Split your load data files so that the files are about equal size, between 1 MB and 1 GB after compression"
  public static final int MAX_PARTS_PER_FILE = 4;

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
  private final Map<String, S3Writer> stagingWritersBySuffix = new HashMap<>();


  // The number of batches of records that will be inserted into each file.
  private final int maxPartsPerFile;
  // The number of batches inserted into the current file.
  private int partsAddedToCurrentFile;
  private String currentFile;

  public S3StreamCopier(final String stagingFolder,
                        final String schema,
                        final AmazonS3 client,
                        final JdbcDatabase db,
                        final S3DestinationConfig s3Config,
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
    this.s3Config = s3Config;

    this.maxPartsPerFile = maxPartsPerFile;
    this.partsAddedToCurrentFile = maxPartsPerFile - 1; // Force a new file on the first call to prepareStagingFile()
  }

  /*
   * old behavior: create s3://bucket/randomUuid/(namespace|schemaName)/generatedFilename
   * S3CsvWriter: create s3://bucket/bucketPath(/namespace)?/streamName/time_generatedSuffix.csv
   */
  @Override
  public String prepareStagingFile() {
    partsAddedToCurrentFile = (partsAddedToCurrentFile + 1) % maxPartsPerFile;
    if (partsAddedToCurrentFile == 0) {
      LOGGER.info("S3 upload part size: {} MB", s3Config.getPartSize());

      try {
        final S3CsvWriter writer = new S3CsvWriter(
            s3Config.cloneWithFormatConfig(new S3CsvFormatConfig(Flattening.NO, (long) s3Config.getPartSize())),
            s3Client,
            configuredAirbyteStream,
            uploadTime,
            DEFAULT_UPLOAD_THREADS,
            DEFAULT_QUEUE_CAPACITY,
            "arst" // TODO remove
        );
        currentFile = writer.getObjectKey();
        stagingWritersBySuffix.put(currentFile, writer);
      } catch (final IOException e) {
        throw new RuntimeException(e);
      }
    }
    return currentFile;
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage, final String suffix) throws Exception {
    if (stagingWritersBySuffix.containsKey(suffix)) {
      stagingWritersBySuffix.get(suffix).write(id, recordMessage);
    }
  }

  @Override
  public void closeStagingUploader(final boolean hasFailed) throws Exception {
    for (final S3Writer writer : stagingWritersBySuffix.values()) {
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
    for (final Map.Entry<String, S3Writer> entry : stagingWritersBySuffix.entrySet()) {
      final String objectKey = entry.getValue().getObjectKey();
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
    for (final Map.Entry<String, S3Writer> entry : stagingWritersBySuffix.entrySet()) {
      final String suffix = entry.getKey();
      final String objectKey = entry.getValue().getObjectKey();

      LOGGER.info("Begin cleaning s3 staging file {}.", objectKey);
      if (s3Client.doesObjectExist(s3Config.getBucketName(), objectKey)) {
        s3Client.deleteObject(s3Config.getBucketName(), objectKey);
      }
      LOGGER.info("S3 staging file {} cleaned.", suffix);
    }

    LOGGER.info("Begin cleaning {} tmp table in destination.", tmpTableName);
    sqlOperations.dropTableIfExists(db, schemaName, tmpTableName);
    LOGGER.info("{} tmp table in destination cleaned.", tmpTableName);
  }

  protected static String getFullS3Path(final String s3BucketName, final String s3StagingFile) {
    return String.join("/", "s3:/", s3BucketName, s3StagingFile);
  }

  public abstract void copyS3CsvFileIntoTable(JdbcDatabase database,
                                              String s3FileLocation,
                                              String schema,
                                              String tableName,
                                              S3DestinationConfig s3Config)
      throws SQLException;

}
