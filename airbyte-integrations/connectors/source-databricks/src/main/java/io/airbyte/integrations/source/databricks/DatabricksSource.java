/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.db.jdbc.streaming.NoOpStreamingQueryConfig;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.sql.JDBCType;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabricksSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabricksSource.class);

  // TODO insert your driver name. Ex: "com.microsoft.sqlserver.jdbc.SQLServerDriver"
  static final String DRIVER_CLASS = DatabaseDriver.DATABRICKS.getDriverClassName();

  public DatabricksSource() {
    // TODO: if the JDBC driver does not support custom fetch size, use NoOpStreamingQueryConfig
    // instead of AdaptiveStreamingQueryConfig.
    super(DRIVER_CLASS, NoOpStreamingQueryConfig::new, new DatabricksSourceOperations());
  }

  // TODO The config is based on spec.json, update according to your DB
  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    // TODO create DB config. Ex: "Jsons.jsonNode(ImmutableMap.builder().put("username",
    // userName).put("password", pas)...build());
    JsonNode configJson = buildUsernamePasswordConfig(config);
    LOGGER.info(configJson.toString());

    return configJson;

    // return null;
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    // TODO Add tables to exclude, Ex "INFORMATION_SCHEMA", "sys", "spt_fallback_db", etc
    return Set.of("system", "information_schema", "INFORMATION_SCHEMA");
  }

  private JsonNode buildUsernamePasswordConfig(final JsonNode config) {
    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, config.get(JdbcUtils.JDBC_URL_KEY).asText());
    return Jsons.jsonNode(configBuilder.build());
    // return Jsons.jsonNode(DatabricksSourceConfig.get(config));
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new DatabricksSource();
    LOGGER.info("starting source: {}", DatabricksSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", DatabricksSource.class);
  }

}
