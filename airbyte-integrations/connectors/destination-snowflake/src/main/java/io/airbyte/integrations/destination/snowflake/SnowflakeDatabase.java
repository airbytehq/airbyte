/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.DefaultJdbcDatabase.CloseableConnectionSupplier;
import io.airbyte.db.jdbc.JdbcDatabase;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Duration;
import java.util.Properties;

/**
 * SnowflakeDatabase contains helpers to create connections to and run queries on Snowflake.
 */
public class SnowflakeDatabase {

  private static final Duration NETWORK_TIMEOUT = Duration.ofMinutes(1);
  private static final Duration QUERY_TIMEOUT = Duration.ofHours(3);

  public static Connection getConnection(JsonNode config) throws SQLException {
    final String connectUrl = String.format("jdbc:snowflake://%s", config.get("host").asText());

    final Properties properties = new Properties();

    properties.put("user", config.get("username").asText());
    properties.put("password", config.get("password").asText());
    properties.put("warehouse", config.get("warehouse").asText());
    properties.put("database", config.get("database").asText());
    properties.put("role", config.get("role").asText());
    properties.put("schema", config.get("schema").asText());

    properties.put("networkTimeout", Math.toIntExact(NETWORK_TIMEOUT.toSeconds()));
    properties.put("queryTimeout", Math.toIntExact(QUERY_TIMEOUT.toSeconds()));
    // allows queries to contain any number of statements.
    properties.put("MULTI_STATEMENT_COUNT", 0);

    // https://docs.snowflake.com/en/user-guide/jdbc-parameters.html#application
    // identify airbyte traffic to snowflake to enable partnership & optimization opportunities
    properties.put("application", "airbyte");

    return DriverManager.getConnection(connectUrl, properties);
  }

  public static JdbcDatabase getDatabase(JsonNode config) {
    return new DefaultJdbcDatabase(new SnowflakeConnectionSupplier(config));
  }

  private static final class SnowflakeConnectionSupplier implements CloseableConnectionSupplier {

    private final JsonNode config;

    public SnowflakeConnectionSupplier(JsonNode config) {
      this.config = config;
    }

    @Override
    public Connection getConnection() throws SQLException {
      return SnowflakeDatabase.getConnection(config);
    }

    @Override
    public void close() {
      // no op.
    }

  }

}
