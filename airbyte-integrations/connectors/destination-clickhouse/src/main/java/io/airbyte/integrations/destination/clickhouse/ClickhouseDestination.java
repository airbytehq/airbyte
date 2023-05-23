/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.jdbc.JdbcBufferedConsumerFactory;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickhouseDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickhouseDestination.class);

  public static final String DRIVER_CLASS = DatabaseDriver.CLICKHOUSE.getDriverClassName();

  public static final String HTTPS_PROTOCOL = "https";
  public static final String HTTP_PROTOCOL = "http";
  public static final String SSL_VERIFICATION_METHOD_KEY = "ssl_mode";
  public static final String DEFAULT_SSL_VERIFICATION_METHOD = "none";
  public static final String CA_CERT_FILENAME = "ca.crt";

  // Create an extra SqlOperations object because the one in the superclass is
  // private and we need to access it
  private final ClickhouseSqlOperations configurableSqlOperations;

  static final List<String> SSL_PARAMETERS = ImmutableList.of(
      "socket_timeout=3000000",
      "ssl=true");
  static final List<String> DEFAULT_PARAMETERS = ImmutableList.of(
      "socket_timeout=3000000");

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new ClickhouseDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public ClickhouseDestination() {
    super(DRIVER_CLASS, new ClickhouseSQLNameTransformer(), new ClickhouseSqlOperations());
    configurableSqlOperations = new ClickhouseSqlOperations();
  }

  @Override
  protected SqlOperations getSqlOperations() {
    return configurableSqlOperations;
  }

  private static void createCertificateFile(String fileName, String fileValue) throws IOException {
    try (final PrintWriter out = new PrintWriter(fileName, StandardCharsets.UTF_8)) {
      out.print(fileValue);
    }
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final boolean isSsl = JdbcUtils.useSsl(config);
    final String sslVerificationMethod = config.has(SSL_VERIFICATION_METHOD_KEY)
        && config.get(SSL_VERIFICATION_METHOD_KEY).has("mode")
            ? config.get(SSL_VERIFICATION_METHOD_KEY).get("mode").asText()
            : DEFAULT_SSL_VERIFICATION_METHOD;
    final String caCertificate = config.has(SSL_VERIFICATION_METHOD_KEY)
        && config.get(SSL_VERIFICATION_METHOD_KEY).has("ca_certificate")
            ? config.get(SSL_VERIFICATION_METHOD_KEY).get("ca_certificate").asText()
            : null;

    final StringBuilder jdbcUrl = new StringBuilder(
        String.format(DatabaseDriver.CLICKHOUSE.getUrlFormatString(),
            isSsl ? HTTPS_PROTOCOL : HTTP_PROTOCOL,
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get(JdbcUtils.DATABASE_KEY).asText()));

    if (isSsl) {
      jdbcUrl.append("?").append(String.join("&", SSL_PARAMETERS));
      jdbcUrl.append(String.format("&sslmode=%s", sslVerificationMethod));

      if (sslVerificationMethod.equals("strict") && caCertificate != null && !caCertificate.equals("")) {
        try {
          createCertificateFile(CA_CERT_FILENAME, caCertificate);
        } catch (final IOException e) {
          throw new RuntimeException("Failed to create encryption file");
        }
        jdbcUrl.append(String.format("&sslrootcert=%s", CA_CERT_FILENAME));
      }
    } else {
      jdbcUrl.append("?").append(String.join("&", DEFAULT_PARAMETERS));
    }

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl);

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final DataSource dataSource = getDataSource(config);
    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final NamingConventionTransformer namingResolver = getNamingResolver();
      final String outputSchema = namingResolver.getIdentifier(config.get(JdbcUtils.DATABASE_KEY).asText());
      configurableSqlOperations.setConfig(ClickhouseDestinationConfig.get(config));
      attemptSQLCreateAndDropTableOperations(outputSchema, database, namingResolver, configurableSqlOperations);
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    } finally {
      try {
        DataSourceFactory.close(dataSource);
      } catch (final Exception e) {
        LOGGER.warn("Unable to close data source.", e);
      }
    }
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    return Collections.emptyMap();
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = ClickhouseDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", ClickhouseDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", ClickhouseDestination.class);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    configurableSqlOperations.setConfig(ClickhouseDestinationConfig.get(config));
    return JdbcBufferedConsumerFactory.create(outputRecordCollector, getDatabase(getDataSource(config)),
        configurableSqlOperations, getNamingResolver(), config,
        catalog);
  }

}
