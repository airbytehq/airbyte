/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageConnectionChecker;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;

public class DatabricksAzureBlobStorageDestination extends DatabricksBaseDestination {

  @Override
  protected void checkPersistence(DatabricksStorageConfig databricksConfig) {
    AzureBlobStorageConfig azureConfig = databricksConfig.getAzureBlobStorageConfigOrThrow();
    final AzureBlobStorageConnectionChecker client = new AzureBlobStorageConnectionChecker(azureConfig);
    client.attemptWriteAndDelete();
  }

  @Override
  protected DatabricksStreamCopierFactory getStreamCopierFactory() {
    return new DatabricksAzureBlobStorageStreamCopierFactory();
  }

}
