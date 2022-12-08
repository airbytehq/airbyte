/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;

public class DatabricksAzureBlobStorageConfig extends DatabricksStorageConfig {

  private final AzureBlobStorageConfig azureConfig;

  public DatabricksAzureBlobStorageConfig(JsonNode config) {
    this.azureConfig = AzureBlobStorageConfig.getAzureBlobConfig(config);
  }

  @Override
  public AzureBlobStorageConfig getAzureBlobStorageConfigOrThrow() {
    return azureConfig;
  }

}
