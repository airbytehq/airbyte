/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static java.util.stream.Collectors.joining;

import com.fasterxml.jackson.databind.JsonNode;
import com.zaxxer.hikari.HikariDataSource;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
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
import java.time.Duration;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.TimeUnit;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * SnowflakeDatabase contains helpers to create connections to and run queries on Snowflake.
 */
public class SnowflakeDatabase {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeDatabase.class);
  private static final int PAUSE_BETWEEN_TOKEN_REFRESH_MIN = 7; // snowflake access token's TTL is 10min and can't be modified

  private static final Duration NETWORK_TIMEOUT = Duration.ofMinutes(1);
  private static final Duration QUERY_TIMEOUT = Duration.ofHours(3);
  private static final SnowflakeSQLNameTransformer nameTransformer = new SnowflakeSQLNameTransformer();
  private static final String DRIVER_CLASS_NAME = "net.snowflake.client.jdbc.SnowflakeDriver";

  private static final String REFRESH_TOKEN_URL = "https://%s/oauth/token-request";
  private static final HttpClient httpClient = HttpClient.newBuilder()
      .version(HttpClient.Version.HTTP_2)
      .connectTimeout(Duration.ofSeconds(10))
      .build();

  public static HikariDataSource createDataSource(final JsonNode config) {
    final HikariDataSource dataSource = new HikariDataSource();

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:snowflake://%s/?",
        config.get("host").asText()));
    final String username = config.get("username").asText();

    final Properties properties = new Properties();

    final JsonNode credentials = config.get("credentials");
    if (credentials != null && credentials.has("auth_type") && "OAuth2.0".equals(
        credentials.get("auth_type").asText())) {
      LOGGER.debug("OAuth login mode is used");
      // OAuth login option is selected on UI
      final String accessToken;
      try {
        // accessToken is only valid for 10 minutes. So we need to get a new one before processing new
        // stream
        accessToken = getAccessTokenUsingRefreshToken(config.get("host").asText(),
            credentials.get("client_id").asText(),
            credentials.get("client_secret").asText(), credentials.get("refresh_token").asText());
      } catch (final IOException e) {
        throw new RuntimeException(e);
      }
      properties.put("client_id", credentials.get("client_id").asText());
      properties.put("client_secret", credentials.get("client_secret").asText());
      properties.put("refresh_token", credentials.get("refresh_token").asText());
      properties.put("host", config.get("host").asText());
      properties.put("authenticator", "oauth");
      properties.put("token", accessToken);
      // the username is required for DBT normalization in OAuth connection
      properties.put("username", username);

      // thread to keep the refresh token up to date
      SnowflakeDestination.SCHEDULED_EXECUTOR_SERVICE.scheduleAtFixedRate(getRefreshTokenTask(dataSource),
          PAUSE_BETWEEN_TOKEN_REFRESH_MIN, PAUSE_BETWEEN_TOKEN_REFRESH_MIN, TimeUnit.MINUTES);

    } else if (credentials != null && credentials.has("password")) {
      LOGGER.debug("User/password login mode is used");
      // Username and pass login option is selected on UI
      dataSource.setUsername(username);
      dataSource.setPassword(credentials.get("password").asText());

    } else {
      LOGGER.warn(
          "Obsolete User/password login mode is used. Please re-create a connection to use the latest connector's version");
      // case to keep the backward compatibility
      dataSource.setUsername(username);
      dataSource.setPassword(config.get("password").asText());
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

    dataSource.setDriverClassName(DRIVER_CLASS_NAME);
    dataSource.setJdbcUrl(jdbcUrl.toString());
    dataSource.setDataSourceProperties(properties);
    return dataSource;
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

  public static JdbcDatabase getDatabase(final DataSource dataSource) {
    return new DefaultJdbcDatabase(dataSource);
  }

  private static Runnable getRefreshTokenTask(final HikariDataSource dataSource) {
    return () -> {
      LOGGER.info("Refresh token process started");
      final var props = dataSource.getDataSourceProperties();
      try {
        final var token = getAccessTokenUsingRefreshToken(props.getProperty("host"),
            props.getProperty("client_id"), props.getProperty("client_secret"),
            props.getProperty("refresh_token"));
        props.setProperty("token", token);
        dataSource.setDataSourceProperties(props);

        LOGGER.info("New refresh token has been obtained");
      } catch (final IOException e) {
        LOGGER.error("Failed to obtain a fresh accessToken:" + e);
      }
    };
  }

}
