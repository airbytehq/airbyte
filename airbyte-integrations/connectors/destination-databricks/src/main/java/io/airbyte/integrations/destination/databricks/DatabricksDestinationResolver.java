/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.databricks.azure.DatabricksAzureBlobStorageDestination;
import io.airbyte.integrations.destination.databricks.s3.DatabricksS3Destination;
import io.airbyte.integrations.destination.databricks.utils.DatabricksConstants;
import java.util.Map;

public class DatabricksDestinationResolver {

  public static DatabricksStorageType getTypeFromConfig(final JsonNode config) {
    if (dataSourceConfigIsNotProvided(config)) {
      throw new IllegalArgumentException("Data Source type configurations must be provided");
    }
    return DatabricksStorageType.valueOf(
        config.get(DatabricksConstants.DATABRICKS_DATA_SOURCE_KEY).get(DatabricksConstants.DATABRICKS_DATA_SOURCE_TYPE_KEY).asText());
  }

  private static boolean dataSourceConfigIsNotProvided(JsonNode config) {
    return !config.hasNonNull(DatabricksConstants.DATABRICKS_DATA_SOURCE_KEY) ||
        !config.get(DatabricksConstants.DATABRICKS_DATA_SOURCE_KEY).hasNonNull(DatabricksConstants.DATABRICKS_DATA_SOURCE_TYPE_KEY);
  }

  public static Map<DatabricksStorageType, Destination> getTypeToDestination() {
    final DatabricksManagedTablesDestination managedTablesDestination = new DatabricksManagedTablesDestination();
    final DatabricksS3Destination s3Destination = new DatabricksS3Destination();
    final DatabricksAzureBlobStorageDestination azureBlobStorageDestination = new DatabricksAzureBlobStorageDestination();

    return ImmutableMap.of(
        DatabricksStorageType.MANAGED_TABLES_STORAGE, managedTablesDestination,
        DatabricksStorageType.S3_STORAGE, s3Destination,
        DatabricksStorageType.AZURE_BLOB_STORAGE, azureBlobStorageDestination);
  }

}
