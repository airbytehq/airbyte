package io.airbyte.workers.storage;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.client.util.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.helpers.LogConfigs;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import software.amazon.awssdk.core.ResponseBytes;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectResponse;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

/**
 * Handles minio and S3.
 */
public class S3WorkerDocStoreClient implements WorkerDocStoreClient {

  private final LogConfigs config;
  private final String bucketName;
  private final Path jobRoot;
  private final S3Client s3Client;

  // todo (cgardens) - log config is the wrong class
  public S3WorkerDocStoreClient(final LogConfigs config, final Path jobRoot) {
    this.config = config;
    this.bucketName = config.getS3LogBucket();
    this.jobRoot = jobRoot;
    this.s3Client = getS3Client(config);
  }

  // config
  // bucket name
  // s3Region
  // s3endpoint

  // todo (cgardens) - dedupe with S3Logs#createS3ClientIfNotExist
  private static S3Client getS3Client(final LogConfigs config) {
      assertValidS3Configuration(configs);

      final var builder = S3Client.builder();

      // Pure S3 Client
      final var s3Region = configs.getS3LogBucketRegion();
      if (!s3Region.isBlank()) {
        builder.region(Region.of(s3Region));
      }

      // The Minio S3 client.
      final var minioEndpoint = configs.getS3MinioEndpoint();
      if (!minioEndpoint.isBlank()) {
        try {
          final var minioUri = new URI(minioEndpoint);
          builder.endpointOverride(minioUri);
          builder.region(Region.US_EAST_1); // Although this is not used, the S3 client will error out if this is not set. Set a stub value.
        } catch (final URISyntaxException e) {
          throw new RuntimeException("Error creating S3 log client to Minio", e);
        }
      }

      return builder.build();
  }

  private static void assertValidS3Configuration(final LogConfigs config) {
    Preconditions.checkNotNull(configs.getAwsAccessKey());
    Preconditions.checkNotNull(configs.getAwsSecretAccessKey());
    Preconditions.checkNotNull(configs.getS3LogBucket());

    // When region is set, endpoint cannot be set and vice versa.
    if (configs.getS3LogBucketRegion().isBlank()) {
      Preconditions.checkNotNull(configs.getS3MinioEndpoint(), "Either S3 region or endpoint needs to be configured.");
    }

    if (configs.getS3MinioEndpoint().isBlank()) {
      Preconditions.checkNotNull(configs.getS3LogBucketRegion(), "Either S3 region or endpoint needs to be configured.");
    }
  }

  @Override
  public void write(final String id, final String document) {
    final PutObjectRequest request = PutObjectRequest.builder()
        .bucket(bucketName)
        .key(id)
        .build();

    s3Client.putObject(request, RequestBody.fromString(Jsons.serialize(document)));
  }

  @Override
  public String read(final String id) {
    final ResponseBytes<GetObjectResponse> objectAsBytes = s3Client.getObjectAsBytes(GetObjectRequest.builder().bucket(bucketName).key(id).build());
    return objectAsBytes.asString(StandardCharsets.UTF_8);
  }
}
