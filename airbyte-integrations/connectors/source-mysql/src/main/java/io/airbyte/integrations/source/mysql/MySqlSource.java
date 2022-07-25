/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.debezium.AirbyteDebeziumHandler.shouldUseCDC;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.mysql.cj.MysqlType;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.mysql.helpers.CdcConfigurationHelper;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.SyncMode;
import java.time.Duration;

import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.TimeUnit;

import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlSource extends AbstractJdbcSource<MysqlType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlSource.class);

  public static final String DRIVER_CLASS = DatabaseDriver.MYSQL.getDriverClassName();
  public static final String MYSQL_CDC_OFFSET = "mysql_cdc_offset";
  public static final String MYSQL_DB_HISTORY = "mysql_db_history";
  public static final String CDC_LOG_FILE = "_ab_cdc_log_file";
  public static final String CDC_LOG_POS = "_ab_cdc_log_pos";
  public static final List<String> SSL_PARAMETERS = List.of(
      "useSSL=true",
      "requireSSL=true");

  public static final String SSL_PARAMETERS_WITH_CERTIFICATE_VALIDATION = "verifyServerCertificate=true";
  public static final String SSL_PARAMETERS_WITHOUT_CERTIFICATE_VALIDATION = "verifyServerCertificate=false";

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new MySqlSource(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public MySqlSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new MySqlSourceOperations());
  }

  private static AirbyteStream removeIncrementalWithoutPk(final AirbyteStream stream) {
    if (stream.getSourceDefinedPrimaryKey().isEmpty()) {
      stream.getSupportedSyncModes().remove(SyncMode.INCREMENTAL);
    }

    return stream;
  }

  private static AirbyteStream setIncrementalToSourceDefined(final AirbyteStream stream) {
    if (stream.getSupportedSyncModes().contains(SyncMode.INCREMENTAL)) {
      stream.setSourceDefinedCursor(true);
    }

    return stream;
  }

  // Note: in place mutation.
  private static AirbyteStream addCdcMetadataColumns(final AirbyteStream stream) {

    final ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    final ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number"));
    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    properties.set(CDC_LOG_FILE, stringType);
    properties.set(CDC_LOG_POS, numberType);
    properties.set(CDC_UPDATED_AT, stringType);
    properties.set(CDC_DELETED_AT, stringType);

    return stream;
  }

  @Override
  public List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations(final JsonNode config) throws Exception {
    final List<CheckedConsumer<JdbcDatabase, Exception>> checkOperations = new ArrayList<>(super.getCheckOperations(config));
    if (isCdc(config)) {
      checkOperations.addAll(CdcConfigurationHelper.getCheckOperations());
    }
    return checkOperations;
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    final AirbyteCatalog catalog = super.discover(config);

    if (isCdc(config)) {
      final List<AirbyteStream> streams = catalog.getStreams().stream()
          .map(MySqlSource::removeIncrementalWithoutPk)
          .map(MySqlSource::setIncrementalToSourceDefined)
          .map(MySqlSource::addCdcMetadataColumns)
          .collect(toList());

      catalog.setStreams(streams);
    }

    return catalog;
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:mysql://%s:%s/%s",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText()));

    // To fetch the result in batches, the "useCursorFetch=true" must be set.
    // https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-implementation-notes.html.
    // When using this approach MySql creates a temporary table which may have some effect on db
    // performance.
    jdbcUrl.append("?useCursorFetch=true");
    jdbcUrl.append("&zeroDateTimeBehavior=convertToNull");
    // ensure the return tinyint(1) is boolean
    jdbcUrl.append("&tinyInt1isBit=true");
    // ensure the return year value is a Date; see the rationale
    // in the setJsonField method in MySqlSourceOperations.java
    jdbcUrl.append("&yearIsDateType=true");
    if (config.get(JdbcUtils.JDBC_URL_PARAMS_KEY) != null && !config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText().isEmpty()) {
      jdbcUrl.append("&").append(config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }
    Map<String, String> additionalParameters = new HashMap<>();
    // assume ssl if not explicitly mentioned.
    if (!config.has(JdbcUtils.SSL_KEY) || config.get(JdbcUtils.SSL_KEY).asBoolean()) {
      if (config.has("ssl_mode")) {
        if ("disable".equals(config.get("ssl_mode").get("mode").asText())) {
          jdbcUrl.append("&").append("sslMode=DISABLE");
        } else {
          additionalParameters.putAll(obtainConnectionOptions(config.get("ssl_mode")));
          jdbcUrl.append("&").append(String.join("&", SSL_PARAMETERS)).append("&");
          if (additionalParameters.isEmpty()) {
            jdbcUrl.append(SSL_PARAMETERS_WITHOUT_CERTIFICATE_VALIDATION);
          } else {
            jdbcUrl.append(SSL_PARAMETERS_WITH_CERTIFICATE_VALIDATION);
          }
        }
      } else {
        jdbcUrl.append("&").append(String.join("&", SSL_PARAMETERS));
      }
    }

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl.toString());

    configBuilder.putAll(additionalParameters);

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }
    return Jsons.jsonNode(configBuilder.build());
  }

  private static boolean isCdc(final JsonNode config) {
    return config.hasNonNull("replication_method")
        && ReplicationMethod.valueOf(config.get("replication_method").asText())
            .equals(ReplicationMethod.CDC);
  }

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(final JdbcDatabase database,
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<MysqlType>>> tableNameToTable,
                                                                             final StateManager stateManager,
                                                                             final Instant emittedAt) {
    final JsonNode sourceConfig = database.getSourceConfig();
    if (isCdc(sourceConfig) && shouldUseCDC(catalog)) {
      final AirbyteDebeziumHandler handler =
          new AirbyteDebeziumHandler(sourceConfig, MySqlCdcTargetPosition.targetPosition(database), true, Duration.ofMinutes(5));

      final Optional<CdcState> cdcState = Optional.ofNullable(stateManager.getCdcStateManager().getCdcState());
      final MySqlCdcSavedInfoFetcher fetcher = new MySqlCdcSavedInfoFetcher(cdcState.orElse(null));
      return Collections.singletonList(handler.getIncrementalIterators(catalog,
          fetcher,
          new MySqlCdcStateHandler(stateManager),
          new MySqlCdcConnectorMetadataInjector(),
          MySqlCdcProperties.getDebeziumProperties(sourceConfig),
          emittedAt));
    } else {
      LOGGER.info("using CDC: {}", false);
      return super.getIncrementalIterators(database, catalog, tableNameToTable, stateManager,
          emittedAt);
    }
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "information_schema",
        "mysql",
        "performance_schema",
        "sys");
  }

  public static void main(final String[] args) throws Exception {
    final Source source = MySqlSource.sshWrappedSource();
    LOGGER.info("starting source: {}", MySqlSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MySqlSource.class);
  }

  public enum ReplicationMethod {
    STANDARD,
    CDC
  }

  /* Helpers */

  public static Map<String, String> obtainConnectionOptions(final JsonNode encryption) {
    Map<String, String> additionalParameters = new HashMap<>();
    if (!encryption.isNull()) {
      final var method = encryption.get("mode").asText().toUpperCase();
      String sslPassword = encryption.has("client_key_password") ? encryption.get("client_key_password").asText() : "";
      var keyStorePassword = RandomStringUtils.randomAlphanumeric(10);
      if (!sslPassword.isEmpty()) {
        keyStorePassword = sslPassword;
      }
      switch (method) {
        case "VERIFY_CA" -> {
          additionalParameters.putAll(obtainConnectionCaOptions(encryption, method, keyStorePassword));
        }
        case "VERIFY_IDENTITY" -> {
          additionalParameters.putAll(obtainConnectionFullOptions(encryption, method, keyStorePassword));
        }
      }
    }
    return additionalParameters;
  }

  private static Map<String, String> obtainConnectionFullOptions(final JsonNode encryption,
                                                                 final String method,
                                                                 final String clientKeyPassword) {
    Map<String, String> additionalParameters = new HashMap<>();
    try {
      convertAndImportFullCertificate(encryption.get("ca_certificate").asText(),
              encryption.get("client_certificate").asText(), encryption.get("client_key").asText(), clientKeyPassword);
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }
    additionalParameters.put("trustCertificateKeyStoreUrl", "customtruststore");
    additionalParameters.put("trustCertificateKeyStorePassword", clientKeyPassword);
    additionalParameters.put("clientCertificateKeyStoreUrl", "customkeystore");
    additionalParameters.put("clientCertificateKeyStorePassword", clientKeyPassword);
    additionalParameters.put("sslMode", method.toUpperCase());
    return additionalParameters;
  }

  private static Map<String, String> obtainConnectionCaOptions(final JsonNode encryption,
                                                               final String method,
                                                               final String clientKeyPassword) {
    Map<String, String> additionalParameters = new HashMap<>();
    try {
      convertAndImportCaCertificate(encryption.get("ca_certificate").asText(), clientKeyPassword);
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }
    additionalParameters.put("trustCertificateKeyStoreUrl", "customtruststore");
    additionalParameters.put("trustCertificateKeyStorePassword", clientKeyPassword);
    additionalParameters.put("sslMode", method.toUpperCase());
    return additionalParameters;
  }

  private static void convertAndImportFullCertificate(final String caCertificate,
                                                      final String clientCertificate,
                                                      final String clientKey,
                                                      final String clientKeyPassword)
          throws IOException, InterruptedException {
    final Runtime run = Runtime.getRuntime();
    createCaCertificate(caCertificate, clientKeyPassword, run);
    createCertificateFile("client-cert.pem", clientCertificate);
    createCertificateFile("client-key.pem", clientKey);
    // add client certificate to the custom keystore
    runProcess("keytool -alias client-certificate -keystore customkeystore"
            + " -import -file client-cert.pem -storepass " + clientKeyPassword + " -noprompt", run);
    // add client key to the custom keystore
    runProcess("keytool -alias client-key -keystore customkeystore"
            + " -import -file client-key.pem -storepass " + clientKeyPassword + " -noprompt", run);
    runProcess("rm client-key.pem", run);

    updateTrustStoreSystemProperty(clientKeyPassword);
  }

  private static void convertAndImportCaCertificate(final String caCertificate,
                                                    final String clientKeyPassword)
          throws IOException, InterruptedException {
    final Runtime run = Runtime.getRuntime();
    createCaCertificate(caCertificate, clientKeyPassword, run);
    updateTrustStoreSystemProperty(clientKeyPassword);
  }

  private static void createCaCertificate(final String caCertificate,
                                          final String clientKeyPassword,
                                          final Runtime run)
          throws IOException, InterruptedException {
    createCertificateFile("ca.pem", caCertificate);
    // add CA certificate to the custom keystore
    runProcess("keytool -import -alias root-certificate -keystore customtruststore"
            + " -file ca.pem -storepass " + clientKeyPassword + " -noprompt", run);
  }

  private static void updateTrustStoreSystemProperty(final String clientKeyPassword) {
    String result = System.getProperty("user.dir") + "/customtruststore";
    System.setProperty("javax.net.ssl.trustStore", result);
    System.setProperty("javax.net.ssl.trustStorePassword", clientKeyPassword);
  }

  private static void createCertificateFile(String fileName, String fileValue) throws IOException {
    try (final PrintWriter out = new PrintWriter(fileName, StandardCharsets.UTF_8)) {
      out.print(fileValue);
    }
  }

  private static void runProcess(final String cmd, final Runtime run) throws IOException, InterruptedException {
    final Process pr = run.exec(cmd);
    if (!pr.waitFor(30, TimeUnit.SECONDS)) {
      pr.destroy();
      throw new RuntimeException("Timeout while executing: " + cmd);
    }
  }

}
