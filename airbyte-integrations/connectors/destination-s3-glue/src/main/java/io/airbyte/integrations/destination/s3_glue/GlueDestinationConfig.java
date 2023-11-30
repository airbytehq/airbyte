/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import static io.airbyte.cdk.integrations.destination.s3.constant.S3Constants.ACCESS_KEY_ID;
import static io.airbyte.cdk.integrations.destination.s3.constant.S3Constants.SECRET_ACCESS_KEY;
import static io.airbyte.cdk.integrations.destination.s3.constant.S3Constants.S_3_BUCKET_REGION;
import static io.airbyte.integrations.destination.s3_glue.MetastoreConstants.GLUE_DATABASE;
import static io.airbyte.integrations.destination.s3_glue.MetastoreConstants.SERIALIZATION_LIBRARY;

import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.services.glue.AWSGlue;
import com.amazonaws.services.glue.AWSGlueClient;
import com.amazonaws.services.glue.AWSGlueClientBuilder;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.destination.s3.S3FormatConfig;
import io.airbyte.cdk.integrations.destination.s3.S3FormatConfigs;
import org.apache.commons.lang3.StringUtils;

public class GlueDestinationConfig {

  private String database;

  private String region;

  private String accessKeyId;

  private String secretAccessKey;

  private String serializationLibrary;

  private S3FormatConfig formatConfig;

  private GlueDestinationConfig() {

  }

  private GlueDestinationConfig(String database,
                                String region,
                                String accessKeyId,
                                String secretAccessKey,
                                String serializationLibrary,
                                S3FormatConfig formatConfig) {
    this.database = database;
    this.region = region;
    this.accessKeyId = accessKeyId;
    this.secretAccessKey = secretAccessKey;
    this.serializationLibrary = serializationLibrary;
    this.formatConfig = formatConfig;
  }

  public static GlueDestinationConfig getInstance(JsonNode jsonNode) {
    return new GlueDestinationConfig(
        jsonNode.get(GLUE_DATABASE) != null ? jsonNode.get(GLUE_DATABASE).asText() : null,
        jsonNode.get(S_3_BUCKET_REGION) != null ? jsonNode.get(S_3_BUCKET_REGION).asText() : null,
        jsonNode.get(ACCESS_KEY_ID) != null ? jsonNode.get(ACCESS_KEY_ID).asText() : null,
        jsonNode.get(SECRET_ACCESS_KEY) != null ? jsonNode.get(SECRET_ACCESS_KEY).asText() : null,
        jsonNode.get(SERIALIZATION_LIBRARY) != null ? jsonNode.get(SERIALIZATION_LIBRARY).asText() : "org.openx.data.jsonserde.JsonSerDe",
        S3FormatConfigs.getS3FormatConfig(jsonNode));
  }

  public AWSGlue getAWSGlueInstance() {
    AWSGlueClientBuilder builder = AWSGlueClient.builder();
    AWSCredentialsProvider awsCredentialsProvider;
    if (!StringUtils.isBlank(accessKeyId) && !StringUtils.isBlank(secretAccessKey)) {
      AWSCredentials awsCreds = new BasicAWSCredentials(accessKeyId, secretAccessKey);
      awsCredentialsProvider = new AWSStaticCredentialsProvider(awsCreds);
    } else {
      awsCredentialsProvider = new DefaultAWSCredentialsProviderChain();
    }

    builder.withCredentials(awsCredentialsProvider);

    if (!StringUtils.isBlank(region)) {
      builder.withRegion(region);
    }

    return builder.build();

  }

  public String getDatabase() {
    return database;
  }

  public String getSerializationLibrary() {
    return serializationLibrary;
  }

}
