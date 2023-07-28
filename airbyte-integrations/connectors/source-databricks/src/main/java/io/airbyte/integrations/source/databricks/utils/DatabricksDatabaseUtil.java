/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks.utils;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.databricks.DatabricksSourceConfig;

public abstract class DatabricksDatabaseUtil {

  public static JsonNode buildJdbcConfig(final JsonNode config) {
    final DatabricksSourceConfig databricksConfig = DatabricksSourceConfig.get(config);

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, DatabricksConstants.DATABRICKS_USERNAME)
        .put(JdbcUtils.PASSWORD_KEY, databricksConfig.personalAccessToken())
        .put(JdbcUtils.JDBC_URL_KEY, databricksConfig.getDatabricksConnectionString());

    return Jsons.jsonNode(configBuilder.build());
  }
}
