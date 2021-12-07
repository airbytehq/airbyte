/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.s3.writer.ProductionWriterFactory;
import io.airbyte.integrations.destination.s3.writer.S3WriterFactory;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.UUID;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class S3Destination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3Destination.class);

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new S3Destination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      attemptS3WriteAndDelete(S3DestinationConfig.getS3DestinationConfig(config), config.get("s3_bucket_path").asText());
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to access the S3 bucket: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect to the S3 bucket with the provided configuration. \n" + e
              .getMessage());
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
      final ConfiguredAirbyteCatalog configuredCatalog,
      final Consumer<AirbyteMessage> outputRecordCollector) {
    final S3WriterFactory formatterFactory = new ProductionWriterFactory();
    return new S3Consumer(S3DestinationConfig.getS3DestinationConfig(config), configuredCatalog, formatterFactory, outputRecordCollector);
  }

  /**
   * Note that this method completely ignores s3Config.getBucketPath(), in favor of the bucketPath parameter.
   */
  public static void attemptS3WriteAndDelete(final S3DestinationConfig s3Config, final String bucketPath) {
    attemptS3WriteAndDelete(s3Config, bucketPath, getAmazonS3(s3Config));
  }

  @VisibleForTesting
  static void attemptS3WriteAndDelete(final S3DestinationConfig s3Config, final String bucketPath, final AmazonS3 s3) {
    final var prefix = bucketPath.isEmpty() ? "" : bucketPath + (bucketPath.endsWith("/") ? "" : "/");
    final String outputTableName = prefix + "_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", "");
    attemptWriteAndDeleteS3Object(s3Config, outputTableName, s3);
  }

  private static void attemptWriteAndDeleteS3Object(final S3DestinationConfig s3Config, final String outputTableName, final AmazonS3 s3) {
    final var s3Bucket = s3Config.getBucketName();

    s3.putObject(s3Bucket, outputTableName, "check-content");
    s3.deleteObject(s3Bucket, outputTableName);
  }

  public static AmazonS3 getAmazonS3(final S3DestinationConfig s3Config) {
    final var endpoint = s3Config.getEndpoint();
    final var region = s3Config.getBucketRegion();
    final var accessKeyId = s3Config.getAccessKeyId();
    final var secretAccessKey = s3Config.getSecretAccessKey();

    final var awsCreds = new BasicAWSCredentials(accessKeyId, secretAccessKey);

    if (endpoint.isEmpty()) {
      return AmazonS3ClientBuilder.standard()
          .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
          .withRegion(s3Config.getBucketRegion())
          .build();

    } else {

      final ClientConfiguration clientConfiguration = new ClientConfiguration();
      clientConfiguration.setSignerOverride("AWSS3V4SignerType");

      return AmazonS3ClientBuilder
          .standard()
          .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(endpoint, region))
          .withPathStyleAccessEnabled(true)
          .withClientConfiguration(clientConfiguration)
          .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
          .build();
    }
  }
}
