/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.storage;

import com.google.api.client.util.Preconditions;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.config.storage.CloudStorageConfigs.GcsConfig;
import java.util.function.Supplier;

/**
 * Takes in the constructor our standard format for gcs configuration and provides a factory that
 * uses that configuration to create a GCS client (Storage).
 */
public class DefaultGcsClientFactory implements Supplier<Storage> {

  public DefaultGcsClientFactory(final GcsConfig config) {
    validate(config);
  }

  private static void validate(final GcsConfig config) {
    Preconditions.checkArgument(!config.getBucketName().isBlank());
    Preconditions.checkArgument(!config.getGoogleApplicationCredentials().isBlank());
  }

  @Override
  public Storage get() {
    return StorageOptions.getDefaultInstance().getService();
  }

}
