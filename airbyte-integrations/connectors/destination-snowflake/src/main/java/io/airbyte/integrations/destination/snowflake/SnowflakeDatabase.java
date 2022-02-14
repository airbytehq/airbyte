/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static java.util.stream.Collectors.joining;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.DefaultJdbcDatabase.CloseableConnectionSupplier;
import io.airbyte.db.jdbc.JdbcDatabase;
import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpRequest.BodyPublisher;
import java.net.http.HttpRequest.BodyPublishers;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Duration;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * SnowflakeDatabase contains helpers to create connections to and run queries on Snowflake.
 */
public class SnowflakeDatabase {

  private static final Duration NETWORK_TIMEOUT = Duration.ofMinutes(1);
  private static final Duration QUERY_TIMEOUT = Duration.ofHours(3);
  private static final SnowflakeSQLNameTransformer nameTransformer = new SnowflakeSQLNameTransformer();
  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeDatabase.class);

  private static final String REFRESH_TOKEN_URL = "https://%s/oauth/token-request";
  private static final HttpClient httpClient = HttpClient.newBuilder()
      .version(HttpClient.Version.HTTP_2)
      .connectTimeout(Duration.ofSeconds(10))
      .build();

  public static Connection getConnection(final JsonNode config) throws SQLException {

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:snowflake://%s/?",
        config.get("host").asText()));

    final Properties properties = new Properties();

    final JsonNode credentials = config.get("credentials");
    if (credentials.has("auth_type") && "Client".equals(credentials.get("auth_type").asText())) {
      // OAuth login option is selected on UI
      final String accessToken;
      try {
        // accessToken is only valid for 10 minutes. So we need to get a new one before processing new
        // stream
        accessToken = getAccessTokenUsingRefreshToken(config.get("host").asText(), credentials.get("client_id").asText(),
            credentials.get("client_secret").asText(), credentials.get("refresh_token").asText());
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
      properties.put("authenticator", "oauth");
      properties.put("token", accessToken);
    } else {
      // Username and pass login option is selected on UI
      properties.put("user", credentials.get("username").asText());
      properties.put("password", credentials.get("password").asText());
    }

    properties.put("warehouse", config.get("warehouse").asText());
    properties.put("database", config.get("database").asText());
    properties.put("role", config.get("role").asText());
    properties.put("schema", nameTransformer.getIdentifier(config.get("schema").asText()));

    properties.put("networkTimeout", Math.toIntExact(NETWORK_TIMEOUT.toSeconds()));
    properties.put("queryTimeout", Math.toIntExact(QUERY_TIMEOUT.toSeconds()));
    // allows queries to contain any number of statements.
    properties.put("MULTI_STATEMENT_COUNT", 0);

    // https://docs.snowflake.com/en/user-guide/jdbc-parameters.html#application
    // identify airbyte traffic to snowflake to enable partnership & optimization opportunities
    properties.put("application", "airbyte");
    // Needed for JDK17 - see
    // https://stackoverflow.com/questions/67409650/snowflake-jdbc-driver-internal-error-fail-to-retrieve-row-count-for-first-arrow
    properties.put("JDBC_QUERY_RESULT_FORMAT", "JSON");

    // https://docs.snowflake.com/en/user-guide/jdbc-configure.html#jdbc-driver-connection-string
    if (config.has("jdbc_url_params")) {
      jdbcUrl.append(config.get("jdbc_url_params").asText());
    }

    LOGGER.info(jdbcUrl.toString());

    return DriverManager.getConnection(jdbcUrl.toString(), properties);
  }

  private static String getAccessTokenUsingRefreshToken(final String hostName,
                                                        final String clientId,
                                                        final String clientSecret,
                                                        final String refreshCode)
      throws IOException {
    final var refreshTokenUri = String.format(REFRESH_TOKEN_URL, hostName);
    final Map<String, String> requestBody = new HashMap<>();
    requestBody.put("grant_type", "refresh_token");
    requestBody.put("refresh_token", refreshCode);

    try {
      BodyPublisher bodyPublisher = BodyPublishers.ofString(requestBody.keySet().stream()
          .map(key -> key + "=" + URLEncoder.encode(requestBody.get(key), StandardCharsets.UTF_8))
          .collect(joining("&")));

      final HttpRequest request = HttpRequest.newBuilder()
          .POST(bodyPublisher)
          .uri(URI.create(refreshTokenUri))
          .header("Content-Type", "application/x-www-form-urlencoded")
          .header("Accept", "application/json")
          .header("Authorization", "Basic " + new String(
              Base64.getEncoder().encode((clientId + ":" + clientSecret).getBytes())))
          .build();

      final HttpResponse<String> response = httpClient.send(request,
          HttpResponse.BodyHandlers.ofString());

      final JsonNode jsonResponse = Jsons.deserialize(response.body());
      if (jsonResponse.has("access_token")) {
        return jsonResponse.get("access_token").asText();
      } else {
        throw new RuntimeException("Failed to obtain accessToken using refresh token. " + jsonResponse);
      }
    } catch (final InterruptedException e) {
      throw new IOException("Failed to refreshToken", e);
    }
  }

  public static JdbcDatabase getDatabase(final JsonNode config) {
    return new DefaultJdbcDatabase(new SnowflakeConnectionSupplier(config));
  }

  private static final class SnowflakeConnectionSupplier implements CloseableConnectionSupplier {

    private final JsonNode config;

    public SnowflakeConnectionSupplier(final JsonNode config) {
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
