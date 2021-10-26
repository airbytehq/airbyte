/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobServiceClient;
import com.azure.storage.blob.BlobServiceClientBuilder;
import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.azure.storage.common.StorageSharedKeyCredential;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AzureBlobStorageDestinationAcceptanceTest extends DestinationAcceptanceTest {

  protected static final Logger LOGGER = LoggerFactory
      .getLogger(AzureBlobStorageDestinationAcceptanceTest.class);
  protected static final ObjectMapper MAPPER = MoreMappers.initMapper();

  protected final String secretFilePath = "secrets/config.json";
  protected final AzureBlobStorageFormat outputFormat;
  protected JsonNode configJson;
  protected AzureBlobStorageDestinationConfig azureBlobStorageDestinationConfig;
  protected SpecializedBlobClientBuilder specializedBlobClientBuilder;
  protected StorageSharedKeyCredential credential;

  protected AzureBlobStorageDestinationAcceptanceTest(final AzureBlobStorageFormat outputFormat) {
    this.outputFormat = outputFormat;
  }

  protected JsonNode getBaseConfigJson() {
    return Jsons.deserialize(IOs.readFile(Path.of(secretFilePath)));
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-azure-blob-storage:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name", "invalidAccountName")
        .put("azure_blob_storage_account_key", "invalidAccountKey")
        .put("azure_blob_storage_endpoint_domain_name", "InvalidDomainName")
        .put("format", getFormatConfig())
        .build());
  }

  /**
   * Helper method to retrieve all synced objects inside the configured bucket path.
   */
  @Deprecated
  protected String getAllSyncedObjects(final String streamName) {
    final AppendBlobClient appendBlobClient = specializedBlobClientBuilder
        .blobName(streamName)
        .buildAppendBlobClient();

    final ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
    appendBlobClient.download(outputStream);
    final String result = new String(outputStream.toByteArray(), StandardCharsets.UTF_8);

    LOGGER.info("All objects: " + result);
    return result;

  }

  protected abstract JsonNode getFormatConfig();

  /**
   * This method does the following:
   * <li>Construct the Azure Blob destination config.</li>
   * <li>Construct the Azure Blob client.</li>
   */
  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    final JsonNode baseConfigJson = getBaseConfigJson();

    configJson = Jsons.jsonNode(ImmutableMap.builder()
        .put("azure_blob_storage_account_name",
            baseConfigJson.get("azure_blob_storage_account_name"))
        .put("azure_blob_storage_account_key", baseConfigJson.get("azure_blob_storage_account_key"))
        .put("azure_blob_storage_endpoint_domain_name",
            baseConfigJson.get("azure_blob_storage_endpoint_domain_name"))
        .put("azure_blob_storage_container_name",
            baseConfigJson.get("azure_blob_storage_container_name").asText()
                + System.currentTimeMillis())
        .put("format", getFormatConfig())
        .build());

    this.azureBlobStorageDestinationConfig = AzureBlobStorageDestinationConfig
        .getAzureBlobStorageConfig(configJson);

    this.credential = new StorageSharedKeyCredential(
        azureBlobStorageDestinationConfig.getAccountName(),
        azureBlobStorageDestinationConfig.getAccountKey());

    this.specializedBlobClientBuilder = new SpecializedBlobClientBuilder()
        .endpoint(azureBlobStorageDestinationConfig.getEndpointUrl())
        .credential(credential)
        .containerName(
            azureBlobStorageDestinationConfig.getContainerName());// Like user\schema in DB

  }

  /**
   * Remove all the Container output from the tests.
   */
  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    final BlobServiceClient storageClient =
        new BlobServiceClientBuilder()
            .endpoint(azureBlobStorageDestinationConfig.getEndpointUrl())
            .credential(credential)
            .buildClient();

    final BlobContainerClient blobContainerClient = storageClient
        .getBlobContainerClient(azureBlobStorageDestinationConfig.getContainerName());

    if (blobContainerClient.exists()) {
      LOGGER.info("Deleting test env: " + azureBlobStorageDestinationConfig.getContainerName());
      blobContainerClient.delete();
    }
  }

}
