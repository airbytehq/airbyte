/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import static java.util.stream.Collectors.joining;

import com.fasterxml.jackson.databind.JsonNode;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpRequest.BodyPublisher;
import java.net.http.HttpRequest.BodyPublishers;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeDataSourceUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeDataSourceUtils.class);
  private static final int PAUSE_BETWEEN_TOKEN_REFRESH_MIN = 7; // snowflake access token's TTL is 10min and can't be modified
  private static final String REFRESH_TOKEN_URL = "https://%s/oauth/token-request";
  private static final HttpClient httpClient = HttpClient.newBuilder()
      .version(HttpClient.Version.HTTP_2)
      .connectTimeout(Duration.ofSeconds(10))
      .build();

  /**
   * Snowflake OAuth access token expires in 10 minutes. For the cases when sync duration is more than
   * 10 min, it requires updating 'token' property after the start of connection pool.
   * HikariDataSource brings support for this requirement.
   *
   * @param config source config JSON
   * @return datasource
   */
  public static HikariDataSource createDataSource(final JsonNode config) {
    HikariConfig hikariConfig = new HikariConfig();
    final String jdbcUrl = buildJDBCUrl(config);
    hikariConfig.setJdbcUrl(jdbcUrl);

    if (config.has("credentials") && config.get("credentials").has("auth_type")
        && "OAuth".equals(config.get("credentials").get("auth_type").asText())) {
      LOGGER.info("Authorization mode is OAuth");
      hikariConfig.setDataSourceProperties(buildAuthProperties(config));
      // thread to keep the refresh token up to date
      SnowflakeSource.SCHEDULED_EXECUTOR_SERVICE.scheduleAtFixedRate(getRefreshTokenTask(hikariConfig),
          PAUSE_BETWEEN_TOKEN_REFRESH_MIN, PAUSE_BETWEEN_TOKEN_REFRESH_MIN, TimeUnit.MINUTES);
    } else if (config.has("credentials") && config.get("credentials").has("password")) {
      LOGGER.info("Authorization mode is 'Username and password'");
      populateUsernamePasswordConfig(hikariConfig, config.get("credentials"));
    } else if (config.has("password") && config.has("username")) {
      LOGGER.info("Authorization mode is deprecated 'Username and password'. Please update your source configuration");
      populateUsernamePasswordConfig(hikariConfig, config);
    }

    return new HikariDataSource(hikariConfig);
  }

  /**
   * Method to make request for a new access token using refresh token and client credentials.
   *
   * @return access token
   */
  public static String getAccessTokenUsingRefreshToken(final String hostName,
                                                       final String clientId,
                                                       final String clientSecret,
                                                       final String refreshCode)
      throws IOException {
    final var refreshTokenUri = String.format(REFRESH_TOKEN_URL, hostName);
    final Map<String, String> requestBody = new HashMap<>();
    requestBody.put("grant_type", "refresh_token");
    requestBody.put("refresh_token", refreshCode);

    try {
      final BodyPublisher bodyPublisher = BodyPublishers.ofString(requestBody.keySet().stream()
          .map(key -> key + "=" + URLEncoder.encode(requestBody.get(key), StandardCharsets.UTF_8))
          .collect(joining("&")));

      final byte[] authorization = Base64.getEncoder()
          .encode((clientId + ":" + clientSecret).getBytes(StandardCharsets.UTF_8));

      final HttpRequest request = HttpRequest.newBuilder()
          .POST(bodyPublisher)
          .uri(URI.create(refreshTokenUri))
          .header("Content-Type", "application/x-www-form-urlencoded")
          .header("Accept", "application/json")
          .header("Authorization", "Basic " + new String(authorization, StandardCharsets.UTF_8))
          .build();

      final HttpResponse<String> response = httpClient.send(request,
          HttpResponse.BodyHandlers.ofString());

      final JsonNode jsonResponse = Jsons.deserialize(response.body());
      if (jsonResponse.has("access_token")) {
        return jsonResponse.get("access_token").asText();
      } else {
        throw new RuntimeException(
            "Failed to obtain accessToken using refresh token. " + jsonResponse);
      }
    } catch (final InterruptedException e) {
      throw new IOException("Failed to refreshToken", e);
    }
  }

  public static String buildJDBCUrl(JsonNode config) {
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
    return jdbcUrl.toString();
  }

  private static Runnable getRefreshTokenTask(final HikariConfig hikariConfig) {
    return () -> {
      LOGGER.info("Refresh token process started");
      var props = hikariConfig.getDataSourceProperties();
      try {
        var token = getAccessTokenUsingRefreshToken(props.getProperty("host"),
            props.getProperty("client_id"), props.getProperty("client_secret"),
            props.getProperty("refresh_token"));
        props.setProperty("token", token);
        hikariConfig.setDataSourceProperties(props);
        LOGGER.info("New refresh token has been obtained");
      } catch (IOException e) {
        LOGGER.error("Failed to obtain a fresh accessToken:" + e);
      }
    };
  }

  public static Properties buildAuthProperties(JsonNode config) {
    Properties properties = new Properties();
    try {
      var credentials = config.get("credentials");
      properties.setProperty("client_id", credentials.get("client_id").asText());
      properties.setProperty("client_secret", credentials.get("client_secret").asText());
      properties.setProperty("refresh_token", credentials.get("refresh_token").asText());
      properties.setProperty("host", config.get("host").asText());
      properties.put("authenticator", "oauth");
      properties.put("account", config.get("host").asText());

      String accessToken = getAccessTokenUsingRefreshToken(
          config.get("host").asText(), credentials.get("client_id").asText(),
          credentials.get("client_secret").asText(), credentials.get("refresh_token").asText());

      properties.put("token", accessToken);
    } catch (IOException e) {
      LOGGER.error("Request access token was failed with error" + e.getMessage());
    }
    return properties;
  }

  private static void populateUsernamePasswordConfig(HikariConfig hikariConfig, JsonNode config) {
    hikariConfig.setUsername(config.get("username").asText());
    hikariConfig.setPassword(config.get("password").asText());
  }

}
