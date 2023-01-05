/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.azure;

import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
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
import java.io.BufferedOutputStream;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
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

public abstract class AzureBlobStorageStreamCopier implements StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureBlobStorageStreamCopier.class);
  protected StagingFilenameGenerator filenameGenerator;
  protected final String stagingFolder;
  protected final Set<String> azureStagingFiles = new HashSet<>();
  protected final AzureBlobStorageConfig azureBlobConfig;
  protected final String tmpTableName;
  protected final String schemaName;
  protected final String streamName;
  protected final JdbcDatabase db;
  protected final Set<String> activeStagingWriterFileNames = new HashSet<>();
  private final ExtendedNameTransformer nameTransformer;
  private final SqlOperations sqlOperations;
  private final DestinationSyncMode destSyncMode;
  private final SpecializedBlobClientBuilder specializedBlobClientBuilder;
  private final HashMap<String, CSVPrinter> csvPrinters = new HashMap<>();
  private final HashMap<String, AppendBlobClient> blobClients = new HashMap<>();
  private String currentFile;

  public AzureBlobStorageStreamCopier(final String stagingFolder,
                                      final DestinationSyncMode destSyncMode,
                                      final String schema,
                                      final String streamName,
                                      final SpecializedBlobClientBuilder specializedBlobClientBuilder,
                                      final JdbcDatabase db,
                                      final AzureBlobStorageConfig azureBlobConfig,
                                      final ExtendedNameTransformer nameTransformer,
                                      final SqlOperations sqlOperations) {
    this.stagingFolder = stagingFolder;
    this.destSyncMode = destSyncMode;
    this.schemaName = schema;
    this.streamName = streamName;
    this.db = db;
    this.nameTransformer = nameTransformer;
    this.sqlOperations = sqlOperations;
    this.tmpTableName = nameTransformer.getTmpTableName(streamName);
    this.specializedBlobClientBuilder = specializedBlobClientBuilder;
    this.azureBlobConfig = azureBlobConfig;
    this.filenameGenerator = new StagingFilenameGenerator(streamName, GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES);
  }

  public static void attemptAzureBlobWriteAndDelete(final AzureBlobStorageConfig config) {
    AppendBlobClient appendBlobClient = null;
    try {
      appendBlobClient = new SpecializedBlobClientBuilder()
          .endpoint(config.getEndpointUrl())
          .sasToken(config.getSasToken())
          .containerName(config.getContainerName())
          .blobName("testAzureBlob" + UUID.randomUUID())
          .buildAppendBlobClient();

      final BlobContainerClient containerClient = getBlobContainerClient(appendBlobClient);
      writeTestDataIntoBlob(appendBlobClient);
      listCreatedBlob(containerClient);
    } finally {
      if (appendBlobClient != null && appendBlobClient.exists()) {
        LOGGER.info("Deleting blob: " + appendBlobClient.getBlobName());
        appendBlobClient.delete();
      }
    }

  }

  private static void listCreatedBlob(final BlobContainerClient containerClient) {
    containerClient.listBlobs().forEach(blobItem -> LOGGER.info("Blob name: " + blobItem.getName() + "Snapshot: " + blobItem.getSnapshot()));
  }

  private static void writeTestDataIntoBlob(final AppendBlobClient appendBlobClient) {
    final String test = "test_data";
    LOGGER.info("Writing test data to Azure Blob storage: " + test);
    final InputStream dataStream = new ByteArrayInputStream(test.getBytes(StandardCharsets.UTF_8));

    final Integer blobCommittedBlockCount = appendBlobClient.appendBlock(dataStream, test.length())
        .getBlobCommittedBlockCount();

    LOGGER.info("blobCommittedBlockCount: " + blobCommittedBlockCount);
  }

  private static BlobContainerClient getBlobContainerClient(final AppendBlobClient appendBlobClient) {
    final BlobContainerClient containerClient = appendBlobClient.getContainerClient();
    if (!containerClient.exists()) {
      containerClient.create();
    }

    if (!appendBlobClient.exists()) {
      appendBlobClient.create();
      LOGGER.info("blobContainerClient created");
    } else {
      LOGGER.info("blobContainerClient already exists");
    }
    return containerClient;
  }

  public Set<String> getAzureStagingFiles() {
    return azureStagingFiles;
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage, final String azureFileName) throws Exception {
    if (csvPrinters.containsKey(azureFileName)) {
      csvPrinters.get(azureFileName).printRecord(id,
          Jsons.serialize(recordMessage.getData()),
          Timestamp.from(Instant.ofEpochMilli(recordMessage.getEmittedAt())));
    }
  }

  @Override
  public String prepareStagingFile() {
    currentFile = prepareAzureStagingFile();
    if (!azureStagingFiles.contains(currentFile)) {

      azureStagingFiles.add(currentFile);
      activeStagingWriterFileNames.add(currentFile);

      final AppendBlobClient appendBlobClient = specializedBlobClientBuilder
          .blobName(currentFile)
          .buildAppendBlobClient();
      blobClients.put(currentFile, appendBlobClient);
      appendBlobClient.create(true);

      final BufferedOutputStream bufferedOutputStream =
          new BufferedOutputStream(appendBlobClient.getBlobOutputStream(), Math.toIntExact(GlobalDataSizeConstants.MAX_FILE_SIZE));
      final var writer = new PrintWriter(bufferedOutputStream, true, StandardCharsets.UTF_8);
      try {
        csvPrinters.put(currentFile, new CSVPrinter(writer, CSVFormat.DEFAULT));
      } catch (final IOException e) {
        throw new RuntimeException(e);
      }
    }
    return currentFile;
  }

  private String prepareAzureStagingFile() {
    return String.join("/", stagingFolder, schemaName, filenameGenerator.getStagingFilename());
  }

  @Override
  public void closeStagingUploader(final boolean hasFailed) throws Exception {
    LOGGER.info("Uploading remaining data for {} stream.", streamName);
    for (final var csvPrinter : csvPrinters.values()) {
      csvPrinter.close();
    }
    LOGGER.info("All data for {} stream uploaded.", streamName);
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
    LOGGER.info("Starting copy to tmp table: {} in destination for stream: {}, schema: {}.", tmpTableName, streamName, schemaName);
    for (final var azureStagingFile : azureStagingFiles) {
      copyAzureBlobCsvFileIntoTable(db, getFullAzurePath(azureStagingFile), schemaName, tmpTableName, azureBlobConfig);
    }
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  private String getFullAzurePath(final String azureStagingFile) {
    return "azure://" + azureBlobConfig.getAccountName() + "." + azureBlobConfig.getEndpointDomainName()
        + "/" + azureBlobConfig.getContainerName() + "/" + azureStagingFile;
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
      LOGGER.info("Destination OVERWRITE mode detected. Dest table: {}, schema: {}, truncated.", destTableName, schemaName);
    }
    queries.append(sqlOperations.insertTableQuery(db, schemaName, tmpTableName, destTableName));
    return queries.toString();
  }

  @Override
  public void removeFileAndDropTmpTable() throws Exception {
    LOGGER.info("Begin cleaning azure blob staging files.");
    for (final AppendBlobClient appendBlobClient : blobClients.values()) {
      appendBlobClient.delete();
    }
    LOGGER.info("Azure Blob staging files cleaned.");

    LOGGER.info("Begin cleaning {} tmp table in destination.", tmpTableName);
    sqlOperations.dropTableIfExists(db, schemaName, tmpTableName);
    LOGGER.info("{} tmp table in destination cleaned.", tmpTableName);
  }

  @Override
  public void closeNonCurrentStagingFileWriters() throws Exception {
    LOGGER.info("Begin closing non current file writers");
    final Set<String> removedKeys = new HashSet<>();
    for (final String key : activeStagingWriterFileNames) {
      if (!key.equals(currentFile)) {
        csvPrinters.get(key).close();
        csvPrinters.remove(key);
        removedKeys.add(key);
      }
    }
    activeStagingWriterFileNames.removeAll(removedKeys);
  }

  @Override
  public String getCurrentFile() {
    return currentFile;
  }

  @VisibleForTesting
  public String getTmpTableName() {
    return tmpTableName;
  }

  public abstract void copyAzureBlobCsvFileIntoTable(JdbcDatabase database,
                                                     String snowflakeAzureExternalStageName,
                                                     String schema,
                                                     String tableName,
                                                     AzureBlobStorageConfig config)
      throws SQLException;

}
