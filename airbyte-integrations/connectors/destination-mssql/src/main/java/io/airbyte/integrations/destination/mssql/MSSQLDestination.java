/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.NoOpJdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.RawOnlySqlGenerator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import java.io.File;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.jetbrains.annotations.NotNull;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MSSQLDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MSSQLDestination.class);

  public static final String DRIVER_CLASS = DatabaseDriver.MSSQLSERVER.getDriverClassName();

  public MSSQLDestination() {
    super(DRIVER_CLASS, new MSSQLNameTransformer(), new SqlServerOperations());
  }

  @NotNull
  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    final HashMap<String, String> properties = new HashMap<>();
    if (config.has("ssl_method")) {
      switch (config.get("ssl_method").asText()) {
        case "unencrypted" -> properties.put("encrypt", "false");
        case "encrypted_trust_server_certificate" -> {
          properties.put("encrypt", "true");
          properties.put("trustServerCertificate", "true");
        }
        case "encrypted_verify_certificate" -> {
          properties.put("encrypt", "true");
          properties.put("trustStore", getTrustStoreLocation());
          final String trustStorePassword = System.getProperty("javax.net.ssl.trustStorePassword");
          if (trustStorePassword != null && !trustStorePassword.isEmpty()) {
            properties.put("trustStorePassword", config.get("trustStorePassword").asText());
          }
          if (config.has("hostNameInCertificate")) {
            properties.put("hostNameInCertificate", config.get("hostNameInCertificate").asText());
          }
        }
      }
    }

    return properties;
  }

  @NotNull
  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final String schema = Optional.ofNullable(config.get("schema")).map(JsonNode::asText).orElse("public");

    final String jdbcUrl = String.format("jdbc:sqlserver://%s:%s;databaseName=%s;",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText());

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl)
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText())
        .put(JdbcUtils.SCHEMA_KEY, schema);

    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      // configBuilder.put(JdbcUtils.CONNECTION_PROPERTIES_KEY,
      // config.get(JdbcUtils.JDBC_URL_PARAMS_KEY));
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY));
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  protected JdbcDestinationHandler<? extends MinimumDestinationState> getDestinationHandler(final String databaseName,
                                                                                            final JdbcDatabase database,
                                                                                            final String rawTableSchema) {
    return new NoOpJdbcDestinationHandler<>(databaseName, database, rawTableSchema, SQLDialect.DEFAULT);
  }

  @NotNull
  @Override
  protected List<Migration> getMigrations(final JdbcDatabase database,
                                          final String databaseName,
                                          final SqlGenerator sqlGenerator,
                                          final DestinationHandler destinationHandler) {
    return List.of();
  }

  private String getTrustStoreLocation() {
    // trust store location code found at https://stackoverflow.com/a/56570588
    final String trustStoreLocation = Optional.ofNullable(System.getProperty("javax.net.ssl.trustStore"))
        .orElseGet(() -> System.getProperty("java.home") + "/lib/security/cacerts");
    final File trustStoreFile = new File(trustStoreLocation);
    if (!trustStoreFile.exists()) {
      throw new RuntimeException("Unable to locate the Java TrustStore: the system property javax.net.ssl.trustStore is undefined or "
          + trustStoreLocation + " does not exist.");
    }
    return trustStoreLocation;
  }

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new MSSQLDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = MSSQLDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", MSSQLDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MSSQLDestination.class);
  }

  @Override
  public boolean isV2Destination() {
    return true;
  }

  @Override
  protected boolean shouldAlwaysDisableTypeDedupe() {
    return true;
  }

  @NotNull
  @Override
  protected JdbcSqlGenerator getSqlGenerator(@NotNull final JsonNode config) {
    return new RawOnlySqlGenerator(new MSSQLNameTransformer());
  }

}
