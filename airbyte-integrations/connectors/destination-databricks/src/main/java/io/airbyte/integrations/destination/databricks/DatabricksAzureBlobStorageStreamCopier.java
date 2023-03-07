/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConfig;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageFormatConfig;
import io.airbyte.integrations.destination.azure_blob_storage.csv.AzureBlobStorageCsvFormatConfig;
import io.airbyte.integrations.destination.azure_blob_storage.csv.AzureBlobStorageCsvWriter;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.IOException;
import java.util.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This implementation does the following operations:
 * <ul>
 * <li>1. CSV writers write data stream into staging CSV files in temporary storage location in
 * Azure Blob Storage.</li>
 * <li>2. Create a tmp delta table based on the staging CSV files.</li>
 * <li>3. Create the destination delta table based on the tmp delta table schema.</li>
 * <li>4. Copy the temporary table into the destination delta table.</li>
 * <li>5. Delete the tmp delta table, and the staging CSV files.</li>
 * </ul>
 */
public class DatabricksAzureBlobStorageStreamCopier extends DatabricksStreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksAzureBlobStorageStreamCopier.class);
  private static final String AZURE_BLOB_ENDPOINT_DOMAIN_NAME = "blob.core.windows.net";
  private static final String AZURE_DFS_ENDPOINT_DOMAIN_NAME = "dfs.core.windows.net";

  private final SpecializedBlobClientBuilder specializedBlobClientBuilder;
  private final AzureBlobStorageConfig azureConfig;
  protected final Set<String> azureStagingFiles = new HashSet<>();

  protected final Set<String> activeStagingWriterFileNames = new HashSet<>();
  protected final HashMap<String, AzureBlobStorageCsvWriter> csvWriters = new HashMap<>();
  protected final HashMap<String, AppendBlobClient> blobClients = new HashMap<>();
  protected String currentFile;

  public DatabricksAzureBlobStorageStreamCopier(final String stagingFolder,
                                                final String schema,
                                                final ConfiguredAirbyteStream configuredStream,
                                                final JdbcDatabase database,
                                                final DatabricksDestinationConfig databricksConfig,
                                                final ExtendedNameTransformer nameTransformer,
                                                final SqlOperations sqlOperations,
                                                SpecializedBlobClientBuilder specializedBlobClientBuilder,
                                                AzureBlobStorageConfig azureConfig) {
    super(stagingFolder, schema, configuredStream, database, databricksConfig, nameTransformer, sqlOperations);

    this.specializedBlobClientBuilder = specializedBlobClientBuilder;
    this.azureConfig = azureConfig;

    LOGGER.info("[Stream {}] Tmp table {} location: {}", streamName, tmpTableName, getTmpTableLocation());
    LOGGER.info("[Stream {}] Data table {} location: {}", streamName, destTableName, getDestTableLocation());
  }

  public String getTmpTableLocation() {
    return String.format("abfss://%s@%s.%s/%s/%s/%s/",
        azureConfig.getContainerName(), azureConfig.getAccountName(), azureConfig.getEndpointDomainName(),
        stagingFolder, schemaName, tmpTableName);
  }

  public String getDestTableLocation() {
    return String.format("abfss://%s@%s.%s/%s/%s/",
        azureConfig.getContainerName(), azureConfig.getAccountName(),
        // If this is .blob.core, we need to replace with .dfs.core to create table in Databricks
        azureConfig.getEndpointDomainName().replace(AZURE_BLOB_ENDPOINT_DOMAIN_NAME, AZURE_DFS_ENDPOINT_DOMAIN_NAME),
        schemaName, streamName);
  }

  @Override
  public String prepareStagingFile() {
    currentFile = prepareAzureStagingFile();
    if (!azureStagingFiles.contains(currentFile)) {

      azureStagingFiles.add(currentFile);
      activeStagingWriterFileNames.add(currentFile);

      final AppendBlobClient appendBlobClient = specializedBlobClientBuilder
          .sasToken(azureConfig.getSasToken())
          .blobName(currentFile)
          .buildAppendBlobClient();
      blobClients.put(currentFile, appendBlobClient);
      getBlobContainerClient(appendBlobClient);

      try {

        String accountKey = "doesntmatter";
        String containerPath = String.format("%s/%s/%s/%s/", azureConfig.getContainerName(), stagingFolder, schemaName, streamName);
        AzureBlobStorageFormatConfig formatConfig =
            new AzureBlobStorageCsvFormatConfig(Jsons.jsonNode(Map.of("flattening", "Root level flattening")));
        AzureBlobStorageDestinationConfig config = new AzureBlobStorageDestinationConfig(azureConfig.getEndpointUrl(),
            azureConfig.getAccountName(), accountKey, containerPath, 5,
            formatConfig);
        this.csvWriters.put(currentFile, new AzureBlobStorageCsvWriter(config, appendBlobClient, configuredStream));
      } catch (final IOException e) {
        throw new RuntimeException(e);
      }
    }
    return currentFile;
  }

  protected String prepareAzureStagingFile() {
    return String.join("/", stagingFolder, schemaName, tmpTableName, filenameGenerator.getStagingFilename());
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage, final String fileName) throws Exception {
    if (csvWriters.containsKey(fileName)) {
      csvWriters.get(fileName).write(id, recordMessage);
    }
  }

  @Override
  public void closeStagingUploader(final boolean hasFailed) throws Exception {
    LOGGER.info("Uploading remaining data for {} stream.", streamName);
    for (final var csvWriter : csvWriters.values()) {
      csvWriter.close(hasFailed);
    }
    LOGGER.info("All data for {} stream uploaded.", streamName);
  }

  @Override
  protected String getCreateTempTableStatement() {
    final AirbyteStream stream = configuredStream.getStream();
    LOGGER.info("Json schema for stream {}: {}", stream.getName(), stream.getJsonSchema());

    String schemaString = getSchemaString();

    LOGGER.info("[Stream {}] tmp table schema: {}", stream.getName(), schemaString);

    return String.format("CREATE TABLE %s.%s (%s) USING csv LOCATION '%s' " +
        "options (\"header\" = \"true\", \"multiLine\" = \"true\") ;",
        schemaName, tmpTableName, schemaString,
        getTmpTableLocation().replace(AZURE_BLOB_ENDPOINT_DOMAIN_NAME, AZURE_DFS_ENDPOINT_DOMAIN_NAME));
  }

  private String getSchemaString() {
    // Databricks requires schema to be provided when creating delta table from CSV
    StringBuilder schemaString = new StringBuilder("_airbyte_ab_id string, _airbyte_emitted_at string");
    ObjectNode properties = (ObjectNode) configuredStream.getStream().getJsonSchema().get("properties");
    List<String> recordHeaders = MoreIterators.toList(properties.fieldNames())
        .stream().sorted().toList();
    for (String header : recordHeaders) {
      JsonNode node = properties.get(header);
      String type = node.get("type").asText();
      schemaString.append(", `").append(header).append("` ").append(type.equals("number") ? "double" : type);
    }
    return schemaString.toString();
  }

  @Override
  public String generateMergeStatement(final String destTableName) {
    LOGGER.info("Preparing to merge tmp table {} to dest table: {}, schema: {}, in destination.", tmpTableName, destTableName, schemaName);
    var queries = new StringBuilder();
    if (destinationSyncMode.equals(DestinationSyncMode.OVERWRITE)) {
      queries.append(sqlOperations.truncateTableQuery(database, schemaName, destTableName));
      LOGGER.info("Destination OVERWRITE mode detected. Dest table: {}, schema: {}, truncated.", destTableName, schemaName);
    }
    queries.append(sqlOperations.copyTableQuery(database, schemaName, tmpTableName, destTableName));

    return queries.toString();
  }

  @Override
  protected void deleteStagingFile() {
    LOGGER.info("Begin cleaning azure blob staging files.");
    for (AppendBlobClient appendBlobClient : blobClients.values()) {
      appendBlobClient.delete();
    }
    LOGGER.info("Azure Blob staging files cleaned.");
  }

  @Override
  public void closeNonCurrentStagingFileWriters() throws Exception {
    LOGGER.info("Begin closing non current file writers");
    Set<String> removedKeys = new HashSet<>();
    for (String key : activeStagingWriterFileNames) {
      if (!key.equals(currentFile)) {
        csvWriters.get(key).close(false);
        csvWriters.remove(key);
        removedKeys.add(key);
      }
    }
    activeStagingWriterFileNames.removeAll(removedKeys);
  }

  @Override
  public String getCurrentFile() {
    return currentFile;
  }

  private static BlobContainerClient getBlobContainerClient(AppendBlobClient appendBlobClient) {
    BlobContainerClient containerClient = appendBlobClient.getContainerClient();
    if (!containerClient.exists()) {
      containerClient.create();
    }

    if (!appendBlobClient.exists()) {
      appendBlobClient.create();
    }
    return containerClient;
  }

}
