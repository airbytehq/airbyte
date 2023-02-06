/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.gcs;

import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.WriteChannel;
import com.google.cloud.storage.BlobId;
import com.google.cloud.storage.BlobInfo;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.StagingFilenameGenerator;
import io.airbyte.integrations.destination.jdbc.constants.GlobalDataSizeConstants;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.nio.channels.Channels;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class GcsStreamCopier implements StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsStreamCopier.class);
  // It is optimal to write every 10,000,000 records (BATCH_SIZE * MAX_PER_FILE_PART_COUNT) to a new
  // file.
  // The BATCH_SIZE is defined in CopyConsumerFactory.
  // The average size of such a file will be about 1 GB.
  // This will make it easier to work with files and speed up the recording of large amounts of data.
  // In addition, for a large number of records, we will not get a drop in the copy request to
  // QUERY_TIMEOUT when
  // the records from the file are copied to the staging table.
  public static final int MAX_PARTS_PER_FILE = 1000;
  protected final GcsConfig gcsConfig;
  protected final String tmpTableName;
  protected final String schemaName;
  protected final String streamName;
  protected final JdbcDatabase db;
  protected final Set<String> gcsStagingFiles = new HashSet<>();
  protected final String stagingFolder;
  protected StagingFilenameGenerator filenameGenerator;
  private final Storage storageClient;
  private final DestinationSyncMode destSyncMode;
  private final ExtendedNameTransformer nameTransformer;
  private final SqlOperations sqlOperations;
  private final HashMap<String, WriteChannel> channels = new HashMap<>();
  private final HashMap<String, CSVPrinter> csvPrinters = new HashMap<>();

  public GcsStreamCopier(final String stagingFolder,
                         final DestinationSyncMode destSyncMode,
                         final String schema,
                         final String streamName,
                         final Storage storageClient,
                         final JdbcDatabase db,
                         final GcsConfig gcsConfig,
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
    this.storageClient = storageClient;
    this.gcsConfig = gcsConfig;
    this.filenameGenerator = new StagingFilenameGenerator(streamName, GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES);
  }

  private String prepareGcsStagingFile() {
    return String.join("/", stagingFolder, schemaName, filenameGenerator.getStagingFilename());
  }

  @Override
  public String prepareStagingFile() {
    final var name = prepareGcsStagingFile();
    if (!gcsStagingFiles.contains(name)) {
      gcsStagingFiles.add(name);
      final var blobId = BlobId.of(gcsConfig.getBucketName(), name);
      final var blobInfo = BlobInfo.newBuilder(blobId).build();
      final var blob = storageClient.create(blobInfo);
      final var channel = blob.writer();
      channels.put(name, channel);
      final OutputStream outputStream = Channels.newOutputStream(channel);

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
  public void write(final UUID id, final AirbyteRecordMessage recordMessage, final String gcsFileName) throws Exception {
    if (csvPrinters.containsKey(gcsFileName)) {
      csvPrinters.get(gcsFileName).printRecord(id,
          Jsons.serialize(recordMessage.getData()),
          Timestamp.from(Instant.ofEpochMilli(recordMessage.getEmittedAt())));
    }
  }

  @Override
  public void closeNonCurrentStagingFileWriters() throws Exception {
    // TODO need to update this method when updating whole class for using GcsWriter
  }

  @Override
  public void closeStagingUploader(final boolean hasFailed) throws Exception {
    LOGGER.info("Uploading remaining data for {} stream.", streamName);
    for (final var csvPrinter : csvPrinters.values()) {
      csvPrinter.close();
    }
    for (final var channel : channels.values()) {
      channel.close();
    }
    LOGGER.info("All data for {} stream uploaded.", streamName);
  }

  @Override
  public void copyStagingFileToTemporaryTable() throws Exception {
    LOGGER.info("Starting copy to tmp table: {} in destination for stream: {}, schema: {}.", tmpTableName, streamName, schemaName);
    for (final var gcsStagingFile : gcsStagingFiles) {
      copyGcsCsvFileIntoTable(db, getFullGcsPath(gcsConfig.getBucketName(), gcsStagingFile), schemaName, tmpTableName, gcsConfig);
    }
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  @Override
  public void removeFileAndDropTmpTable() throws Exception {
    for (final var gcsStagingFile : gcsStagingFiles) {
      LOGGER.info("Begin cleaning gcs staging file {}.", gcsStagingFile);
      final var blobId = BlobId.of(gcsConfig.getBucketName(), gcsStagingFile);
      if (storageClient.get(blobId).exists()) {
        storageClient.delete(blobId);
      }
      LOGGER.info("GCS staging file {} cleaned.", gcsStagingFile);
    }

    LOGGER.info("Begin cleaning {} tmp table in destination.", tmpTableName);
    sqlOperations.dropTableIfExists(db, schemaName, tmpTableName);
    LOGGER.info("{} tmp table in destination cleaned.", tmpTableName);
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
  public String createDestinationTable() throws Exception {
    final var destTableName = nameTransformer.getRawTableName(streamName);
    LOGGER.info("Preparing table {} in destination.", destTableName);
    sqlOperations.createTableIfNotExists(db, schemaName, destTableName);
    LOGGER.info("Table {} in destination prepared.", tmpTableName);

    return destTableName;
  }

  @Override
  public String generateMergeStatement(final String destTableName) throws Exception {
    LOGGER.info("Preparing to merge tmp table {} to dest table: {}, schema: {}, in destination.", tmpTableName, destTableName, schemaName);
    final var queries = new StringBuilder();
    if (destSyncMode.equals(DestinationSyncMode.OVERWRITE)) {
      queries.append(sqlOperations.truncateTableQuery(db, schemaName, destTableName));
      LOGGER.info("Destination OVERWRITE mode detected. Dest table: {}, schema: {}, will be truncated.", destTableName, schemaName);
    }
    queries.append(sqlOperations.insertTableQuery(db, schemaName, tmpTableName, destTableName));
    return queries.toString();
  }

  @Override
  public String getCurrentFile() {
    // TODO need to update this method when updating whole class for using GcsWriter
    return null;
  }

  private static String getFullGcsPath(final String bucketName, final String stagingFile) {
    // this is intentionally gcs:/ not gcs:// since the join adds the additional slash
    return String.join("/", "gcs:/", bucketName, stagingFile);
  }

  public static void attemptWriteToPersistence(final GcsConfig gcsConfig) throws IOException {
    final String outputTableName = "_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", "");
    attemptWriteAndDeleteGcsObject(gcsConfig, outputTableName);
  }

  private static void attemptWriteAndDeleteGcsObject(final GcsConfig gcsConfig, final String outputTableName) throws IOException {
    final var storage = getStorageClient(gcsConfig);
    final var blobId = BlobId.of(gcsConfig.getBucketName(), "check-content/" + outputTableName);
    final var blobInfo = BlobInfo.newBuilder(blobId).build();

    storage.create(blobInfo, "".getBytes(StandardCharsets.UTF_8));
    storage.delete(blobId);
  }

  public static Storage getStorageClient(final GcsConfig gcsConfig) throws IOException {
    final InputStream credentialsInputStream = new ByteArrayInputStream(gcsConfig.getCredentialsJson().getBytes(StandardCharsets.UTF_8));
    final GoogleCredentials credentials = GoogleCredentials.fromStream(credentialsInputStream);
    return StorageOptions.newBuilder()
        .setCredentials(credentials)
        .setProjectId(gcsConfig.getProjectId())
        .build()
        .getService();
  }

  @VisibleForTesting
  public String getTmpTableName() {
    return tmpTableName;
  }

  @VisibleForTesting
  public Set<String> getGcsStagingFiles() {
    return gcsStagingFiles;
  }

  public abstract void copyGcsCsvFileIntoTable(JdbcDatabase database,
                                               String gcsFileLocation,
                                               String schema,
                                               String tableName,
                                               GcsConfig gcsConfig)
      throws SQLException;

}
