/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.jdbc.copy.azureblob;

import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.azure.storage.blob.specialized.BlobOutputStream;
import com.azure.storage.common.StorageSharedKeyCredential;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AzureBlobStreamCopier implements StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureBlobStreamCopier.class);

  private final AppendBlobClient appendBlobClient;
  private final AzureBlobConfig azureBlobConfig;
  private final CSVPrinter csvPrinter;
  private final String tmpTableName;
  private final DestinationSyncMode destSyncMode;
  private final String schemaName;
  private final String streamName;
  private final JdbcDatabase db;
  private final ExtendedNameTransformer nameTransformer;
  private final SqlOperations sqlOperations;
  private final BlobOutputStream blobOutputStream;
  private final String azureBlobPath;
  private final String snowflakeAzureExternalStageName;

  public AzureBlobStreamCopier(String stagingFolder,
                        DestinationSyncMode destSyncMode,
                        String schema,
                        String streamName,
                        AppendBlobClient appendBlobClient,
                        JdbcDatabase db,
                        AzureBlobConfig azureBlobConfig,
                        ExtendedNameTransformer nameTransformer,
                        SqlOperations sqlOperations) {
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
    this.snowflakeAzureExternalStageName = azureBlobConfig.getSnowflakeAzureExternalStageName();
    
    this.blobOutputStream = appendBlobClient.getBlobOutputStream();

    var writer = new PrintWriter(blobOutputStream, true, StandardCharsets.UTF_8);
    try {
      this.csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void write(UUID id, AirbyteRecordMessage recordMessage) throws Exception {
    csvPrinter.printRecord(id,         
      Jsons.serialize(recordMessage.getData()),
      Timestamp.from(Instant.ofEpochMilli(recordMessage.getEmittedAt())));
  }

  @Override
  public void closeStagingUploader(boolean hasFailed) throws Exception {
    LOGGER.info("Uploading remaining data for {} stream.", streamName);
    csvPrinter.close();
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
    LOGGER.info("Starting copy to tmp table: {} in destination for stream: {}, schema: {}, .", tmpTableName, streamName, schemaName);
    copyAzureBlobCsvFileIntoTable(db, snowflakeAzureExternalStageName, schemaName, tmpTableName, appendBlobClient);
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
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

  public static void attemptAzureBlobWriteAndDelete(AzureBlobConfig azureBlobConfig) {
    attemptAzureBlobWriteAndDelete(azureBlobConfig, "");
  }

  public static void attemptAzureBlobWriteAndDelete(AzureBlobConfig azureBlobConfig, String blobPath) {
    var prefix = blobPath.isEmpty() ? "" : blobPath + (blobPath.endsWith("/") ? "" : "/");
    final String streamName = prefix + "_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", "");
    attemptWriteAndDeleteAzureBlobObject(azureBlobConfig, streamName);
  }

  private static void attemptWriteAndDeleteAzureBlobObject(AzureBlobConfig azureBlobConfig, String streamName) {
    var azure = getAppendBlobClient(azureBlobConfig, streamName); // client instantiation creates the blob necessarily
    azure.delete();
  }

  public static AppendBlobClient getAppendBlobClient(AzureBlobConfig azureBlobConfig, String streamName) {
   
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

  public abstract void copyAzureBlobCsvFileIntoTable(JdbcDatabase database,
                                              String snowflakeAzureExternalStageName,
                                              String schema,
                                              String tableName,
                                              AppendBlobClient aappendBlobClient)
      throws SQLException;

}
