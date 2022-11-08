/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import com.amazonaws.auth.AWSCredentials;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import org.junit.jupiter.api.Test;

class S3DestinationConfigTest {

  private static final S3DestinationConfig CONFIG = S3DestinationConfig.create("test-bucket", "test-path", "test-region")
      .withEndpoint("test-endpoint")
      .withPathFormat("${STREAM_NAME}/${NAMESPACE}")
      .withAccessKeyCredential("test-key", "test-secret")
      .get();

  @Test
  public void testCreateFromExistingConfig() {
    assertEquals(CONFIG, S3DestinationConfig.create(CONFIG).get());
  }

  @Test
  public void testCreateAndModify() {
    final String newBucketName = "new-bucket";
    final String newBucketPath = "new-path";
    final String newBucketRegion = "new-region";
    final String newEndpoint = "new-endpoint";
    final String newKey = "new-key";
    final String newSecret = "new-secret";

    final S3DestinationConfig modifiedConfig = S3DestinationConfig.create(CONFIG)
        .withBucketName(newBucketName)
        .withBucketPath(newBucketPath)
        .withBucketRegion(newBucketRegion)
        .withEndpoint(newEndpoint)
        .withAccessKeyCredential(newKey, newSecret)
        .get();

    assertNotEquals(CONFIG, modifiedConfig);
    assertEquals(newBucketName, modifiedConfig.getBucketName());
    assertEquals(newBucketPath, modifiedConfig.getBucketPath());
    assertEquals(newBucketRegion, modifiedConfig.getBucketRegion());

    final S3AccessKeyCredentialConfig credentialConfig = (S3AccessKeyCredentialConfig) modifiedConfig.getS3CredentialConfig();
    assertEquals(newKey, credentialConfig.getAccessKeyId());
    assertEquals(newSecret, credentialConfig.getSecretAccessKey());
  }

  @Test
  public void testGetS3DestinationConfigAWS_S3Provider() {
    final JsonNode s3config = Jsons.deserialize("{\n"
        + "  \"s3_bucket_name\": \"paste-bucket-name-here\",\n"
        + "  \"s3_bucket_path\": \"integration-test\",\n"
        + "  \"s3_bucket_region\": \"paste-bucket-region-here\",\n"
        + "  \"access_key_id\": \"paste-access-key-id-here\",\n"
        + "  \"secret_access_key\": \"paste-secret-access-key-here\"\n"
        + "}");

    final S3DestinationConfig result = S3DestinationConfig.getS3DestinationConfig(s3config, StorageProvider.AWS_S3);

    assertThat(result.getEndpoint()).isEmpty();
    assertThat(result.getBucketName()).isEqualTo("paste-bucket-name-here");
    assertThat(result.getBucketPath()).isEqualTo("integration-test");
    assertThat(result.getBucketRegion()).isEqualTo("paste-bucket-region-here");
    assertThat(result.getPathFormat()).isEqualTo("${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_");
    final AWSCredentials awsCredentials = result.getS3CredentialConfig().getS3CredentialsProvider().getCredentials();
    assertThat(awsCredentials.getAWSAccessKeyId()).isEqualTo("paste-access-key-id-here");
    assertThat(awsCredentials.getAWSSecretKey()).isEqualTo("paste-secret-access-key-here");
    assertThat(result.isCheckIntegrity()).isEqualTo(true);
  }

  @Test
  public void testGetS3DestinationConfigCF_R2Provider() {
    final JsonNode s3config = Jsons.deserialize("{\n"
        + "  \"s3_bucket_name\": \"paste-bucket-name-here\",\n"
        + "  \"s3_bucket_path\": \"integration-test\",\n"
        + "  \"account_id\": \"paster-account-id-here\",\n"
        + "  \"access_key_id\": \"paste-access-key-id-here\",\n"
        + "  \"secret_access_key\": \"paste-secret-access-key-here\"\n"
        + "}\n");

    final S3DestinationConfig result = S3DestinationConfig.getS3DestinationConfig(s3config, StorageProvider.CF_R2);

    assertThat(result.getEndpoint()).isEqualTo("https://paster-account-id-here.r2.cloudflarestorage.com");
    assertThat(result.getBucketName()).isEqualTo("paste-bucket-name-here");
    assertThat(result.getBucketPath()).isEqualTo("integration-test");
    assertThat(result.getBucketRegion()).isNull();
    assertThat(result.getPathFormat()).isEqualTo("${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_");
    final AWSCredentials awsCredentials = result.getS3CredentialConfig().getS3CredentialsProvider().getCredentials();
    assertThat(awsCredentials.getAWSAccessKeyId()).isEqualTo("paste-access-key-id-here");
    assertThat(awsCredentials.getAWSSecretKey()).isEqualTo("paste-secret-access-key-here");
    assertThat(result.isCheckIntegrity()).isEqualTo(false);
  }

}
