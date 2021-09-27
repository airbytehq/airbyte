/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.gcs;

import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.WriteChannel;
import com.google.cloud.storage.BlobId;
import com.google.cloud.storage.BlobInfo;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.DestinationSyncMode;
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

  private final Storage storageClient;
  private final GcsConfig gcsConfig;
  private final String tmpTableName;
  private final DestinationSyncMode destSyncMode;
  private final String schemaName;
  private final String streamName;
  private final JdbcDatabase db;
  private final ExtendedNameTransformer nameTransformer;
  private final SqlOperations sqlOperations;
  private final Set<String> gcsStagingFiles = new HashSet<>();
  private final HashMap<String, WriteChannel> channels = new HashMap<>();
  private final HashMap<String, CSVPrinter> csvPrinters = new HashMap<>();
  private final String stagingFolder;

  public GcsStreamCopier(String stagingFolder,
                         DestinationSyncMode destSyncMode,
                         String schema,
                         String streamName,
                         Storage storageClient,
                         JdbcDatabase db,
                         GcsConfig gcsConfig,
                         ExtendedNameTransformer nameTransformer,
                         SqlOperations sqlOperations) {
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
  }

  private String prepareGcsStagingFile() {
    return String.join("/", stagingFolder, schemaName, Strings.addRandomSuffix("", "", 3) + "_" + streamName);
  }

  @Override
  public String prepareStagingFile() {
    var name = prepareGcsStagingFile();
    gcsStagingFiles.add(name);
    var blobId = BlobId.of(gcsConfig.getBucketName(), name);
    var blobInfo = BlobInfo.newBuilder(blobId).build();
    var blob = storageClient.create(blobInfo);
    var channel = blob.writer();
    channels.put(name, channel);
    OutputStream outputStream = Channels.newOutputStream(channel);

    var writer = new PrintWriter(outputStream, true, StandardCharsets.UTF_8);
    try {
      csvPrinters.put(name, new CSVPrinter(writer, CSVFormat.DEFAULT));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    return name;
  }

  @Override
  public void write(UUID id, AirbyteRecordMessage recordMessage, String gcsFileName) throws Exception {
    if (csvPrinters.containsKey(gcsFileName)) {
      csvPrinters.get(gcsFileName).printRecord(id,
          Jsons.serialize(recordMessage.getData()),
          Timestamp.from(Instant.ofEpochMilli(recordMessage.getEmittedAt())));
    }
  }

  @Override
  public void closeStagingUploader(boolean hasFailed) throws Exception {
    LOGGER.info("Uploading remaining data for {} stream.", streamName);
    for (var csvPrinter : csvPrinters.values()) {
      csvPrinter.close();
    }
    for (var channel : channels.values()) {
      channel.close();
    }
    LOGGER.info("All data for {} stream uploaded.", streamName);
  }

  @Override
  public void copyStagingFileToTemporaryTable() throws Exception {
    LOGGER.info("Starting copy to tmp table: {} in destination for stream: {}, schema: {}.", tmpTableName, streamName, schemaName);
    for (var gcsStagingFile : gcsStagingFiles) {
      copyGcsCsvFileIntoTable(db, getFullGcsPath(gcsConfig.getBucketName(), gcsStagingFile), schemaName, tmpTableName, gcsConfig);
    }
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  @Override
  public void removeFileAndDropTmpTable() throws Exception {
    for (var gcsStagingFile : gcsStagingFiles) {
      LOGGER.info("Begin cleaning gcs staging file {}.", gcsStagingFile);
      var blobId = BlobId.of(gcsConfig.getBucketName(), gcsStagingFile);
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
    var destTableName = nameTransformer.getRawTableName(streamName);
    LOGGER.info("Preparing table {} in destination.", destTableName);
    sqlOperations.createTableIfNotExists(db, schemaName, destTableName);
    LOGGER.info("Table {} in destination prepared.", tmpTableName);

    return destTableName;
  }

  @Override
  public String generateMergeStatement(String destTableName) throws Exception {
    LOGGER.info("Preparing to merge tmp table {} to dest table: {}, schema: {}, in destination.", tmpTableName, destTableName, schemaName);
    var queries = new StringBuilder();
    if (destSyncMode.equals(DestinationSyncMode.OVERWRITE)) {
      queries.append(sqlOperations.truncateTableQuery(db, schemaName, destTableName));
      LOGGER.info("Destination OVERWRITE mode detected. Dest table: {}, schema: {}, will be truncated.", destTableName, schemaName);
    }
    queries.append(sqlOperations.copyTableQuery(db, schemaName, tmpTableName, destTableName));
    return queries.toString();
  }

  private static String getFullGcsPath(String bucketName, String stagingFile) {
    // this is intentionally gcs:/ not gcs:// since the join adds the additional slash
    return String.join("/", "gcs:/", bucketName, stagingFile);
  }

  public static void attemptWriteToPersistence(GcsConfig gcsConfig) throws IOException {
    final String outputTableName = "_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", "");
    attemptWriteAndDeleteGcsObject(gcsConfig, outputTableName);
  }

  private static void attemptWriteAndDeleteGcsObject(GcsConfig gcsConfig, String outputTableName) throws IOException {
    var storage = getStorageClient(gcsConfig);
    var blobId = BlobId.of(gcsConfig.getBucketName(), "check-content/" + outputTableName);
    var blobInfo = BlobInfo.newBuilder(blobId).build();

    storage.create(blobInfo, "".getBytes());
    storage.delete(blobId);
  }

  public static Storage getStorageClient(GcsConfig gcsConfig) throws IOException {
    InputStream credentialsInputStream = new ByteArrayInputStream(gcsConfig.getCredentialsJson().getBytes());
    GoogleCredentials credentials = GoogleCredentials.fromStream(credentialsInputStream);
    return StorageOptions.newBuilder()
        .setCredentials(credentials)
        .setProjectId(gcsConfig.getProjectId())
        .build()
        .getService();
  }

  public abstract void copyGcsCsvFileIntoTable(JdbcDatabase database,
                                               String gcsFileLocation,
                                               String schema,
                                               String tableName,
                                               GcsConfig gcsConfig)
      throws SQLException;

}
