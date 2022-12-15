/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.storage;

import com.google.api.client.util.Preconditions;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.config.storage.CloudStorageConfigs.GcsConfig;
import java.io.ByteArrayInputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.function.Supplier;

/**
 * Takes in the constructor our standard format for gcs configuration and provides a factory that
 * uses that configuration to create a GCS client (Storage).
 */
@SuppressWarnings("PMD.AvoidThrowingRawExceptionTypes")
public class DefaultGcsClientFactory implements Supplier<Storage> {

  private final GcsConfig config;

  public DefaultGcsClientFactory(final GcsConfig config) {
    validate(config);
    this.config = config;
  }

  private static void validate(final GcsConfig config) {
    Preconditions.checkArgument(!config.getBucketName().isBlank());
    Preconditions.checkArgument(!config.getGoogleApplicationCredentials().isBlank());
  }

  @Override
  public Storage get() {
    try {
      final var credentialsByteStream = new ByteArrayInputStream(Files.readAllBytes(Path.of(config.getGoogleApplicationCredentials())));
      final var credentials = ServiceAccountCredentials.fromStream(credentialsByteStream);
      return StorageOptions.newBuilder().setCredentials(credentials).build().getService();
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

}
