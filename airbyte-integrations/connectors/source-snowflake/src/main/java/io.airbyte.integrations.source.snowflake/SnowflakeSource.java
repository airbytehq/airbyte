/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import static io.airbyte.integrations.source.snowflake.SnowflakeDataSourceUtils.KEY_PAIR_METHOD;
import static io.airbyte.integrations.source.snowflake.SnowflakeDataSourceUtils.OAUTH_METHOD;
import static io.airbyte.integrations.source.snowflake.SnowflakeDataSourceUtils.PRIVATE_KEY_FIELD_NAME;
import static io.airbyte.integrations.source.snowflake.SnowflakeDataSourceUtils.PRIVATE_KEY_FILE_NAME;
import static io.airbyte.integrations.source.snowflake.SnowflakeDataSourceUtils.PRIVATE_KEY_PASSWORD;
import static io.airbyte.integrations.source.snowflake.SnowflakeDataSourceUtils.UNRECOGNIZED;
import static io.airbyte.integrations.source.snowflake.SnowflakeDataSourceUtils.USERNAME_PASSWORD_METHOD;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
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
  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;

  public static final String DRIVER_CLASS = DatabaseDriver.SNOWFLAKE.getDriverClassName();
  public static final ScheduledExecutorService SCHEDULED_EXECUTOR_SERVICE = Executors.newScheduledThreadPool(1);

  private final String airbyteEnvironment;

  public SnowflakeSource(final String airbyteEnvironment) {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new SnowflakeSourceOperations());
    this.airbyteEnvironment = airbyteEnvironment;
  }

  @Override
  public JdbcDatabase createDatabase(final JsonNode sourceConfig) throws SQLException {
    final JsonNode jdbcConfig = toDatabaseConfig(sourceConfig);
    // Create the data source
    final DataSource dataSource = SnowflakeDataSourceUtils.createDataSource(sourceConfig, airbyteEnvironment);
    dataSources.add(dataSource);

    final JdbcDatabase database = new StreamingJdbcDatabase(
        dataSource,
        sourceOperations,
        streamingQueryConfigProvider);

    quoteString = (quoteString == null ? database.getMetaData().getIdentifierQuoteString() : quoteString);
    database.setSourceConfig(sourceConfig);
    database.setDatabaseConfig(jdbcConfig);
    return database;
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final String jdbcUrl = SnowflakeDataSourceUtils.buildJDBCUrl(config, airbyteEnvironment);

    if (config.has("credentials")) {
      final JsonNode credentials = config.get("credentials");
      final String authType =
          credentials.has("auth_type") ? credentials.get("auth_type").asText() : UNRECOGNIZED;
      return switch (authType) {
        case OAUTH_METHOD -> buildOAuthConfig(config, jdbcUrl);
        case USERNAME_PASSWORD_METHOD -> buildUsernamePasswordConfig(config.get("credentials"),
            jdbcUrl);
        case KEY_PAIR_METHOD -> buildKeyPairConfig(credentials, jdbcUrl);
        default -> throw new IllegalArgumentException("Unrecognized auth type: " + authType);
      };
    } else {
      return buildUsernamePasswordConfig(config, jdbcUrl);
    }
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "INFORMATION_SCHEMA");
  }

  @Override
  protected int getStateEmissionFrequency() {
    return INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  @Override
  protected String getCountColumnName() {
    return "RECORD_COUNT";
  }

  private JsonNode buildOAuthConfig(final JsonNode config, final String jdbcUrl) {
    final String accessToken;
    final var credentials = config.get("credentials");
    try {
      accessToken = SnowflakeDataSourceUtils.getAccessTokenUsingRefreshToken(
          config.get(JdbcUtils.HOST_KEY).asText(), credentials.get("client_id").asText(),
          credentials.get("client_secret").asText(), credentials.get("refresh_token").asText());
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.CONNECTION_PROPERTIES_KEY,
            String.join(";", "authenticator=oauth", "token=" + accessToken))
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl);
    return Jsons.jsonNode(configBuilder.build());
  }

  private JsonNode buildUsernamePasswordConfig(final JsonNode config, final String jdbcUrl) {
    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl);
    LOGGER.info(jdbcUrl);
    return Jsons.jsonNode(configBuilder.build());
  }

  private JsonNode buildKeyPairConfig(final JsonNode config, final String jdbcUrl) {
    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl);

    String privateKeyValue = config.get(PRIVATE_KEY_FIELD_NAME).asText();
    createPrivateKeyFile(PRIVATE_KEY_FILE_NAME, privateKeyValue);
    configBuilder.put("private_key_file", PRIVATE_KEY_FILE_NAME);
    if (config.has(PRIVATE_KEY_PASSWORD)) {
      configBuilder.put("private_key_file_pwd", config.get(PRIVATE_KEY_PASSWORD).asText());
    }

    LOGGER.info(jdbcUrl);
    return Jsons.jsonNode(configBuilder.build());
  }

  private void createPrivateKeyFile(String fileName, String fileValue) {
    try (PrintWriter pw = new PrintWriter(fileName, StandardCharsets.UTF_8)) {
      pw.print(fileValue);
    } catch (IOException e) {
      throw new RuntimeException("Failed to create file for private key", e);
    }
  }

}
