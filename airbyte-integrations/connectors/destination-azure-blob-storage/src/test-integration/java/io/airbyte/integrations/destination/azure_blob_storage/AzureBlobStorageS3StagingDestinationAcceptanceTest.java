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
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.charset.StandardCharsets;
import java.nio.file.Path;

public abstract class AzureBlobStorageS3StagingDestinationAcceptanceTest extends DestinationAcceptanceTest {

  protected static final Logger LOGGER = LoggerFactory
      .getLogger(AzureBlobStorageS3StagingDestinationAcceptanceTest.class);

  protected final String secretFilePath = "secrets/config_s3_staging.json";
  protected final AzureBlobStorageFormat outputFormat;
  protected JsonNode configJson;
  protected AzureBlobStorageDestinationConfig azureBlobStorageDestinationConfig;
  protected SpecializedBlobClientBuilder specializedBlobClientBuilder;
  protected StorageSharedKeyCredential credential;

  protected AzureBlobStorageS3StagingDestinationAcceptanceTest(final AzureBlobStorageFormat outputFormat) {
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
        .put("loading_method", Jsons.jsonNode(ImmutableMap.builder()
                .put("method", "S3 Staging")
                .put("bucket_name", "fail_bucket_name")
                .put("bucket_path", "fail_bucket_path")
                .put("bucket_region", "fail_bucket_region")
                .put("keep_files_in_s3-bucket", "Delete all tmp files from S3")
                .put("credential", Jsons.jsonNode(ImmutableMap.builder()
                        .put("credential_type", "S3_KEY")
                        .put("access_key_id", "fail_access_key_id")
                        .put("secret_access_key", "fail_secret_access_key")
                        .build()))
                .build()))
        .build());
  }

  /**
   * Helper method to retrieve all synced objects inside the configured bucket path.
   */
  protected String getAllSyncedObjects(final String streamName) {
    final AppendBlobClient appendBlobClient = specializedBlobClientBuilder
        .blobName(streamName)
        .buildAppendBlobClient();

    final String result = new String(appendBlobClient.downloadContent().toBytes(), StandardCharsets.UTF_8);

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
        .put("loading_method", getGcsLoadingMethod(baseConfigJson))
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

  protected JsonNode getGcsLoadingMethod(final JsonNode baseConfigJson) {
    return Jsons.jsonNode(ImmutableMap.builder()
            .put("method", "S3 Staging")
            .put("bucket_name", baseConfigJson.get("bucket_name"))
            .put("bucket_path", baseConfigJson.get("bucket_path"))
            .put("bucket_region", baseConfigJson.get("bucket_region"))
            .put("keep_files_in_s3-bucket", "Delete all tmp files from S3")
            .put("credential", Jsons.jsonNode(ImmutableMap.builder()
                    .put("credential_type", "S3_KEY")
                    .put("access_key_id", baseConfigJson.get("access_key_id"))
                    .put("secret_access_key", baseConfigJson.get("secret_access_key"))
                    .build()))
            .build());
  }

}
