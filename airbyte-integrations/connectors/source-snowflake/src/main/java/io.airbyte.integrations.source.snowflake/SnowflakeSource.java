/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.io.IOException;
import java.sql.JDBCType;
import java.sql.SQLException;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSource.class);
  public static final String DRIVER_CLASS = "net.snowflake.client.jdbc.SnowflakeDriver";
  public static final ScheduledExecutorService SCHEDULED_EXECUTOR_SERVICE = Executors.newScheduledThreadPool(1);

  public SnowflakeSource() {
    super(DRIVER_CLASS, new SnowflakeJdbcStreamingQueryConfiguration(),
        new SnowflakeSourceOperations());
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new SnowflakeSource();
    LOGGER.info("starting source: {}", SnowflakeSource.class);
    new IntegrationRunner(source).run(args);
    SCHEDULED_EXECUTOR_SERVICE.shutdownNow();
    LOGGER.info("completed source: {}", SnowflakeSource.class);
  }

  @Override
  public JdbcDatabase createDatabase(JsonNode config) throws SQLException {
    final DataSource dataSource = SnowflakeDataSourceUtils.createDataSource(config);
    var database = new StreamingJdbcDatabase(dataSource, new SnowflakeSourceOperations(),
        new SnowflakeJdbcStreamingQueryConfiguration());
    quoteString = database.getMetaData().getIdentifierQuoteString();
    return database;
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:snowflake://%s/?",
        config.get("host").asText()));

    // Add required properties
    jdbcUrl.append(String.format(
        "role=%s&warehouse=%s&database=%s&schema=%s&JDBC_QUERY_RESULT_FORMAT=%s&CLIENT_SESSION_KEEP_ALIVE=%s",
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

    if (config.has("credentials") && config.get("credentials").has("auth_type")
        && "OAuth".equals(config.get("credentials").get("auth_type").asText())) {
      // Use OAuth authorization method
      final String accessToken;
      var credentials = config.get("credentials");
      try {
        accessToken = SnowflakeDataSourceUtils.getAccessTokenUsingRefreshToken(
            config.get("host").asText(), credentials.get("client_id").asText(),
            credentials.get("client_secret").asText(), credentials.get("refresh_token").asText());
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
      final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
          .put("connection_properties",
              String.join(";", "authenticator=oauth", "token=" + accessToken))
          .put("jdbc_url", jdbcUrl.toString());
      return Jsons.jsonNode(configBuilder.build());
    } else if (config.has("credentials") && config.get("credentials").has("username")) {
      // Use Username and password authorization method
      var credentials = config.get("credentials");
      final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
          .put("username", credentials.get("username").asText())
          .put("password", credentials.get("password").asText())
          .put("jdbc_url", jdbcUrl.toString());
      LOGGER.info(jdbcUrl.toString());
      return Jsons.jsonNode(configBuilder.build());
    } else if (config.has("password") && config.has("username")) {
      // Use deprecated Username and password authorization method
      final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
          .put("username", config.get("username").asText())
          .put("password", config.get("password").asText())
          .put("jdbc_url", jdbcUrl.toString());
      LOGGER.info(jdbcUrl.toString());
      return Jsons.jsonNode(configBuilder.build());
    } else {
      throw new RuntimeException("Invalid authorization credentials");
    }
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "INFORMATION_SCHEMA");
  }

}
