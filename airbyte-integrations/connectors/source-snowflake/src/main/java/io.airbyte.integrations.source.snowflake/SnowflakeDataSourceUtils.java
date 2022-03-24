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
    hikariConfig.setJdbcUrl(jdbcUrl.toString());

    if (config.has("credentials") && config.get("credentials").has("auth_type")
        && "OAuth".equals(config.get("credentials").get("auth_type").asText())) {
      LOGGER.info("Authorization mode is OAuth");
      try {
        var credentials = config.get("credentials");
        Properties properties = new Properties();
        properties.setProperty("client_id", credentials.get("client_id").asText());
        properties.setProperty("client_secret", credentials.get("client_secret").asText());
        properties.setProperty("refresh_token", credentials.get("refresh_token").asText());
        properties.setProperty("host", config.get("host").asText());
        var accessToken = getAccessTokenUsingRefreshToken(
            config.get("host").asText(), credentials.get("client_id").asText(),
            credentials.get("client_secret").asText(), credentials.get("refresh_token").asText());
        properties.put("authenticator", "oauth");
        properties.put("token", accessToken);
        properties.put("account", config.get("host").asText());
        hikariConfig.setDataSourceProperties(properties);
        // thread to keep the refresh token up to date
        SnowflakeSource.SCHEDULED_EXECUTOR_SERVICE.scheduleAtFixedRate(getRefreshTokenTask(hikariConfig),
            PAUSE_BETWEEN_TOKEN_REFRESH_MIN, PAUSE_BETWEEN_TOKEN_REFRESH_MIN, TimeUnit.MINUTES);
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    } else if (config.has("credentials") && config.get("credentials").has("password")) {
      LOGGER.info("Authorization mode is 'Username and password'");
      var credentials = config.get("credentials");
      hikariConfig.setUsername(credentials.get("username").asText());
      hikariConfig.setPassword(credentials.get("password").asText());
    } else if (config.has("password") && config.has("username")) {
      LOGGER.info("Authorization mode is deprecated 'Username and password'. Please update your source configuration");
      hikariConfig.setUsername(config.get("username").asText());
      hikariConfig.setPassword(config.get("password").asText());
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

}
