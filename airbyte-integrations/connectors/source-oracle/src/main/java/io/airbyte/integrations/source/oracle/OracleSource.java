/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.OracleJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import java.io.IOException;
import java.io.PrintWriter;
import java.sql.JDBCType;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OracleSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleSource.class);

  public static final String DRIVER_CLASS = "oracle.jdbc.OracleDriver";

  private List<String> schemas;

  private static final String KEY_STORE_FILE_PATH = "clientkeystore.jks";
  private static final String KEY_STORE_PASS = RandomStringUtils.randomAlphanumeric(8);

  enum Protocol {
    TCP,
    TCPS
  }

  public OracleSource() {
    super(DRIVER_CLASS, new OracleJdbcStreamingQueryConfiguration());
  }

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new OracleSource(), List.of("host"), List.of("port"));
  }

  @Override
  public JsonNode toDatabaseConfig(JsonNode config) {
    List<String> additionalParameters = new ArrayList<>();

    Protocol protocol = config.has("encryption")
        ? obtainConnectionProtocol(config.get("encryption"), additionalParameters)
        : Protocol.TCP;
    final String connectionString = String.format(
        "jdbc:oracle:thin:@(DESCRIPTION=(ADDRESS=(PROTOCOL=%s)(HOST=%s)(PORT=%s))(CONNECT_DATA=(SID=%s)))",
        protocol,
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("sid").asText());

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", connectionString);

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
    }

    // Use the upper-cased username by default.
    schemas = List.of(config.get("username").asText().toUpperCase(Locale.ROOT));
    if (config.has("schemas") && config.get("schemas").isArray()) {
      schemas = new ArrayList<>();
      for (final JsonNode schema : config.get("schemas")) {
        schemas.add(schema.asText());
      }
    }
    if (!additionalParameters.isEmpty()) {
      String connectionParams = String.join(";", additionalParameters);
      configBuilder.put("connection_properties", connectionParams);
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  private Protocol obtainConnectionProtocol(JsonNode encryption, List<String> additionalParameters) {
    String encryptionMethod = encryption.get("encryption_method").asText();
    switch (encryptionMethod) {
      case "unencrypted" -> {
        return Protocol.TCP;
      }
      case "client_nne" -> {
        String algorithm = encryption.get("encryption_algorithm").asText();
        additionalParameters.add("oracle.net.encryption_client=REQUIRED");
        additionalParameters.add("oracle.net.encryption_types_client=( " + algorithm + " )");
        return Protocol.TCP;
      }
      case "encrypted_verify_certificate" -> {
        try {
          convertAndImportCertificate(encryption.get("ssl_certificate").asText());
        } catch (IOException | InterruptedException e) {
          throw new RuntimeException("Failed to import certificate into Java Keystore");
        }
        additionalParameters.add("javax.net.ssl.trustStore=" + KEY_STORE_FILE_PATH);
        additionalParameters.add("javax.net.ssl.trustStoreType=JKS");
        additionalParameters.add("javax.net.ssl.trustStorePassword=" + KEY_STORE_PASS);
        return Protocol.TCPS;
      }
    }
    throw new RuntimeException(
        "Failed to obtain connection protocol from config " + encryption.asText());
  }

  private static void convertAndImportCertificate(String certificate) throws IOException, InterruptedException {
    Runtime run = Runtime.getRuntime();
    try (PrintWriter out = new PrintWriter("certificate.pem")) {
      out.print(certificate);
    }
    runProcess("openssl x509 -outform der -in certificate.pem -out certificate.der", run);
    runProcess(
        "keytool -import -alias rds-root -keystore " + KEY_STORE_FILE_PATH + " -file certificate.der -storepass " + KEY_STORE_PASS + " -noprompt",
        run);
  }

  private static void runProcess(String cmd, Runtime run) throws IOException, InterruptedException {
    Process pr = run.exec(cmd);
    if (!pr.waitFor(30, TimeUnit.SECONDS)) {
      pr.destroy();
      throw new RuntimeException("Timeout while executing: " + cmd);
    } ;
  }

  @Override
  public List<TableInfo<CommonField<JDBCType>>> discoverInternal(JdbcDatabase database) throws Exception {
    List<TableInfo<CommonField<JDBCType>>> internals = new ArrayList<>();
    for (String schema : schemas) {
      LOGGER.debug("Discovering schema: {}", schema);
      internals.addAll(super.discoverInternal(database, schema));
    }

    for (TableInfo<CommonField<JDBCType>> info : internals) {
      LOGGER.debug("Found table: {}", info.getName());
    }

    return internals;
  }

  /**
   * Since the Oracle connector allows a user to specify schemas, and picks a default schemas
   * otherwise, system tables are never included, and do not need to be excluded by default.
   */
  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of();
  }

  public static void main(String[] args) throws Exception {
    final Source source = OracleSource.sshWrappedSource();
    LOGGER.info("starting source: {}", OracleSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", OracleSource.class);
  }

}
