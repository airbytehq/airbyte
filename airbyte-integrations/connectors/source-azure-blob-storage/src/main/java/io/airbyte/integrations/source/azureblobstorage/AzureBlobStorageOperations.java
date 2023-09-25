/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azureblobstorage;

import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.models.BlobListDetails;
import com.azure.storage.blob.models.ListBlobsOptions;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedFunction;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import org.apache.commons.lang3.StringUtils;

public abstract class AzureBlobStorageOperations {

  protected final BlobContainerClient blobContainerClient;

  protected final AzureBlobStorageConfig azureBlobStorageConfig;

  protected AzureBlobStorageOperations(AzureBlobStorageConfig azureBlobStorageConfig) {
    this.azureBlobStorageConfig = azureBlobStorageConfig;
    this.blobContainerClient = azureBlobStorageConfig.createBlobContainerClient();
  }

  public abstract JsonNode inferSchema();

  public abstract List<JsonNode> readBlobs(OffsetDateTime offsetDateTime);

  public List<AzureBlob> listBlobs() {

    var listBlobsOptions = new ListBlobsOptions();
    listBlobsOptions.setDetails(new BlobListDetails()
        .setRetrieveMetadata(true)
        .setRetrieveDeletedBlobs(false));

    if (!StringUtils.isBlank(azureBlobStorageConfig.prefix())) {
      listBlobsOptions.setPrefix(azureBlobStorageConfig.prefix());
    }

    var pagedIterable = blobContainerClient.listBlobs(listBlobsOptions, null);

    List<AzureBlob> azureBlobs = new ArrayList<>();
    pagedIterable.forEach(blobItem -> azureBlobs.add(new AzureBlob.Builder()
        .withName(blobItem.getName())
        .withLastModified(blobItem.getProperties().getLastModified())
        .build()));
    return azureBlobs;

  }

  protected <T, R> R handleCheckedIOException(CheckedFunction<T, R, IOException> checkedFunction, T parameter) {
    try {
      return checkedFunction.apply(parameter);
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    }
  }

}
