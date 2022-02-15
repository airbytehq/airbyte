/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.mysql.MySQLSqlOperations.VersionCompatibility;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySQLDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySQLDestination.class);
  public static final List<String> HOST_KEY = List.of("host");
  public static final List<String> PORT_KEY = List.of("port");

  public static final String DRIVER_CLASS = "com.mysql.cj.jdbc.Driver";

  public static final String JDBC_URL_PARAMS_KEY = "jdbc_url_params";

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new MySQLDestination(), HOST_KEY, PORT_KEY);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try (final JdbcDatabase database = getDatabase(config)) {
      final MySQLSqlOperations mySQLSqlOperations = (MySQLSqlOperations) getSqlOperations();

      final String outputSchema = getNamingResolver().getIdentifier(config.get("database").asText());
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
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        getDriverClass(),
        "allowLoadLocalInfile=true");
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final List<String> additionalParameters = getAdditionalParameters(config);

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:mysql://%s:%s/%s",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("database").asText()));
    // zero dates by default cannot be parsed into java date objects (they will throw an error)
    // in addition, users don't always have agency in fixing them e.g: maybe they don't own the database
    // and can't
    // remove zero date values.
    // since zero dates are placeholders, we convert them to null by default
    //FIXME(girarda): do we also want to prevent people from overriding zeroDateTimeBehavior?
    jdbcUrl.append("?zeroDateTimeBehavior=convertToNull");
    if (!additionalParameters.isEmpty()) {
      jdbcUrl.append("&");
      additionalParameters.forEach(x -> jdbcUrl.append(x).append("&"));
    }

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", jdbcUrl.toString());

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  private List<String> getAdditionalParameters(final JsonNode config) {
    final List<String> additionalParameters = new ArrayList<>();
    addJDBCUrlParameters(config, additionalParameters);
    if (useSSL(config)) {
      addSSLJdbcParameters(additionalParameters);
    }
    return additionalParameters;
  }

  private void addJDBCUrlParameters(final JsonNode config, final List<String> additionalParameters) {
    if (config.has(JDBC_URL_PARAMS_KEY)) {
      final String additionalParams = config.get(JDBC_URL_PARAMS_KEY).asText();
      if (additionalParams.isBlank()) {
        return;
      }
      if (useSSL(config)) {
        for (final String p : getSSLParameters().keySet()) {
          if (containsParameterKey(additionalParams, p)) {
            throw new RuntimeException("Cannot overwrite JDBC parameter " + p);
          }
        }
      }
      additionalParameters.add(additionalParams);
    }
  }

  private boolean containsParameterKey(final String additionalParametersString, final String key) {
    final String s = String.format("%s=", key);
    return additionalParametersString.contains(s);
  }

  private void addSSLJdbcParameters(final List<String> additionalParameters) {
    for (final Entry<String, String> sslParameter : getSSLParameters().entrySet()) {
      final String param = formatParameter(sslParameter.getKey(), sslParameter.getValue());
      additionalParameters.add(param);
    }
  }

  private boolean useSSL(final JsonNode config) {
    return !config.has("ssl") || config.get("ssl").asBoolean();
  }

  static Map<String, String> getSSLParameters() {
    final Builder<String, String> builder = ImmutableMap.builder();
    return builder
        .put("useSSL", "true")
        .put("requireSSL", "true")
        .put("verifyServerCertificate", "false")
        .build();
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
