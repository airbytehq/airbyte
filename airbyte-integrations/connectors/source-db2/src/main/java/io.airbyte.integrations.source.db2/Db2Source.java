/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.db2;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.Db2JdbcStreamingQueryConfiguration;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.dto.JdbcPrivilegeDto;
import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Db2Source extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(Db2Source.class);
  public static final String DRIVER_CLASS = "com.ibm.db2.jcc.DB2Driver";
  public static final String USERNAME = "username";
  public static final String PASSWORD = "password";
  private static Db2SourceOperations operations;

  private static final String KEY_STORE_PASS = RandomStringUtils.randomAlphanumeric(8);
  private static final String KEY_STORE_FILE_PATH = "clientkeystore.jks";

  public Db2Source() {
    super(DRIVER_CLASS, new Db2JdbcStreamingQueryConfiguration(), new Db2SourceOperations());
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new Db2Source();
    LOGGER.info("starting source: {}", Db2Source.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", Db2Source.class);
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:db2://%s:%s/%s",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("db").asText()));

    var result = Jsons.jsonNode(ImmutableMap.builder()
        .put("jdbc_url", jdbcUrl.toString())
        .put(USERNAME, config.get(USERNAME).asText())
        .put(PASSWORD, config.get(PASSWORD).asText())
        .build());

    // assume ssl if not explicitly mentioned.
    final var additionalParams = obtainConnectionOptions(config.get("encryption"));
    if (!additionalParams.isEmpty()) {
      jdbcUrl.append(":").append(String.join(";", additionalParams));
      jdbcUrl.append(";");
      result = Jsons.jsonNode(ImmutableMap.builder()
          .put("jdbc_url", jdbcUrl.toString())
          .put(USERNAME, config.get(USERNAME).asText())
          .put(PASSWORD, config.get(PASSWORD).asText())
          .put("connection_properties", additionalParams)
          .build());
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
  public Set<JdbcPrivilegeDto> getPrivilegesTableForCurrentUser(final JdbcDatabase database, final String schema) throws SQLException {
    return database
        .query(getPrivileges(), sourceOperations::rowToJson)
        .map(this::getPrivilegeDto)
        .collect(Collectors.toSet());
  }

  private CheckedFunction<Connection, PreparedStatement, SQLException> getPrivileges() {
    return connection -> connection.prepareStatement(
        "SELECT DISTINCT OBJECTNAME, OBJECTSCHEMA FROM SYSIBMADM.PRIVILEGES WHERE OBJECTTYPE = 'TABLE' AND PRIVILEGE = 'SELECT' AND AUTHID = SESSION_USER");
  }

  private JdbcPrivilegeDto getPrivilegeDto(JsonNode jsonNode) {
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
    try (final PrintWriter out = new PrintWriter("certificate.pem")) {
      out.print(certificate);
    }
    runProcess("openssl x509 -outform der -in certificate.pem -out certificate.der", run);
    runProcess(
        "keytool -import -alias rds-root -keystore " + KEY_STORE_FILE_PATH + " -file certificate.der -storepass " + keyStorePassword + " -noprompt",
        run);
  }

  private static void runProcess(final String cmd, final Runtime run) throws IOException, InterruptedException {
    final Process pr = run.exec(cmd);
    if (!pr.waitFor(30, TimeUnit.SECONDS)) {
      pr.destroy();
      throw new RuntimeException("Timeout while executing: " + cmd);
    }
  }

}
