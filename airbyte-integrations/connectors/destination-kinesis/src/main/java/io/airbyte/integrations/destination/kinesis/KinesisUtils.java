/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import java.util.UUID;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.kinesis.KinesisClient;
import software.amazon.awssdk.services.kinesis.model.KinesisException;

public class KinesisUtils {

  private KinesisUtils() {

  }

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

  static KinesisException buildKinesisException(String message, Throwable cause) {
    return (KinesisException) KinesisException.builder()
        .message(message)
        .cause(cause)
        .build();
  }

  static String buildPartitionKey() {
    return UUID.randomUUID().toString();
  }

}
