/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

public final class AzureBlobStorageDestinationConstants {

  public static final String DEFAULT_STORAGE_CONTAINER_NAME = "airbytecontainer";
  public static final String DEFAULT_STORAGE_ENDPOINT_HTTP_PROTOCOL = "https";
  public static final String DEFAULT_STORAGE_ENDPOINT_DOMAIN_NAME = "blob.core.windows.net";
  public static final String DEFAULT_STORAGE_ENDPOINT_FORMAT = "%s://%s.%s";
  public static final int DEFAULT_STORAGE_OUTPUT_BUFFER_SIZE = 5;

  private AzureBlobStorageDestinationConstants() {}

}
