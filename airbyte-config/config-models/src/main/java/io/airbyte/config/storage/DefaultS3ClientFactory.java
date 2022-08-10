/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.storage;

import com.google.common.base.Preconditions;
import io.airbyte.config.storage.CloudStorageConfigs.S3ApiWorkerStorageConfig;
import io.airbyte.config.storage.CloudStorageConfigs.S3Config;
import java.util.function.Supplier;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;

/**
 * Takes in the constructor our standard format for S3 configuration and provides a factory that
 * uses that configuration to create an S3Client.
 */
public class DefaultS3ClientFactory implements Supplier<S3Client> {

  private final S3Config s3Config;

  public DefaultS3ClientFactory(final S3Config s3Config) {
    validate(s3Config);

    this.s3Config = s3Config;
  }

  private static void validate(final S3Config config) {
    Preconditions.checkNotNull(config);
    validateBase(config);
    Preconditions.checkArgument(!config.getRegion().isBlank());
  }

  static void validateBase(final S3ApiWorkerStorageConfig s3BaseConfig) {
    Preconditions.checkArgument(!s3BaseConfig.getAwsAccessKey().isBlank());
    Preconditions.checkArgument(!s3BaseConfig.getAwsSecretAccessKey().isBlank());
    Preconditions.checkArgument(!s3BaseConfig.getBucketName().isBlank());
    Preconditions.checkArgument(!s3BaseConfig.getBucketName().isBlank());
  }

  @Override
  public S3Client get() {
    final var builder = S3Client.builder();
    builder.credentialsProvider(() -> AwsBasicCredentials.create(s3Config.getAwsAccessKey(), s3Config.getAwsSecretAccessKey()));
    builder.region(Region.of(s3Config.getRegion()));
    return builder.build();
  }

}
