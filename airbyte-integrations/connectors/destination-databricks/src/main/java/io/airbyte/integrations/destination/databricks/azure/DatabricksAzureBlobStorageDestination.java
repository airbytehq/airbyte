/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.azure;

import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageConnectionChecker;
import io.airbyte.integrations.destination.databricks.DatabricksExternalStorageBaseDestination;
import io.airbyte.integrations.destination.databricks.DatabricksStorageConfigProvider;
import io.airbyte.integrations.destination.databricks.DatabricksStreamCopierFactory;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;

public class DatabricksAzureBlobStorageDestination extends DatabricksExternalStorageBaseDestination {

  @Override
  protected void checkPersistence(DatabricksStorageConfigProvider databricksConfig) {
    AzureBlobStorageConfig azureConfig = databricksConfig.getAzureBlobStorageConfigOrThrow();
    final AzureBlobStorageConnectionChecker client = new AzureBlobStorageConnectionChecker(azureConfig);
    client.attemptWriteAndDelete();
  }

  @Override
  protected DatabricksStreamCopierFactory getStreamCopierFactory() {
    return new DatabricksAzureBlobStorageStreamCopierFactory();
  }

}
