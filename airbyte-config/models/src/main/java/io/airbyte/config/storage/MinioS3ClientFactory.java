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

public class MinioS3ClientFactory implements Supplier<S3Client> {

  private final MinioConfig minioConfig;

  public MinioS3ClientFactory(final MinioConfig minioConfig) {
    validate(minioConfig);
    this.minioConfig = minioConfig;
  }

  private static void validate(final MinioConfig config) {
    Preconditions.checkNotNull(config);
    DefaultS3ClientFactory.validateBase(config);
    Preconditions.checkNotNull(config.getMinioEndpoint());
  }

  @Override
  public S3Client get() {
    final var builder = S3Client.builder();

    // The Minio S3 client.
    final var minioEndpoint = minioConfig.getMinioEndpoint();
    try {
      final var minioUri = new URI(minioEndpoint);
      builder.endpointOverride(minioUri);
      builder.region(Region.US_EAST_1); // Although this is not used, the S3 client will error out if this is not set. Set a stub value.
    } catch (final URISyntaxException e) {
      throw new RuntimeException("Error creating S3 log client to Minio", e);
    }

    return builder.build();
  }
}
