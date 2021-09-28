/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;

public class DynamodbDestinationConfig {

  private final String endpoint;
  private final String tableName;
  private final String accessKeyId;
  private final String secretAccessKey;
  private final String region;

  public DynamodbDestinationConfig(
                                   String endpoint,
                                   String tableName,
                                   String region,
                                   String accessKeyId,
                                   String secretAccessKey) {
    this.endpoint = endpoint;
    this.tableName = tableName;
    this.region = region;
    this.accessKeyId = accessKeyId;
    this.secretAccessKey = secretAccessKey;
  }

  public static DynamodbDestinationConfig getDynamodbDestinationConfig(JsonNode config) {
    return new DynamodbDestinationConfig(
        config.get("dynamodb_endpoint") == null ? "" : config.get("dynamodb_endpoint").asText(),
        config.get("dynamodb_table_name").asText(),
        config.get("dynamodb_region").asText(),
        config.get("access_key_id").asText(),
        config.get("secret_access_key").asText());
  }

  public String getEndpoint() {
    return endpoint;
  }

  public String getAccessKeyId() {
    return accessKeyId;
  }

  public String getSecretAccessKey() {
    return secretAccessKey;
  }

  public String getRegion() {
    return region;
  }

  public String getTableName() {
    return tableName;
  }

}
