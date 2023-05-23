/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;

public record ClickhouseDestinationDeployTypeConfig(String type, String cluster, boolean replication) {

  public static final String DEFAULT_DEPLOY_TYPE = "clickhouse-cloud";
  public static final String DEFAULT_CLUSTER_NAME = "default";
  public static final boolean DEFAULT_REPLICATION = false;

  public static ClickhouseDestinationDeployTypeConfig get(final JsonNode config) {
    return new ClickhouseDestinationDeployTypeConfig(
        config.has("deploy_type") ? config.get("deploy_type").asText() : DEFAULT_DEPLOY_TYPE,
        config.has("cluster") ? config.get("cluster").asText() : DEFAULT_CLUSTER_NAME,
        config.has("replication") ? config.get("replication").asBoolean() : DEFAULT_REPLICATION);
  }

  public static ClickhouseDestinationDeployTypeConfig defaultConfig() {
    return new ClickhouseDestinationDeployTypeConfig(DEFAULT_DEPLOY_TYPE, DEFAULT_CLUSTER_NAME,
        DEFAULT_REPLICATION);
  }

}
