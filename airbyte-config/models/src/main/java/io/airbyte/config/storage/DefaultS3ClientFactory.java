package io.airbyte.config.storage;

import com.google.common.base.Preconditions;
import io.airbyte.config.storage.CloudStorageConfigs.MinioConfig;
import io.airbyte.config.storage.CloudStorageConfigs.S3Config;
import io.airbyte.config.storage.CloudStorageConfigs.S3LikeWorkerStorageConfig;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.function.Supplier;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;

public class DefaultS3ClientFactory implements Supplier<S3Client> {

  private final S3Config s3Config;

  public DefaultS3ClientFactory(final S3Config s3Config) {
    validate(s3Config);

    this.s3Config = s3Config;
  }

  private static void validate(final S3Config config) {
    Preconditions.checkNotNull(config);
    validateBase(config);
    Preconditions.checkNotNull(config.getRegion());
  }

  static void validateBase(final S3LikeWorkerStorageConfig s3BaseConfig) {
    Preconditions.checkNotNull(s3BaseConfig.getAwsAccessKey());
    Preconditions.checkNotNull(s3BaseConfig.getAwsSecretAccessKey());
    Preconditions.checkNotNull(s3BaseConfig.getBucketName());
    Preconditions.checkNotNull(s3BaseConfig.getBucketName());
  }

  @Override
  public S3Client get() {
    final var builder = S3Client.builder();
    builder.region(Region.of(s3Config.getRegion()));
    return builder.build();
  }
}
