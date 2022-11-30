/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import java.util.UUID;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.kinesis.KinesisClient;
import software.amazon.awssdk.services.kinesis.model.KinesisException;

/**
 * KinesisUtils class providing utility methods for various Kinesis functionalities.
 */
public class KinesisUtils {

  private KinesisUtils() {

  }

  /**
   * Configures and returns a Kinesis client with the provided configuration.
   *
   * @param kinesisConfig used to configure the Kinesis client.
   * @return KinesisClient which can be used to access Kinesis.
   */
  static KinesisClient buildKinesisClient(KinesisConfig kinesisConfig) {
    var kinesisClientBuilder = KinesisClient.builder();

    // configure access credentials
    kinesisClientBuilder.credentialsProvider(StaticCredentialsProvider.create(
        AwsBasicCredentials.create(kinesisConfig.getAccessKey(), kinesisConfig.getPrivateKey())));

    if (kinesisConfig.getRegion() != null && !kinesisConfig.getRegion().isBlank()) {
      // configure access region
      kinesisClientBuilder.region(Region.of(kinesisConfig.getRegion()));
    }

    if (kinesisConfig.getEndpoint() != null) {
      // configure access endpoint
      kinesisClientBuilder.endpointOverride(kinesisConfig.getEndpoint());
    }

    return kinesisClientBuilder.build();
  }

  /**
   * Build a Kinesis exception with the provided message and cause.
   *
   * @param message of the exception
   * @param cause of the exception
   * @return KinesisException to be thrown
   */
  static KinesisException buildKinesisException(String message, Throwable cause) {
    return (KinesisException) KinesisException.builder()
        .message(message)
        .cause(cause)
        .build();
  }

  /**
   * Create random UUID which can be used as a partition key for streaming data.
   *
   * @return String partition key for distributing data across shards.
   */
  static String buildPartitionKey() {
    return UUID.randomUUID().toString();
  }

}
