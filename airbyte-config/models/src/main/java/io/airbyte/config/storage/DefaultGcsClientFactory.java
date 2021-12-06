package io.airbyte.config.storage;

import com.google.api.client.util.Preconditions;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.config.storage.CloudStorageConfigs.GcsConfig;
import java.util.function.Supplier;

public class DefaultGcsClientFactory implements Supplier<Storage> {

  public DefaultGcsClientFactory(final GcsConfig config) {
    validate(config);
  }

  private static void validate(final GcsConfig config) {
      Preconditions.checkNotNull(config.getBucketName());
      Preconditions.checkNotNull(config.getGoogleApplicationCredentials());
  }

  @Override
  public Storage get() {
    return StorageOptions.getDefaultInstance().getService();
  }
}
