/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import static io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConstants.*;

import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.azure.storage.common.StorageSharedKeyCredential;
import com.fasterxml.jackson.databind.JsonNode;
import java.util.Locale;

public class AzureBlobStorageDestinationConfig {

  private final String endpointUrl;
  private final String accountName;
  private final String accountKey;
  private final String containerName;
  private final int outputStreamBufferSize;
  private final int blobSpillSize;
  private final AzureBlobStorageFormatConfig formatConfig;

  public AzureBlobStorageDestinationConfig(final String endpointUrl,
                                           final String accountName,
                                           final String accountKey,
                                           final String containerName,
                                           final int outputStreamBufferSize,
                                           final int blobSpillSize,
                                           final AzureBlobStorageFormatConfig formatConfig) {
    this.endpointUrl = endpointUrl;
    this.accountName = accountName;
    this.accountKey = accountKey;
    this.containerName = containerName;
    this.outputStreamBufferSize = outputStreamBufferSize;
    this.blobSpillSize = blobSpillSize;
    this.formatConfig = formatConfig;
  }

  public AzureBlobStorageDestinationConfig(
                                           final String endpointUrl,
                                           final String accountName,
                                           final String accountKey,
                                           final String containerName,
                                           final int outputStreamBufferSize,
                                           final AzureBlobStorageFormatConfig formatConfig) {
    this.endpointUrl = endpointUrl;
    this.accountName = accountName;
    this.accountKey = accountKey;
    this.containerName = containerName;
    this.outputStreamBufferSize = outputStreamBufferSize;
    this.blobSpillSize = 0;
    this.formatConfig = formatConfig;
  }

  public String getEndpointUrl() {
    return endpointUrl;
  }

  public String getAccountName() {
    return accountName;
  }

  public String getAccountKey() {
    return accountKey;
  }

  public String getContainerName() {
    return containerName;
  }

  public AzureBlobStorageFormatConfig getFormatConfig() {
    return formatConfig;
  }

  public static SpecializedBlobClientBuilder createSpecializedBlobClientBuilder(
                                                                                AzureBlobStorageDestinationConfig destinationConfig) {

    // Init the client itself here
    final StorageSharedKeyCredential credential = new StorageSharedKeyCredential(
        destinationConfig.getAccountName(),
        destinationConfig.getAccountKey());

    return new SpecializedBlobClientBuilder()
        .endpoint(destinationConfig.getEndpointUrl())
        .credential(credential)
        .containerName(destinationConfig.getContainerName());

  }

  public long getBlobSpillSize() {
    // Convert from MB to Bytes
    return (long) blobSpillSize * 1024 * 1024;
  }

  public int getOutputStreamBufferSize() {
    // Convert from MB to Bytes
    return outputStreamBufferSize * 1024 * 1024;
  }

  public static AzureBlobStorageDestinationConfig getAzureBlobStorageConfig(final JsonNode config) {
    final String accountNameFomConfig = config.get("azure_blob_storage_account_name").asText();
    final String accountKeyFromConfig = config.get("azure_blob_storage_account_key").asText();
    final JsonNode endpointFromConfig = config
        .get("azure_blob_storage_endpoint_domain_name");
    final JsonNode containerName = config.get("azure_blob_storage_container_name");
    final int outputStreamBufferSizeFromConfig =
        config.get("azure_blob_storage_output_buffer_size") != null
            ? config.get("azure_blob_storage_output_buffer_size").asInt(DEFAULT_STORAGE_OUTPUT_BUFFER_SIZE)
            : DEFAULT_STORAGE_OUTPUT_BUFFER_SIZE;

    final String endpointComputed = String.format(Locale.ROOT, DEFAULT_STORAGE_ENDPOINT_FORMAT,
        DEFAULT_STORAGE_ENDPOINT_HTTP_PROTOCOL,
        accountNameFomConfig,
        endpointFromConfig == null ? DEFAULT_STORAGE_ENDPOINT_DOMAIN_NAME
            : endpointFromConfig.asText());

    final String containerNameComputed =
        containerName == null ? DEFAULT_STORAGE_CONTAINER_NAME : containerName.asText();

    final int blobSpillSize = config.get("azure_blob_storage_spill_size") != null
        ? config.get("azure_blob_storage_spill_size").asInt(0)
        : 0;

    return new AzureBlobStorageDestinationConfig(
        endpointComputed,
        accountNameFomConfig,
        accountKeyFromConfig,
        containerNameComputed,
        outputStreamBufferSizeFromConfig,
        blobSpillSize,
        AzureBlobStorageFormatConfigs.getAzureBlobStorageFormatConfig(config));
  }

}
