/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.StagingFilenameGenerator;
import io.airbyte.integrations.destination.jdbc.constants.GlobalDataSizeConstants;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * @deprecated See {@link S3StreamCopier}
 */
@Deprecated
public abstract class LegacyS3StreamCopier implements StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(LegacyS3StreamCopier.class);

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
  protected final Set<String> s3StagingFiles = new HashSet<>();
  private final Map<String, StreamTransferManager> multipartUploadManagers = new HashMap<>();
  private final Map<String, MultiPartOutputStream> outputStreams = new HashMap<>();
  private final Map<String, CSVPrinter> csvPrinters = new HashMap<>();
  protected final String stagingFolder;
  private final StagingFilenameGenerator filenameGenerator;

  public LegacyS3StreamCopier(final String stagingFolder,
                              final DestinationSyncMode destSyncMode,
                              final String schema,
                              final String streamName,
                              final AmazonS3 client,
                              final JdbcDatabase db,
                              final S3DestinationConfig s3Config,
                              final ExtendedNameTransformer nameTransformer,
                              final SqlOperations sqlOperations) {
    this.destSyncMode = destSyncMode;
    this.schemaName = schema;
    this.streamName = streamName;
    this.stagingFolder = stagingFolder;
    this.db = db;
    this.nameTransformer = nameTransformer;
    this.sqlOperations = sqlOperations;
    this.tmpTableName = nameTransformer.getTmpTableName(streamName);
    this.s3Client = client;
    this.s3Config = s3Config;
    this.filenameGenerator = new StagingFilenameGenerator(streamName, GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES);
  }

  private String prepareS3StagingFile() {
    return String.join("/", stagingFolder, schemaName, filenameGenerator.getStagingFilename());
  }

  @Override
  public String prepareStagingFile() {
    final var name = prepareS3StagingFile();
    if (!s3StagingFiles.contains(name)) {
      s3StagingFiles.add(name);
      LOGGER.info("S3 upload part size: {} MB", s3Config.getPartSize());
      // The stream transfer manager lets us greedily stream into S3. The native AWS SDK does not
      // have support for streaming multipart uploads;
      // The alternative is first writing the entire output to disk before loading into S3. This is not
      // feasible with large tables.
      // Data is chunked into parts. A part is sent off to a queue to be uploaded once it has reached it's
      // configured part size.
      // Memory consumption is (numUploadThreads + queue capacity) * part size = (10 + 10) * 10 = 200 MB
      // at current configurations.
      final var manager = new StreamTransferManager(s3Config.getBucketName(), name, s3Client)
          .numUploadThreads(DEFAULT_UPLOAD_THREADS)
          .queueCapacity(DEFAULT_QUEUE_CAPACITY)
          .partSize(s3Config.getPartSize());
      multipartUploadManagers.put(name, manager);
      final var outputStream = manager.getMultiPartOutputStreams().get(0);
      // We only need one output stream as we only have one input stream. This is reasonably performant.
      // See the above comment.
      outputStreams.put(name, outputStream);
      final var writer = new PrintWriter(outputStream, true, StandardCharsets.UTF_8);
      try {
        csvPrinters.put(name, new CSVPrinter(writer, CSVFormat.DEFAULT));
      } catch (final IOException e) {
        throw new RuntimeException(e);
      }
    }
    return name;
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage, final String s3FileName) throws Exception {
    if (csvPrinters.containsKey(s3FileName)) {
      csvPrinters.get(s3FileName).printRecord(id,
          Jsons.serialize(recordMessage.getData()),
          Timestamp.from(Instant.ofEpochMilli(recordMessage.getEmittedAt())));
    }
  }

  @Override
  public void closeStagingUploader(final boolean hasFailed) throws Exception {
    if (hasFailed) {
      for (final var multipartUploadManager : multipartUploadManagers.values()) {
        multipartUploadManager.abort();
      }
    }
    closeAndWaitForUpload();
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
    s3StagingFiles.forEach(s3StagingFile -> Exceptions.toRuntime(() -> {
      copyS3CsvFileIntoTable(db, getFullS3Path(s3Config.getBucketName(), s3StagingFile), schemaName, tmpTableName, s3Config);
    }));
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
    s3StagingFiles.forEach(s3StagingFile -> {
      LOGGER.info("Begin cleaning s3 staging file {}.", s3StagingFile);
      if (s3Client.doesObjectExist(s3Config.getBucketName(), s3StagingFile)) {
        s3Client.deleteObject(s3Config.getBucketName(), s3StagingFile);
      }
      LOGGER.info("S3 staging file {} cleaned.", s3StagingFile);
    });

    LOGGER.info("Begin cleaning {} tmp table in destination.", tmpTableName);
    sqlOperations.dropTableIfExists(db, schemaName, tmpTableName);
    LOGGER.info("{} tmp table in destination cleaned.", tmpTableName);
  }

  protected static String getFullS3Path(final String s3BucketName, final String s3StagingFile) {
    return String.join("/", "s3:/", s3BucketName, s3StagingFile);
  }

  /**
   * Closes the printers/outputstreams and waits for any buffered uploads to complete.
   */
  private void closeAndWaitForUpload() throws IOException {
    LOGGER.info("Uploading remaining data for {} stream.", streamName);
    for (final var csvPrinter : csvPrinters.values()) {
      csvPrinter.close();
    }
    for (final var outputStream : outputStreams.values()) {
      outputStream.close();
    }
    for (final var multipartUploadManager : multipartUploadManagers.values()) {
      multipartUploadManager.complete();
    }
    LOGGER.info("All data for {} stream uploaded.", streamName);
  }

  public abstract void copyS3CsvFileIntoTable(JdbcDatabase database,
                                              String s3FileLocation,
                                              String schema,
                                              String tableName,
                                              S3DestinationConfig s3Config)
      throws SQLException;

}
