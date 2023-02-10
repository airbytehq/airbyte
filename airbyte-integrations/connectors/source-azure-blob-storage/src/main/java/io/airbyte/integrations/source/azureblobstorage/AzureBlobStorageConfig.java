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

    // prefix and tags are mutually exclusive

    String prefix,

    String blobsTags,

    String schema,

    FormatConfig formatConfig

) {

    public record FormatConfig(Format format) {

        public enum Format {

            JSON

        }

    }

    public static AzureBlobStorageConfig createAzureBlobStorageConfig(JsonNode jsonNode) {
        return new AzureBlobStorageConfig(
            jsonNode.get("azure_blob_storage_endpoint").asText(),
            jsonNode.get("azure_blob_storage_account_name").asText(),
            jsonNode.get("azure_blob_storage_account_key").asText(),
            jsonNode.get("azure_blob_storage_container_name").asText(),
            jsonNode.get("azure_blob_storage_blobs_prefix").asText(),
            jsonNode.get("azure_blob_storage_blobs_tags").asText(),
            jsonNode.get("azure_blob_storage_blobs_schema").asText(),
            new FormatConfig(FormatConfig.Format.JSON)
        );
    }

    public BlobContainerClient createBlobContainerClient() {
        StorageSharedKeyCredential credential = new StorageSharedKeyCredential(
            this.accountName(),
            this.accountKey());

        return new BlobContainerClientBuilder()
            .endpoint(this.endpoint())
            .credential(credential)
            .containerName(this.containerName())
            .buildClient();

    }

}
