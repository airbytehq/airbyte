/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle;

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
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.RandomStringUtils;
import org.jetbrains.annotations.NotNull;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OracleDestination extends AbstractJdbcDestination<MinimumDestinationState> implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleDestination.class);
  public static final String DRIVER_CLASS = DatabaseDriver.ORACLE.getDriverClassName();

  protected static final String KEY_STORE_FILE_PATH = "clientkeystore.jks";
  private static final String KEY_STORE_PASS = RandomStringUtils.randomAlphanumeric(8);
  public static final String ENCRYPTION_METHOD_KEY = "encryption_method";

  public static final String JDBC_URL_PARAMS_KEY = "jdbc_url_params";

  enum Protocol {
    TCP,
    TCPS
  }

  public OracleDestination() {
    super(DRIVER_CLASS, new OracleNameTransformer(), new OracleOperations("users"));
    System.setProperty("oracle.jdbc.timezoneAsRegion", "false");
  }

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new OracleDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    final HashMap<String, String> properties = new HashMap<>();
    if (config.has(JdbcUtils.ENCRYPTION_KEY)) {
      final JsonNode encryption = config.get(JdbcUtils.ENCRYPTION_KEY);
      final String encryptionMethod = encryption.get(ENCRYPTION_METHOD_KEY).asText();
      switch (encryptionMethod) {
        case "unencrypted" -> {

        }
        case "client_nne" -> {
          final String algorithm = encryption.get("encryption_algorithm").asText();
          properties.put("oracle.net.encryption_client", "REQUIRED");
          properties.put("oracle.net.encryption_types_client", "( " + algorithm + " )");
        }
        case "encrypted_verify_certificate" -> {
          tryConvertAndImportCertificate(encryption.get("ssl_certificate").asText());
          properties.put("javax.net.ssl.trustStore", KEY_STORE_FILE_PATH);
          properties.put("javax.net.ssl.trustStoreType", "JKS");
          properties.put("javax.net.ssl.trustStorePassword", KEY_STORE_PASS);
        }
        default -> throw new RuntimeException("Failed to obtain connection protocol from config " + encryption.asText());
      }

    }
    return properties;
  }

  @NotNull
  @Override
  public JsonNode toJdbcConfig(@NotNull final JsonNode config) {
    final Protocol protocol = obtainConnectionProtocol(config);
    final String connectionString = String.format(
        "jdbc:oracle:thin:@(DESCRIPTION=(ADDRESS=(PROTOCOL=%s)(HOST=%s)(PORT=%s))(CONNECT_DATA=(SID=%s)))",
        protocol,
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        config.get("sid").asText());

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, connectionString);

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }
    if (config.has(JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JDBC_URL_PARAMS_KEY, config.get(JDBC_URL_PARAMS_KEY));
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  protected Protocol obtainConnectionProtocol(final JsonNode config) {
    if (!config.has(JdbcUtils.ENCRYPTION_KEY)) {
      return Protocol.TCP;
    }
    final JsonNode encryption = config.get(JdbcUtils.ENCRYPTION_KEY);
    final String encryptionMethod = encryption.get(ENCRYPTION_METHOD_KEY).asText();
    switch (encryptionMethod) {
      case "unencrypted", "client_nne" -> {
        return Protocol.TCP;
      }
      case "encrypted_verify_certificate" -> {
        return Protocol.TCPS;
      }
    }
    throw new RuntimeException(
        "Failed to obtain connection protocol from config " + encryption.asText());
  }

  private static void tryConvertAndImportCertificate(final String certificate) {
    try {
      convertAndImportCertificate(certificate);
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }
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
  protected String getDatabaseName(@NotNull final JsonNode config) {
    return config.get("sid").asText();
  }

  @NotNull
  @Override
  protected JdbcSqlGenerator getSqlGenerator() {
    return new RawOnlySqlGenerator(new OracleNameTransformer());
  }

  @NotNull
  @Override
  protected JdbcDestinationHandler<MinimumDestinationState> getDestinationHandler(final String databaseName,
                                                                                  final JdbcDatabase database,
                                                                                  final String rawTableSchema) {
    return new NoOpJdbcDestinationHandler<>(databaseName, database, rawTableSchema, SQLDialect.DEFAULT);
  }

  @NotNull
  @Override
  protected List<Migration<MinimumDestinationState>> getMigrations(@NotNull final JdbcDatabase database,
                                                                   @NotNull final String databaseName,
                                                                   @NotNull final SqlGenerator sqlGenerator,
                                                                   @NotNull final DestinationHandler<MinimumDestinationState> destinationHandler) {
    return List.of();
  }

  private static void convertAndImportCertificate(final String certificate)
      throws IOException, InterruptedException {
    final Runtime run = Runtime.getRuntime();
    try (final PrintWriter out = new PrintWriter("certificate.pem", StandardCharsets.UTF_8)) {
      out.print(certificate);
    }
    runProcess("openssl x509 -outform der -in certificate.pem -out certificate.der", run);
    runProcess("keytool -import -alias rds-root -keystore " + KEY_STORE_FILE_PATH
        + " -file certificate.der -storepass " + KEY_STORE_PASS + " -noprompt", run);
  }

  private static void runProcess(final String cmd, final Runtime run) throws IOException, InterruptedException {
    final Process pr = run.exec(cmd);
    if (!pr.waitFor(30, TimeUnit.SECONDS)) {
      pr.destroy();
      throw new RuntimeException("Timeout while executing: " + cmd);
    }
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = sshWrappedDestination();
    LOGGER.info("starting destination: {}", OracleDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", OracleDestination.class);
  }

}
