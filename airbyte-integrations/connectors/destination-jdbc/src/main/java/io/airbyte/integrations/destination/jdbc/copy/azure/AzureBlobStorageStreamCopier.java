package io.airbyte.integrations.destination.jdbc.copy.azure;

import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.models.AppendBlobItem;
import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.BlobOutputStream;
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.azure.storage.common.StorageSharedKeyCredential;
import com.google.cloud.WriteChannel;
import com.google.cloud.storage.BlobId;
import com.google.cloud.storage.BlobInfo;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.StagingFilenameGenerator;
import io.airbyte.integrations.destination.jdbc.constants.GlobalDataSizeConstants;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.BufferedOutputStream;
import java.io.IOException;
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

public abstract class AzureBlobStorageStreamCopier implements StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureBlobStorageStreamCopier.class);
  protected StagingFilenameGenerator filenameGenerator;
  private final AppendBlobClient appendBlobClient;
  private final AzureBlobStorageConfig azureBlobConfig;
//  private final CSVPrinter csvPrinter;
  private final String tmpTableName;
  private final DestinationSyncMode destSyncMode;
  private final String schemaName;
  private final String streamName;
  private final JdbcDatabase db;
  private final ExtendedNameTransformer nameTransformer;
  private final SqlOperations sqlOperations;
//  private final BlobOutputStream blobOutputStream;
  private final String azureBlobPath;
//  private final String snowflakeAzureExternalStageName;
  private final String stagingFolder;
  protected final Set<String> azureStagingFiles = new HashSet<>();
  private final HashMap<String, CSVPrinter> csvPrinters = new HashMap<>();
//  private final HashMap<String, BlobOutputStream> channels = new HashMap<>();
//  private final BufferedOutputStream bufferedOutputStream;

  public AzureBlobStorageStreamCopier(String stagingFolder,
      DestinationSyncMode destSyncMode,
      String schema,
      String streamName,
      AppendBlobClient appendBlobClient,
      JdbcDatabase db,
      AzureBlobStorageConfig azureBlobConfig,
      ExtendedNameTransformer nameTransformer,
      SqlOperations sqlOperations) {
    this.stagingFolder = stagingFolder;
    this.destSyncMode = destSyncMode;
    this.schemaName = schema;
    this.streamName = streamName;
    this.db = db;
    this.nameTransformer = nameTransformer;
    this.sqlOperations = sqlOperations;
    this.tmpTableName = nameTransformer.getTmpTableName(streamName);
    this.appendBlobClient = appendBlobClient;
    this.azureBlobConfig = azureBlobConfig;
    this.azureBlobPath = String.join("/", azureBlobConfig.getEndpointUrl(), azureBlobConfig.getContainerName(), streamName);
//    this.snowflakeAzureExternalStageName = azureBlobConfig.getSnowflakeAzureExternalStageName();
    this.filenameGenerator = new StagingFilenameGenerator(streamName, GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES);
//    this.bufferedOutputStream = new BufferedOutputStream(appendBlobClient.getBlobOutputStream(), Math.toIntExact(GlobalDataSizeConstants.MAX_FILE_SIZE));

    //    this.blobOutputStream = appendBlobClient.getBlobOutputStream();
//
//    var writer = new PrintWriter(blobOutputStream, true, StandardCharsets.UTF_8);
//    try {
//      this.csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT);
//    } catch (IOException e) {
//      throw new RuntimeException(e);
//    }
  }

  @Override
  public void write(UUID id, AirbyteRecordMessage recordMessage, String azureFileName) throws Exception {
    if (csvPrinters.containsKey(azureFileName)) {
      csvPrinters.get(azureFileName).printRecord(id,
          Jsons.serialize(recordMessage.getData()),
          Timestamp.from(Instant.ofEpochMilli(recordMessage.getEmittedAt())));
    }
  }

  @Override
  public String prepareStagingFile() {
    final String name = prepareAzureStagingFile();
    if (!azureStagingFiles.contains(name)) {
      azureStagingFiles.add(name);
//      AppendBlobClient appendBlobClient = getAppendBlobClient(azureBlobConfig, streamName);
//      BlobOutputStream blobOutputStream = appendBlobClient.getBlobOutputStream();
      BufferedOutputStream bufferedOutputStream = new BufferedOutputStream(appendBlobClient.getBlobOutputStream(), Math.toIntExact(GlobalDataSizeConstants.MAX_FILE_SIZE));
//      AppendBlobItem appendBlobItem = appendBlobClient.create();
//      final var blobId = BlobId.of(gcsConfig.getBucketName(), name);
//      final var blobInfo = BlobInfo.newBuilder(blobId).build();
//      final var blob = storageClient.create(blobInfo);
//      final var channel = blob.writer();
//      channels.put(name, blobOutputStream);
//      final OutputStream outputStream = Channels.newOutputStream(channel);

      final var writer = new PrintWriter(bufferedOutputStream, true, StandardCharsets.UTF_8);
      try {
        csvPrinters.put(name, new CSVPrinter(writer, CSVFormat.DEFAULT));
      } catch (final IOException e) {
        throw new RuntimeException(e);
      }
    }
    return name;
  }

  private String prepareAzureStagingFile() {
    String join = String.join("/", stagingFolder, schemaName, filenameGenerator.getStagingFilename());
    LOGGER.error("join fileL3:" +join);
    return join;

  }
//  @Override
//  public void write(UUID id, AirbyteRecordMessage recordMessage) throws Exception {
//    csvPrinter.printRecord(id,
//        Jsons.serialize(recordMessage.getData()),
//        Timestamp.from(Instant.ofEpochMilli(recordMessage.getEmittedAt())));
//  }

  @Override
  public void closeStagingUploader(boolean hasFailed) throws Exception {
    LOGGER.info("Uploading remaining data for {} stream.", streamName);
    LOGGER.error("CSVPrinters:"+ csvPrinters.values().toString());
    for (final var csvPrinter : csvPrinters.values()) {
      csvPrinter.close();
    }
//    for (final var channel : channels.values()) {
//      channel.close();
//    }
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
      copyAzureBlobCsvFileIntoTable(db, getFullAzurePath(azureBlobConfig, azureStagingFile), schemaName, tmpTableName, azureBlobConfig);
    }
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  private String getFullAzurePath(AzureBlobStorageConfig containerName, String azureStagingFile) {
    return null;
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
      LOGGER.info("Destination OVERWRITE mode detected. Dest table: {}, schema: {}, truncated.", destTableName, schemaName);
    }
    queries.append(sqlOperations.copyTableQuery(db, schemaName, tmpTableName, destTableName));
    return queries.toString();
  }

  @Override
  public void removeFileAndDropTmpTable() throws Exception {
    LOGGER.info("Begin cleaning azure blob staging file {}.", azureBlobPath);
    if (appendBlobClient.exists()) {
      appendBlobClient.delete();
    }
    LOGGER.info("Azure Blob staging file {} cleaned.", azureBlobPath);

    LOGGER.info("Begin cleaning {} tmp table in destination.", tmpTableName);
    sqlOperations.dropTableIfExists(db, schemaName, tmpTableName);
    LOGGER.info("{} tmp table in destination cleaned.", tmpTableName);
  }


  public static AppendBlobClient getAppendBlobClient(AzureBlobStorageConfig azureBlobConfig, String streamName) {

    // Init the client itself here
    StorageSharedKeyCredential credential = new StorageSharedKeyCredential(
        azureBlobConfig.getAccountName(),
        azureBlobConfig.getAccountKey()
    );

    AppendBlobClient appendBlobClient = new SpecializedBlobClientBuilder()
        .endpoint(azureBlobConfig.getEndpointUrl())
        .credential(credential)
        .containerName(azureBlobConfig.getContainerName())
        .blobName(streamName)
        .buildAppendBlobClient();

    appendBlobClient.create(true); // overwrite if exists
    return appendBlobClient;

  }

  @Override
  public void closeNonCurrentStagingFileWriters() throws Exception {

  }

  @Override
  public String getCurrentFile() {
    return null;
  }
  public abstract void copyAzureBlobCsvFileIntoTable(JdbcDatabase database,
      String snowflakeAzureExternalStageName,
      String schema,
      String tableName,
      AzureBlobStorageConfig config)
      throws SQLException;

}
