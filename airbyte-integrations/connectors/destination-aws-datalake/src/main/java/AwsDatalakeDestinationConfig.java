/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.aws_datalake;

import com.fasterxml.jackson.databind.JsonNode;

public class AwsDatalakeDestinationConfig {

  private final String awsAccountId;
  private final String region;
  private final String accessKeyId;
  private final String secretAccessKey;
  private final String bucketName;
  private final String prefix;
  private final String databaseName;

  public AwsDatalakeDestinationConfig(String awsAccountId,
                                      String region,
                                      String accessKeyId,
                                      String secretAccessKey,
                                      String bucketName,
                                      String prefix,
                                      String databaseName) {
    this.awsAccountId = awsAccountId;
    this.region = region;
    this.accessKeyId = accessKeyId;
    this.secretAccessKey = secretAccessKey;
    this.bucketName = bucketName;
    this.prefix = prefix;
    this.databaseName = databaseName;

  }

  public static AwsDatalakeDestinationConfig getAwsDatalakeDestinationConfig(JsonNode config) {

    final String aws_access_key_id = config.path("credentials").get("aws_access_key_id").asText();
    final String aws_secret_access_key = config.path("credentials").get("aws_secret_access_key").asText();

    return new AwsDatalakeDestinationConfig(
        config.get("aws_account_id").asText(),
        config.get("region").asText(),
        aws_access_key_id,
        aws_secret_access_key,
        config.get("bucket_name").asText(),
        config.get("bucket_prefix").asText(),
        config.get("lakeformation_database_name").asText());
  }

  public String getAwsAccountId() {
    return awsAccountId;
  }

  public String getRegion() {
    return region;
  }

  public String getAccessKeyId() {
    return accessKeyId;
  }

  public String getSecretAccessKey() {
    return secretAccessKey;
  }

  public String getBucketName() {
    return bucketName;
  }

  public String getPrefix() {
    return prefix;
  }

  public String getDatabaseName() {
    return databaseName;
  }

}
