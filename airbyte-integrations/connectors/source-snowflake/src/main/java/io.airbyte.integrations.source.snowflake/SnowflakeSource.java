/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.sql.JDBCType;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSource.class);
  public static final String DRIVER_CLASS = "net.snowflake.client.jdbc.SnowflakeDriver";

  public SnowflakeSource() {
    super(DRIVER_CLASS, new SnowflakeJdbcStreamingQueryConfiguration(), new SnowflakeSourceOperations());
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new SnowflakeSource();
    LOGGER.info("starting source: {}", SnowflakeSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", SnowflakeSource.class);
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:snowflake://%s/?",
        config.get("host").asText()));

    // Add required properties
    jdbcUrl.append(String.format("role=%s&warehouse=%s&database=%s&schema=%s&JDBC_QUERY_RESULT_FORMAT=%s&CLIENT_SESSION_KEEP_ALIVE=%s",
        config.get("role").asText(),
        config.get("warehouse").asText(),
        config.get("database").asText(),
        config.get("schema").asText(),
        // Needed for JDK17 - see
        // https://stackoverflow.com/questions/67409650/snowflake-jdbc-driver-internal-error-fail-to-retrieve-row-count-for-first-arrow
        "JSON",
        true));

    // https://docs.snowflake.com/en/user-guide/jdbc-configure.html#jdbc-driver-connection-string
    if (config.has("jdbc_url_params")) {
      jdbcUrl.append("&").append(config.get("jdbc_url_params").asText());
    }

    LOGGER.info(jdbcUrl.toString());

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("password", config.get("password").asText())
        .put("jdbc_url", jdbcUrl.toString());

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "INFORMATION_SCHEMA");
  }

}
