/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import io.airbyte.integrations.destination.gcs.credential.GcsHmacKeyCredentialConfig;

public class GcsS3Helper {

  private static final String GCS_ENDPOINT = "https://storage.googleapis.com";

  public static AmazonS3 getGcsS3Client(GcsDestinationConfig gcsDestinationConfig) {
    GcsHmacKeyCredentialConfig hmacKeyCredential = (GcsHmacKeyCredentialConfig) gcsDestinationConfig.getCredentialConfig();
    BasicAWSCredentials awsCreds = new BasicAWSCredentials(hmacKeyCredential.getHmacKeyAccessId(), hmacKeyCredential.getHmacKeySecret());

    return AmazonS3ClientBuilder.standard()
        .withEndpointConfiguration(
            new AwsClientBuilder.EndpointConfiguration(GCS_ENDPOINT, gcsDestinationConfig.getBucketRegion()))
        .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
        .build();
  }

}
