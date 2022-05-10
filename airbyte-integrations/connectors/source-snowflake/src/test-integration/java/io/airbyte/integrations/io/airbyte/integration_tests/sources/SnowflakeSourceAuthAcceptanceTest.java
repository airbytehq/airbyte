/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.zaxxer.hikari.HikariDataSource;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.snowflake.SnowflakeDataSourceUtils;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Properties;
import javax.sql.DataSource;

public class SnowflakeSourceAuthAcceptanceTest extends SnowflakeSourceAcceptanceTest {

  @Override
  protected DataSource createDataSource() {
    final HikariDataSource dataSource = new HikariDataSource();
    final Properties properties = new Properties();

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

    final var credentials = config.get("credentials");
    try {
      properties.setProperty("client_id", credentials.get("client_id").asText());
      properties.setProperty("client_secret", credentials.get("client_secret").asText());
      properties.setProperty("refresh_token", credentials.get("refresh_token").asText());
      properties.setProperty("host", config.get("host").asText());
      final var accessToken = SnowflakeDataSourceUtils.getAccessTokenUsingRefreshToken(
          config.get("host").asText(), credentials.get("client_id").asText(),
          credentials.get("client_secret").asText(), credentials.get("refresh_token").asText());
      properties.put("authenticator", "oauth");
      properties.put("token", accessToken);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }

    properties.put("warehouse", config.get("warehouse").asText());
    properties.put("account", config.get("host").asText());
    properties.put("role", config.get("role").asText());
    // allows queries to contain any number of statements
    properties.put("MULTI_STATEMENT_COUNT", "0");
    // https://docs.snowflake.com/en/user-guide/jdbc-parameters.html#application
    // identify airbyte traffic to snowflake to enable partnership & optimization opportunities
    properties.put("dataSource.application", "airbyte");
    // Needed for JDK17 - see
    // https://stackoverflow.com/questions/67409650/snowflake-jdbc-driver-internal-error-fail-to-retrieve-row-count-for-first-arrow
    properties.put("JDBC_QUERY_RESULT_FORMAT", "JSON");

    dataSource.setDriverClassName("net.snowflake.client.jdbc.SnowflakeDriver");
    dataSource.setJdbcUrl(jdbcUrl.toString());
    dataSource.setDataSourceProperties(properties);
    return dataSource;
  }

  JsonNode getStaticConfig() {
    return Jsons
        .deserialize(IOs.readFile(Path.of("secrets/config_auth.json")));
  }

  @Override
  public void testBackwardCompatibilityAfterAddingOAuth() throws Exception {
    // this test case is not valid for OAuth method
  }

}
