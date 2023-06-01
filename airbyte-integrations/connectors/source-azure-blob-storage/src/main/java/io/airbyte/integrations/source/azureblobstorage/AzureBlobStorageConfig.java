/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azureblobstorage;

import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobContainerClientBuilder;
import com.azure.storage.common.StorageSharedKeyCredential;
import com.fasterxml.jackson.databind.JsonNode;

public record AzureBlobStorageConfig(

                                     String endpoint,

                                     String accountName,

                                     String accountKey,

                                     String containerName,

                                     String prefix,

                                     Long schemaInferenceLimit,

                                     FormatConfig formatConfig

) {

  public record FormatConfig(Format format) {

    public enum Format {

      JSONL

    }

  }

  public static AzureBlobStorageConfig createAzureBlobStorageConfig(JsonNode jsonNode) {
    return new AzureBlobStorageConfig(
        jsonNode.has("azure_blob_storage_endpoint") ? jsonNode.get("azure_blob_storage_endpoint").asText() : null,
        jsonNode.get("azure_blob_storage_account_name").asText(),
        jsonNode.get("azure_blob_storage_account_key").asText(),
        jsonNode.get("azure_blob_storage_container_name").asText(),
        jsonNode.has("azure_blob_storage_blobs_prefix") ? jsonNode.get("azure_blob_storage_blobs_prefix").asText() : null,
        jsonNode.has("azure_blob_storage_schema_inference_limit") ? jsonNode.get("azure_blob_storage_schema_inference_limit").asLong() : null,
        formatConfig(jsonNode));
  }

  public BlobContainerClient createBlobContainerClient() {
    StorageSharedKeyCredential credential = new StorageSharedKeyCredential(
        this.accountName(),
        this.accountKey());

    var builder = new BlobContainerClientBuilder()
        .credential(credential)
        .containerName(this.containerName());

    if (this.endpoint() != null) {
      builder.endpoint(this.endpoint());
    }

    return builder.buildClient();
  }

  private static FormatConfig formatConfig(JsonNode config) {
    JsonNode formatConfig = config.get("format");

    FormatConfig.Format formatType = FormatConfig.Format
        .valueOf(formatConfig.get("format_type").asText().toUpperCase());

    return new FormatConfig(formatType);
  }

}
