/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.jsonl;

import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageFormat;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageFormatConfig;

public class AzureBlobStorageJsonlFormatConfig implements AzureBlobStorageFormatConfig {

  @Override
  public AzureBlobStorageFormat getFormat() {
    return AzureBlobStorageFormat.JSONL;
  }

}
