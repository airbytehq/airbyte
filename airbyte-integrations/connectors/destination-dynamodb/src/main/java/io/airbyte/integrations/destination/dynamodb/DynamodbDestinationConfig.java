/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;

public class DynamodbDestinationConfig {

  private final String endpoint;
  private final String tableNamePrefix;
  private final String accessKeyId;
  private final String secretAccessKey;
  private final String region;

  public DynamodbDestinationConfig(
                                   final String endpoint,
                                   final String tableNamePrefix,
                                   final String region,
                                   final String accessKeyId,
                                   final String secretAccessKey) {
    this.endpoint = endpoint;
    this.tableNamePrefix = tableNamePrefix;
    this.region = region;
    this.accessKeyId = accessKeyId;
    this.secretAccessKey = secretAccessKey;
  }

  public static DynamodbDestinationConfig getDynamodbDestinationConfig(final JsonNode config) {
    return new DynamodbDestinationConfig(
        config.get("dynamodb_endpoint") == null ? "" : config.get("dynamodb_endpoint").asText(),
        config.get("dynamodb_table_name_prefix").asText(),
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

  public String getTableNamePrefix() {
    return tableNamePrefix;
  }

}
