/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import java.time.Duration;
import java.util.Map;
import javax.sql.DataSource;

/**
 * SnowflakeDatabase contains helpers to create connections to and run queries on Snowflake.
 */
public class SnowflakeDatabase {

  private static final Duration NETWORK_TIMEOUT = Duration.ofMinutes(1);
  private static final Duration QUERY_TIMEOUT = Duration.ofHours(3);
  private static final SnowflakeSQLNameTransformer nameTransformer = new SnowflakeSQLNameTransformer();
  private static final String DRIVER_CLASS_NAME = "net.snowflake.client.jdbc.SnowflakeDriver";

  private static DataSource createDataSource(final JsonNode config) {
    final String host = config.get("host").asText();
    final String username = config.get("username").asText();
    final String password = config.get("password").asText();

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:snowflake://%s/?", host));
    if (config.has("jdbc_url_params")) {
      jdbcUrl.append(config.get("jdbc_url_params").asText());
    }

    final Map<String, String> properties = new ImmutableMap.Builder<String, String>()
        .put("warehouse", config.get("warehouse").asText())
        .put("database", config.get("database").asText())
        .put("role", config.get("role").asText())
        .put("schema", nameTransformer.getIdentifier(config.get("schema").asText()))
        .put("networkTimeout", String.valueOf(Math.toIntExact(NETWORK_TIMEOUT.toSeconds())))
        .put("queryTimeout", String.valueOf(Math.toIntExact(QUERY_TIMEOUT.toSeconds())))
        // allows queries to contain any number of statements
        .put("MULTI_STATEMENT_COUNT", "0")
        // https://docs.snowflake.com/en/user-guide/jdbc-parameters.html#application
        // identify airbyte traffic to snowflake to enable partnership & optimization opportunities
        .put("application", "airbyte")
        // Needed for JDK17 - see
        // https://stackoverflow.com/questions/67409650/snowflake-jdbc-driver-internal-error-fail-to-retrieve-row-count-for-first-arrow
        .put("JDBC_QUERY_RESULT_FORMAT", "JSON")
        .build();

    return Databases.createBasicDataSource(username, password, jdbcUrl.toString(), DRIVER_CLASS_NAME, properties);
  }

  public static JdbcDatabase getDatabase(final JsonNode config) {
    final DataSource dataSource = createDataSource(config);
    return new DefaultJdbcDatabase(dataSource);
  }

}
