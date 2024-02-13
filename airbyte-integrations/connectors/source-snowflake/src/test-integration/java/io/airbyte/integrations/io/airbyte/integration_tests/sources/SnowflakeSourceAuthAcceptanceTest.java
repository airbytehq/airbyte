/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.zaxxer.hikari.HikariDataSource;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.snowflake.SnowflakeDataSourceUtils;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Properties;
import javax.sql.DataSource;
import org.junit.jupiter.api.Disabled;

@Disabled("The provided refresh token is invalid.")
public class SnowflakeSourceAuthAcceptanceTest extends SnowflakeSourceAcceptanceTest {

  @Override
  protected DataSource createDataSource() {
    final HikariDataSource dataSource = new HikariDataSource();
    final Properties properties = new Properties();
    config = getStaticConfig();

    final StringBuilder jdbcUrl = new StringBuilder(
        String.format("jdbc:snowflake://%s/?", config.get(JdbcUtils.HOST_KEY).asText()));
    jdbcUrl.append(String.format(
        "role=%s&warehouse=%s&database=%s&schema=%s&CLIENT_METADATA_REQUEST_USE_CONNECTION_CTX=true&JDBC_QUERY_RESULT_FORMAT=%s&CLIENT_SESSION_KEEP_ALIVE=%s",
        config.get("role").asText(),
        config.get("warehouse").asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText(),
        config.get("schema").asText(),
        // Needed for JDK17 - see
        // https://stackoverflow.com/questions/67409650/snowflake-jdbc-driver-internal-error-fail-to-retrieve-row-count-for-first-arrow
        "JSON",
        true));
    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      jdbcUrl.append(config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }

    final var credentials = config.get("credentials");
    try {
      properties.setProperty("client_id", credentials.get("client_id").asText());
      properties.setProperty("client_secret", credentials.get("client_secret").asText());
      properties.setProperty("refresh_token", credentials.get("refresh_token").asText());
      properties.setProperty(JdbcUtils.HOST_KEY, config.get(JdbcUtils.HOST_KEY).asText());
      final var accessToken = SnowflakeDataSourceUtils.getAccessTokenUsingRefreshToken(
          config.get(JdbcUtils.HOST_KEY).asText(), credentials.get("client_id").asText(),
          credentials.get("client_secret").asText(), credentials.get("refresh_token").asText());
      properties.put("authenticator", "oauth");
      properties.put("token", accessToken);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }

    properties.put("warehouse", config.get("warehouse").asText());
    properties.put("account", config.get(JdbcUtils.HOST_KEY).asText());
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
    final JsonNode node = Jsons
        .deserialize(IOs.readFile(Path.of("secrets/config_auth.json")));
    ((ObjectNode) node).put("schema", SCHEMA_NAME);
    return node;
  }

  @Override
  public void testBackwardCompatibilityAfterAddingOAuth() throws Exception {
    // this test case is not valid for OAuth method
  }

}
