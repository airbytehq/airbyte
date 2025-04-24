/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import static java.util.stream.Collectors.joining;

import com.fasterxml.jackson.databind.JsonNode;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
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
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeDataSourceUtils {

  public static final String OAUTH_METHOD = "OAuth";
  public static final String USERNAME_PASSWORD_METHOD = "username/password";
  public static final String KEY_PAIR_METHOD = "Key Pair Authentication";
  public static final String PRIVATE_KEY_FIELD_NAME = "private_key";
  public static final String PRIVATE_KEY_PASSWORD = "private_key_password";
  public static final String PRIVATE_KEY_FILE_NAME = "rsa_key.p8";

  public static final String UNRECOGNIZED = "Unrecognized";
  public static final String AIRBYTE_OSS = "airbyte_oss";
  public static final String AIRBYTE_CLOUD = "airbyte_cloud";
  private static final String JDBC_CONNECTION_STRING =
      "role=%s&warehouse=%s&database=%s&JDBC_QUERY_RESULT_FORMAT=%s&CLIENT_SESSION_KEEP_ALIVE=%s&application=%s";

  private static final String JDBC_SCHEMA_PARAM = "&schema=%s&CLIENT_METADATA_REQUEST_USE_CONNECTION_CTX=true";
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
  public static HikariDataSource createDataSource(final JsonNode config, final String airbyteEnvironment) {
    final HikariDataSource dataSource = new HikariDataSource();
    dataSource.setJdbcUrl(buildJDBCUrl(config, airbyteEnvironment));

    if (config.has("credentials")) {
      final JsonNode credentials = config.get("credentials");
      final String authType = credentials.has("auth_type") ? credentials.get("auth_type").asText() : UNRECOGNIZED;
      switch (authType) {
        case OAUTH_METHOD -> {
          LOGGER.info("Authorization mode is OAuth");
          dataSource.setDataSourceProperties(buildAuthProperties(config));
          // thread to keep the refresh token up to date
          SnowflakeSource.SCHEDULED_EXECUTOR_SERVICE.scheduleAtFixedRate(
              getAccessTokenTask(dataSource),
              PAUSE_BETWEEN_TOKEN_REFRESH_MIN, PAUSE_BETWEEN_TOKEN_REFRESH_MIN, TimeUnit.MINUTES);
        }
        case USERNAME_PASSWORD_METHOD -> {
          LOGGER.info("Authorization mode is 'Username and password'");
          populateUsernamePasswordConfig(dataSource, config.get("credentials"));
        }
        case KEY_PAIR_METHOD -> {
          LOGGER.info("Authorization mode is 'Key Pair Authentication'");
          populateKeyPairConfig(dataSource, config.get("credentials"));
        }
        default -> throw new IllegalArgumentException("Unrecognized auth type: " + authType);
      }
    } else {
      LOGGER.info("Authorization mode is deprecated 'Username and password'. Please update your source configuration");
      populateUsernamePasswordConfig(dataSource, config);
    }

    return dataSource;
  }

  /**
   * Method to make request for a new access token using refresh token and client credentials.
   *
   * @return access token
   */
  public static String getAccessTokenUsingRefreshToken(final String hostName,
                                                       final String clientId,
                                                       final String clientSecret,
                                                       final String refreshToken)
      throws IOException {
    final var refreshTokenUri = String.format(REFRESH_TOKEN_URL, hostName);
    final Map<String, String> requestBody = new HashMap<>();
    requestBody.put("grant_type", "refresh_token");
    requestBody.put("refresh_token", refreshToken);

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
        LOGGER.error("Failed to obtain accessToken using refresh token. " + jsonResponse);
        throw new RuntimeException(
            "Failed to obtain accessToken using refresh token. " + jsonResponse);
      }
    } catch (final InterruptedException e) {
      throw new IOException("Failed to refreshToken", e);
    }
  }

  public static String buildJDBCUrl(final JsonNode config, final String airbyteEnvironment) {
    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:snowflake://%s/?",
        config.get(JdbcUtils.HOST_KEY).asText()));

    // Add required properties
    jdbcUrl.append(String.format(JDBC_CONNECTION_STRING,
        config.get("role").asText(),
        config.get("warehouse").asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText(),
        // Needed for JDK17 - see
        // https://stackoverflow.com/questions/67409650/snowflake-jdbc-driver-internal-error-fail-to-retrieve-row-count-for-first-arrow
        "JSON",
        true,
        airbyteEnvironment));

    if (config.get("schema") != null && StringUtils.isNotBlank(config.get("schema").asText())) {
      jdbcUrl.append(JDBC_SCHEMA_PARAM.formatted(config.get("schema").asText()));
    }

    // https://docs.snowflake.com/en/user-guide/jdbc-configure.html#jdbc-driver-connection-string
    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      jdbcUrl.append("&").append(config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }
    return jdbcUrl.toString();
  }

  private static Runnable getAccessTokenTask(final HikariDataSource dataSource) {
    return () -> {
      LOGGER.info("Refresh token process started");
      final var props = dataSource.getDataSourceProperties();
      try {
        final var token = getAccessTokenUsingRefreshToken(props.getProperty(JdbcUtils.HOST_KEY),
            props.getProperty("client_id"), props.getProperty("client_secret"),
            props.getProperty("refresh_token"));
        props.setProperty("token", token);
        dataSource.setDataSourceProperties(props);
        LOGGER.info("New access token has been obtained");
      } catch (final IOException e) {
        LOGGER.error("Failed to obtain a fresh accessToken:" + e);
      }
    };
  }

  public static Properties buildAuthProperties(final JsonNode config) {
    final Properties properties = new Properties();
    try {
      final var credentials = config.get("credentials");
      properties.setProperty("client_id", credentials.get("client_id").asText());
      properties.setProperty("client_secret", credentials.get("client_secret").asText());
      properties.setProperty("refresh_token", credentials.get("refresh_token").asText());
      properties.setProperty(JdbcUtils.HOST_KEY, config.get(JdbcUtils.HOST_KEY).asText());
      properties.put("authenticator", "oauth");
      properties.put("account", config.get(JdbcUtils.HOST_KEY).asText());

      final String accessToken = getAccessTokenUsingRefreshToken(
          config.get(JdbcUtils.HOST_KEY).asText(), credentials.get("client_id").asText(),
          credentials.get("client_secret").asText(), credentials.get("refresh_token").asText());

      properties.put("token", accessToken);
    } catch (final IOException e) {
      LOGGER.error("Request access token was failed with error" + e.getMessage());
    }
    return properties;
  }

  private static void populateUsernamePasswordConfig(final HikariConfig hikariConfig, final JsonNode config) {
    hikariConfig.setUsername(config.get(JdbcUtils.USERNAME_KEY).asText());
    hikariConfig.setPassword(config.get(JdbcUtils.PASSWORD_KEY).asText());
  }

  private static void populateKeyPairConfig(final HikariConfig hikariConfig, final JsonNode config) {
    hikariConfig.setUsername(config.get(JdbcUtils.USERNAME_KEY).asText());
    hikariConfig.setDataSourceProperties(buildKeyPairProperties(config));
  }

  private static Properties buildKeyPairProperties(JsonNode config) {
    final Properties properties = new Properties();
    properties.setProperty("private_key_file", PRIVATE_KEY_FILE_NAME);
    if (config.has(PRIVATE_KEY_PASSWORD)) {
      properties.setProperty("private_key_file_pwd", config.get(PRIVATE_KEY_PASSWORD).asText());
    }
    return properties;
  }

}
