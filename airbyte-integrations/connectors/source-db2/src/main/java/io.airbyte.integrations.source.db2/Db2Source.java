/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.db2;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.cdk.integrations.source.jdbc.dto.JdbcPrivilegeDto;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Db2Source extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(Db2Source.class);
  public static final String DRIVER_CLASS = DatabaseDriver.DB2.getDriverClassName();

  private static final String KEY_STORE_PASS = RandomStringUtils.randomAlphanumeric(8);
  private static final String KEY_STORE_FILE_PATH = "clientkeystore.jks";
  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;

  public Db2Source() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new Db2SourceOperations());
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new Db2Source();
    LOGGER.info("starting source: {}", Db2Source.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", Db2Source.class);
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final StringBuilder jdbcUrl = new StringBuilder(String.format(DatabaseDriver.DB2.getUrlFormatString(),
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asInt(),
        config.get("db").asText()));

    var result = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl.toString())
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText())
        .build());

    // assume ssl if not explicitly mentioned.
    final var additionalParams = obtainConnectionOptions(config.get(JdbcUtils.ENCRYPTION_KEY));
    if (!additionalParams.isEmpty()) {
      jdbcUrl.append(":").append(String.join(";", additionalParams));
      jdbcUrl.append(";");
      result = Jsons.jsonNode(ImmutableMap.builder()
          .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl.toString())
          .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
          .put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText())
          .put(JdbcUtils.CONNECTION_PROPERTIES_KEY, additionalParams)
          .build());
    }

    if (config.get(JdbcUtils.JDBC_URL_PARAMS_KEY) != null && !config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText().isEmpty()) {
      ((ObjectNode) result).put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }

    return result;
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "NULLID", "SYSCAT", "SQLJ", "SYSFUN", "SYSIBM", "SYSIBMADM", "SYSIBMINTERNAL", "SYSIBMTS",
        "SYSPROC", "SYSPUBLIC", "SYSSTAT", "SYSTOOLS");
  }

  @Override
  @SuppressWarnings("unchecked")
  public Set<JdbcPrivilegeDto> getPrivilegesTableForCurrentUser(final JdbcDatabase database, final String schema) throws SQLException {
    try (final Stream<JsonNode> stream = database.unsafeQuery(getPrivileges(), sourceOperations::rowToJson)) {
      return stream.map(this::getPrivilegeDto).collect(Collectors.toSet());
    }
  }

  @Override
  protected boolean isNotInternalSchema(final JsonNode jsonNode, final Set<String> internalSchemas) {
    return false;
  }

  @Override
  protected int getStateEmissionFrequency() {
    return INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  @Override
  protected String getCountColumnName() {
    return "RECORD_COUNT";
  }

  private CheckedFunction<Connection, PreparedStatement, SQLException> getPrivileges() {
    return connection -> connection.prepareStatement(
        "SELECT DISTINCT OBJECTNAME, OBJECTSCHEMA FROM SYSIBMADM.PRIVILEGES WHERE OBJECTTYPE = 'TABLE' AND PRIVILEGE = 'SELECT'");
  }

  private JdbcPrivilegeDto getPrivilegeDto(final JsonNode jsonNode) {
    return JdbcPrivilegeDto.builder()
        .schemaName(jsonNode.get("OBJECTSCHEMA").asText().trim())
        .tableName(jsonNode.get("OBJECTNAME").asText())
        .build();
  }

  /* Helpers */

  private List<String> obtainConnectionOptions(final JsonNode encryption) {
    final List<String> additionalParameters = new ArrayList<>();
    if (!encryption.isNull()) {
      final String encryptionMethod = encryption.get("encryption_method").asText();
      if ("encrypted_verify_certificate".equals(encryptionMethod)) {
        final var keyStorePassword = getKeyStorePassword(encryption.get("key_store_password"));
        try {
          convertAndImportCertificate(encryption.get("ssl_certificate").asText(), keyStorePassword);
        } catch (final IOException | InterruptedException e) {
          throw new RuntimeException("Failed to import certificate into Java Keystore");
        }
        additionalParameters.add("sslConnection=true");
        additionalParameters.add("sslTrustStoreLocation=" + KEY_STORE_FILE_PATH);
        additionalParameters.add("sslTrustStorePassword=" + keyStorePassword);
      }
    }
    return additionalParameters;
  }

  private static String getKeyStorePassword(final JsonNode encryptionKeyStorePassword) {
    var keyStorePassword = KEY_STORE_PASS;
    if (!encryptionKeyStorePassword.isNull() || !encryptionKeyStorePassword.isEmpty()) {
      keyStorePassword = encryptionKeyStorePassword.asText();
    }
    return keyStorePassword;
  }

  private static void convertAndImportCertificate(final String certificate, final String keyStorePassword)
      throws IOException, InterruptedException {
    final Runtime run = Runtime.getRuntime();
    try (final PrintWriter out = new PrintWriter("certificate.pem", StandardCharsets.UTF_8)) {
      out.print(certificate);
    }
    runProcess("openssl x509 -outform der -in certificate.pem -out certificate.der", run);
    runProcess(
        "keytool -import -alias rds-root -keystore " + KEY_STORE_FILE_PATH + " -file certificate.der -storepass " + keyStorePassword + " -noprompt",
        run);
  }

  private static void runProcess(final String cmd, final Runtime run) throws IOException, InterruptedException {
    final Process pr = run.exec(cmd.split(" "));
    if (!pr.waitFor(30, TimeUnit.SECONDS)) {
      pr.destroy();
      throw new RuntimeException("Timeout while executing: " + cmd);
    }
  }

}
