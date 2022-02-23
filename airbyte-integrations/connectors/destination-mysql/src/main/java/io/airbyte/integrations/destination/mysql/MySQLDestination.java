/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Streams;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.mysql.MySQLSqlOperations.VersionCompatibility;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySQLDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySQLDestination.class);

  public static final String DATABASE_KEY = "database";
  public static final String HOST_KEY = "host";
  public static final String JDBC_URL_KEY = "jdbc_url";
  public static final String JDBC_URL_PARAMS_KEY = "jdbc_url_params";
  public static final String PASSWORD_KEY = "password";
  public static final String PORT_KEY = "port";
  public static final String SSL_KEY = "ssl";
  public static final String USERNAME_KEY = "username";

  public static final String DRIVER_CLASS = "com.mysql.cj.jdbc.Driver";

  static final Map<String, String> SSL_JDBC_PARAMETERS = ImmutableMap.of(
      "useSSL", "true",
      "requireSSL", "true",
      "verifyServerCertificate", "false");
  static final Map<String, String> DEFAULT_JDBC_PARAMETERS = ImmutableMap.of(
      "zeroDateTimeBehavior", "convertToNull");

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new MySQLDestination(), List.of(HOST_KEY), List.of(PORT_KEY));
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try (final JdbcDatabase database = getDatabase(config)) {
      final MySQLSqlOperations mySQLSqlOperations = (MySQLSqlOperations) getSqlOperations();

      final String outputSchema = getNamingResolver().getIdentifier(config.get(DATABASE_KEY).asText());
      attemptSQLCreateAndDropTableOperations(outputSchema, database, getNamingResolver(),
          mySQLSqlOperations);

      mySQLSqlOperations.verifyLocalFileEnabled(database);

      final VersionCompatibility compatibility = mySQLSqlOperations.isCompatibleVersion(database);
      if (!compatibility.isCompatible()) {
        throw new RuntimeException(String
            .format("Your MySQL version %s is not compatible with Airbyte",
                compatibility.getVersion()));
      }

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    }
  }

  public MySQLDestination() {
    super(DRIVER_CLASS, new MySQLNameTransformer(), new MySQLSqlOperations());
  }

  @Override
  protected JdbcDatabase getDatabase(final JsonNode config) {
    final JsonNode jdbcConfig = toJdbcConfig(config);

    return Databases.createJdbcDatabase(
        jdbcConfig.get(USERNAME_KEY).asText(),
        jdbcConfig.has(PASSWORD_KEY) ? jdbcConfig.get(PASSWORD_KEY).asText() : null,
        jdbcConfig.get(JDBC_URL_KEY).asText(),
        getDriverClass(),
        "allowLoadLocalInfile=true");
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final List<String> additionalParameters = getAdditionalParameters(config);

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:mysql://%s:%s/%s",
        config.get(HOST_KEY).asText(),
        config.get(PORT_KEY).asText(),
        config.get(DATABASE_KEY).asText()));
    // zero dates by default cannot be parsed into java date objects (they will throw an error)
    // in addition, users don't always have agency in fixing them e.g: maybe they don't own the database
    // and can't
    // remove zero date values.
    // since zero dates are placeholders, we convert them to null by default
    if (!additionalParameters.isEmpty()) {
      jdbcUrl.append("?");
      jdbcUrl.append(String.join("&", additionalParameters));
    }

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(USERNAME_KEY, config.get(USERNAME_KEY).asText())
        .put(JDBC_URL_KEY, jdbcUrl.toString());

    if (config.has(PASSWORD_KEY)) {
      configBuilder.put(PASSWORD_KEY, config.get(PASSWORD_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  private List<String> getAdditionalParameters(final JsonNode config) {
    final Map<String, String> customParameters = getCustomJdbcParameters(config);

    if (useSSL(config)) {
      return convertToJdbcStrings(customParameters, MoreMaps.merge(DEFAULT_JDBC_PARAMETERS, SSL_JDBC_PARAMETERS));
    } else {
      return convertToJdbcStrings(customParameters, DEFAULT_JDBC_PARAMETERS);
    }
  }

  private List<String> convertToJdbcStrings(final Map<String, String> customParameters, final Map<String, String> defaultParametersMap) {
    assertCustomParametersDontOverwriteDefaultParameters(customParameters, defaultParametersMap);
    return Streams.concat(Stream.of(customParameters, defaultParametersMap))
        .map(Map::entrySet)
        .flatMap(Collection::stream)
        .map(entry -> formatParameter(entry.getKey(), entry.getValue()))
        .collect(Collectors.toList());
  }

  private void assertCustomParametersDontOverwriteDefaultParameters(final Map<String, String> customParameters,
                                                                    final Map<String, String> defaultParameters) {
    for (final String key : defaultParameters.keySet()) {
      if (customParameters.containsKey(key) && !Objects.equals(customParameters.get(key), defaultParameters.get(key))) {
        throw new IllegalArgumentException("Cannot overwrite default JDBC parameter " + key);
      }
    }
  }

  private Map<String, String> getCustomJdbcParameters(final JsonNode config) {
    final Map<String, String> parameters = new HashMap<>();
    if (config.has(JDBC_URL_PARAMS_KEY)) {
      final String jdbcParams = config.get(JDBC_URL_PARAMS_KEY).asText();
      if (!jdbcParams.isBlank()) {
        final String[] keyValuePairs = jdbcParams.split("&");
        for (final String kv : keyValuePairs) {
          final String[] split = kv.split("=");
          if (split.length == 2) {
            parameters.put(split[0], split[1]);
          } else {
            throw new IllegalArgumentException(
                "jdbc_url_params must be formatted as 'key=value' pairs separated by the symbol '&'. (example: key1=value1&key2=value2&key3=value3). Got "
                    + jdbcParams);
          }
        }
      }
    }
    return parameters;
  }

  private boolean useSSL(final JsonNode config) {
    return !config.has(SSL_KEY) || config.get(SSL_KEY).asBoolean();
  }

  static String formatParameter(final String key, final String value) {
    return String.format("%s=%s", key, value);
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = MySQLDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", MySQLDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MySQLDestination.class);
  }

}
