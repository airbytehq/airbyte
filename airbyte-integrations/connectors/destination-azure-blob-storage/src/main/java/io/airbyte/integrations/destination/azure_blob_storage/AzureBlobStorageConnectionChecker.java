/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import com.azure.core.http.rest.PagedIterable;
import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.models.BlobItem;
import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.azure.storage.common.StorageSharedKeyCredential;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureBlobStorageConnectionChecker {

  private static final String TEST_BLOB_NAME_PREFIX = "testConnectionBlob";
  private BlobContainerClient containerClient; // aka schema in SQL DBs
  private final AppendBlobClient appendBlobClient; // aka "SQL Table"

  private static final Logger LOGGER = LoggerFactory.getLogger(
      AzureBlobStorageConnectionChecker.class);

  public AzureBlobStorageConnectionChecker(
                                           final AzureBlobStorageDestinationConfig azureBlobStorageConfig) {

    final StorageSharedKeyCredential credential = new StorageSharedKeyCredential(
        azureBlobStorageConfig.getAccountName(),
        azureBlobStorageConfig.getAccountKey());

    this.appendBlobClient =
        new SpecializedBlobClientBuilder()
            .endpoint(azureBlobStorageConfig.getEndpointUrl())
            .credential(credential)
            .containerName(azureBlobStorageConfig.getContainerName()) // Like schema in DB
            .blobName(TEST_BLOB_NAME_PREFIX + UUID.randomUUID()) // Like table in DB
            .buildAppendBlobClient();
  }

  public AzureBlobStorageConnectionChecker(final AzureBlobStorageConfig azureBlobStorageConfig) {
    this.appendBlobClient =
        new SpecializedBlobClientBuilder()
            .endpoint(azureBlobStorageConfig.getEndpointUrl())
            .sasToken(azureBlobStorageConfig.getSasToken())
            .containerName(azureBlobStorageConfig.getContainerName()) // Like schema in DB
            .blobName(TEST_BLOB_NAME_PREFIX + UUID.randomUUID()) // Like table in DB
            .buildAppendBlobClient();
  }

  /*
   * This a kinda test method that is used in CHECK operation to make sure all works fine with the
   * current config
   */
  public void attemptWriteAndDelete() {
    initTestContainerAndBlob();
    writeUsingAppendBlock("Some test data");
    listBlobsInContainer()
        .forEach(
            blobItem -> LOGGER.info(
                "Blob name: " + blobItem.getName() + "Snapshot: " + blobItem.getSnapshot()));

    deleteBlob();
  }

  private void initTestContainerAndBlob() {
    // create container if absent (aka SQl Schema)
    this.containerClient = appendBlobClient.getContainerClient();
    if (!containerClient.exists()) {
      containerClient.create();
    }

    // create a storage container if absent (aka Table is SQL BD)
    if (!appendBlobClient.exists()) {
      appendBlobClient.create();
      LOGGER.info("blobContainerClient created");
    } else {
      LOGGER.info("blobContainerClient already exists");
    }
  }

  /*
   * This options may be used to write and flush right away. Note: Azure SDK fails for empty lines,
   * but those are not supposed to be written here
   */
  public void writeUsingAppendBlock(final String data) {
    LOGGER.info("Writing test data to Azure Blob storage: " + data);
    final InputStream dataStream = new ByteArrayInputStream(data.getBytes(StandardCharsets.UTF_8));

    final Integer blobCommittedBlockCount = appendBlobClient.appendBlock(dataStream, data.length())
        .getBlobCommittedBlockCount();

    LOGGER.info("blobCommittedBlockCount: " + blobCommittedBlockCount);
  }

  /*
   * List the blob(s) in our container.
   */
  public PagedIterable<BlobItem> listBlobsInContainer() {
    return containerClient.listBlobs();
  }

  /*
   * Delete the blob we created earlier.
   */
  public void deleteBlob() {
    LOGGER.info("Deleting blob: " + appendBlobClient.getBlobName());
    appendBlobClient.delete(); // remove aka "SQL Table" used
  }

  /*
   * Delete the Container. Be very careful when you ise ir. It removes thw whole bucket and supposed
   * to be used in check connection ony for writing tmp data
   */
  public void deleteContainer() {
    LOGGER.info("Deleting blob: " + containerClient.getBlobContainerName());
    containerClient.delete(); // remove aka "SQL Schema" used
  }

}
