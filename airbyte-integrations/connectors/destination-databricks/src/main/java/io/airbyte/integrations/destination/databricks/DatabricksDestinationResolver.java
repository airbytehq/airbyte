/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.base.Destination;
import java.util.Map;

public class DatabricksDestinationResolver {

  public static DatabricksStorageType getTypeFromConfig(final JsonNode config) {
    if (isS3Copy(config)) {
      return DatabricksStorageType.S3;
    } else if (isAzureBlobCopy(config)) {
      return DatabricksStorageType.AZURE_BLOB_STORAGE;
    } else {
      throw new IllegalArgumentException("S3 or Azure Blob Storage configurations must be provided");
    }
  }

  public static boolean isS3Copy(final JsonNode config) {
    return config.has("data_source") && config.get("data_source").isObject() && config.get("data_source").has("s3_bucket_name");
  }

  public static boolean isAzureBlobCopy(final JsonNode config) {
    return config.has("data_source") && config.get("data_source").isObject()
        && config.get("data_source").has("azure_blob_storage_account_name");
  }

  public static Map<DatabricksStorageType, Destination> getTypeToDestination() {
    final DatabricksS3Destination s3Destination = new DatabricksS3Destination();
    final DatabricksAzureBlobStorageDestination azureBlobStorageDestination = new DatabricksAzureBlobStorageDestination();

    return ImmutableMap.of(
        DatabricksStorageType.S3, s3Destination,
        DatabricksStorageType.AZURE_BLOB_STORAGE, azureBlobStorageDestination);
  }

}
