/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.Request;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.SignerFactory;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.handlers.RequestHandler2;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.Credentials;
import io.airbyte.integrations.destination.gcs.credential.GcsCredentialConfig;
import io.airbyte.integrations.destination.gcs.credential.GcsCredentialConfigs;
import io.airbyte.integrations.destination.gcs.credential.GcsHmacKeyCredentialConfig;
import io.airbyte.integrations.destination.gcs.signer.CustomGCPSigner;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3DestinationConstants;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.S3FormatConfigs;
import io.airbyte.integrations.destination.gcs.credential.GCPOauth2Adapter;

/**
 * Currently we always reuse the S3 client for GCS. So the GCS config extends from the S3 config.
 * This may change in the future.
 */
public class GcsDestinationConfig extends S3DestinationConfig {

  private static final String GCS_ENDPOINT = "https://storage.googleapis.com";

  private final GcsCredentialConfig credentialConfig;

  public GcsDestinationConfig(final String bucketName,
                              final String bucketPath,
                              final String bucketRegion,
                              final GcsCredentialConfig credentialConfig,
                              final S3FormatConfig formatConfig) {
    super(GCS_ENDPOINT,
        bucketName,
        bucketPath,
        bucketRegion,
        S3DestinationConstants.DEFAULT_PATH_FORMAT,
        credentialConfig.getS3CredentialConfig().orElseThrow(),
        S3DestinationConstants.DEFAULT_PART_SIZE_MB,
        formatConfig,
        null);
    this.credentialConfig = credentialConfig;
  }

  public static GcsDestinationConfig getGcsDestinationConfig(final JsonNode config) {
    return new GcsDestinationConfig(
        config.get("gcs_bucket_name").asText(),
        config.get("gcs_bucket_path").asText(),
        config.get("gcs_bucket_region").asText(),
        GcsCredentialConfigs.getCredentialConfig(config),
        S3FormatConfigs.getS3FormatConfig(config));
  }
  public static GcsDestinationConfig getGcsDestinationConfig(final JsonNode config, final Credentials googleCredentials) {
    return new GcsDestinationConfig(
        config.get("gcs_bucket_name").asText(),
        config.get("gcs_bucket_path").asText(),
        config.get("gcs_bucket_region").asText(),
        GcsCredentialConfigs.getCredentialConfig(config, googleCredentials),
        S3FormatConfigs.getS3FormatConfig(config));
  }

  @Override
  protected AmazonS3 createS3Client() {
    switch (credentialConfig.getCredentialType()) {
      case HMAC_KEY -> {
        final GcsHmacKeyCredentialConfig hmacKeyCredential = (GcsHmacKeyCredentialConfig) credentialConfig;
        final BasicAWSCredentials awsCreds = new BasicAWSCredentials(hmacKeyCredential.getHmacKeyAccessId(), hmacKeyCredential.getHmacKeySecret());
        return AmazonS3ClientBuilder.standard()
            .withEndpointConfiguration(
                new AwsClientBuilder.EndpointConfiguration(GCS_ENDPOINT, getBucketRegion()))
            .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
            .build();
      }
      case OAUTH2 -> {
        final String signerPath = "io.airbyte.integrations.destination.gcs.signer.CustomGCPSigner";
        SignerFactory.registerSigner(signerPath, CustomGCPSigner.class);
        ClientConfiguration clientConfig = new ClientConfiguration();
        clientConfig.setSignerOverride(signerPath);
        final GCPOauth2Adapter googleCredentials = (GCPOauth2Adapter) credentialConfig;
        return AmazonS3ClientBuilder.standard().withClientConfiguration(clientConfig)
            .withEndpointConfiguration(
                new AwsClientBuilder.EndpointConfiguration(GCS_ENDPOINT, getBucketRegion()))
            .withRequestHandlers(new RequestHandler2() {
              @Override
              public void beforeRequest(Request<?> request) {
                request.addHeader("x-goog-project-id", "dataline-integration-testing");
              }
            }).withCredentials(new AWSStaticCredentialsProvider(googleCredentials)).build();
      }
      default -> throw new IllegalArgumentException("Unsupported credential type: " + credentialConfig.getCredentialType().name());
    }
  }

  public GcsCredentialConfig getGcsCredentialConfig() {
    return credentialConfig;
  }

}
