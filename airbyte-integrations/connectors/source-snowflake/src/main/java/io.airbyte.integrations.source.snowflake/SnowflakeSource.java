/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.zaxxer.hikari.HikariDataSource;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.io.IOException;
import java.sql.JDBCType;
import java.sql.SQLException;
import java.util.Properties;
import java.util.Set;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSource.class);
  public static final String DRIVER_CLASS = "net.snowflake.client.jdbc.SnowflakeDriver";
  public static boolean isSourceAlive;

  public SnowflakeSource() {
    super(DRIVER_CLASS, new SnowflakeJdbcStreamingQueryConfiguration(),
        new SnowflakeSourceOperations());
  }


  public static void main(final String[] args) throws Exception {
    final Source source = new SnowflakeSource();
    LOGGER.info("starting source: {}", SnowflakeSource.class);
    isSourceAlive = true;
    new IntegrationRunner(source).run(args);
    isSourceAlive = false;
    LOGGER.info("completed source: {}", SnowflakeSource.class);
  }

  @Override
  public JdbcDatabase createDatabase(JsonNode config) throws SQLException {
    final DataSource dataSource = createDataSource(config);
    var database = new StreamingJdbcDatabase(dataSource, JdbcUtils.getDefaultSourceOperations(),
        new SnowflakeJdbcStreamingQueryConfiguration());
    quoteString = database.getMetaData().getIdentifierQuoteString();
    return database;
  }

  private HikariDataSource createDataSource(final JsonNode config) {
    HikariDataSource dataSource = new HikariDataSource();

    final StringBuilder jdbcUrl = new StringBuilder(
        String.format("jdbc:snowflake://%s/?", config.get("host").asText()));
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
    if (config.has("jdbc_url_params")) {
      jdbcUrl.append(config.get("jdbc_url_params").asText());
    }
    Properties properties = new Properties();
    var credentials = config.get("credentials");
    if (credentials.has("auth_type") && "Client".equals(credentials.get("auth_type").asText())) {
      try {

        properties.setProperty("client_id", credentials.get("client_id").asText());
        properties.setProperty("client_secret", credentials.get("client_secret").asText());
        properties.setProperty("refresh_token", credentials.get("refresh_token").asText());
        properties.setProperty("host", config.get("host").asText());
        var accessToken = SnowflakeOAuthUtils.getAccessTokenUsingRefreshToken(
            config.get("host").asText(), credentials.get("client_id").asText(),
            credentials.get("client_secret").asText(), credentials.get("refresh_token").asText());
        properties.put("authenticator", "oauth");
        properties.put("token", accessToken);
        properties.put("account", config.get("host").asText());
        dataSource.setDataSourceProperties(properties);
        new SnowflakeAccessTokenLoader(dataSource).start();
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    } else {
      dataSource.setUsername(credentials.get("username").asText());
      dataSource.setPassword(credentials.get("password").asText());
    }
    properties.put("account", config.get("host").asText());
    dataSource.setDataSourceProperties(properties);
    dataSource.setDriverClassName(DRIVER_CLASS);
    dataSource.setJdbcUrl(jdbcUrl.toString());

    return dataSource;
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

    var credentials = config.get("credentials");
    if (credentials.has("auth_type") && "Client".equals(credentials.get("auth_type").asText())) {
      final String accessToken;
      try {
        accessToken = SnowflakeOAuthUtils.getAccessTokenUsingRefreshToken(
            config.get("host").asText(), credentials.get("client_id").asText(),
            credentials.get("client_secret").asText(), credentials.get("refresh_token").asText());
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
      final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
          .put("connection_properties",
              String.join(";", "user=" + credentials.get("username").asText(),
                  "authenticator=oauth", "token=" + accessToken))
          .put("jdbc_url", jdbcUrl.toString());
      System.out.println(Jsons.jsonNode(configBuilder.build()).asText());
      return Jsons.jsonNode(configBuilder.build());
    } else {
      final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
          .put("username", credentials.get("username").asText())
          .put("password", credentials.get("password").asText())
          .put("jdbc_url", jdbcUrl.toString());
      LOGGER.info(jdbcUrl.toString());
      return Jsons.jsonNode(configBuilder.build());
    }
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "INFORMATION_SCHEMA");
  }

}
