/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.sql.JDBCType;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OracleSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleSource.class);

  public static final String DRIVER_CLASS = DatabaseDriver.ORACLE.getDriverClassName();

  private List<String> schemas;

  private static final String KEY_STORE_FILE_PATH = "clientkeystore.jks";
  private static final String KEY_STORE_PASS = RandomStringUtils.randomAlphanumeric(8);

  enum Protocol {
    TCP,
    TCPS
  }

  public OracleSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, JdbcUtils.getDefaultSourceOperations());
  }

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new OracleSource(), List.of("host"), List.of("port"));
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final List<String> additionalParameters = new ArrayList<>();

    /*
     * The property useFetchSizeWithLongColumn required to select LONG or LONG RAW columns. Oracle
     * recommends avoiding LONG and LONG RAW columns. Use LOB instead. They are included in Oracle only
     * for legacy reasons. THIS IS A THIN ONLY PROPERTY. IT SHOULD NOT BE USED WITH ANY OTHER DRIVERS.
     * See https://docs.oracle.com/cd/E11882_01/appdev.112/e13995/oracle/jdbc/OracleDriver.html
     * https://docs.oracle.com/cd/B19306_01/java.102/b14355/jstreams.htm#i1014085
     */
    additionalParameters.add("oracle.jdbc.useFetchSizeWithLongColumn=true");

    final Protocol protocol = config.has("encryption")
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

    if (config.get("jdbc_url_params") != null && !config.get("jdbc_url_params").asText().isEmpty()) {
      additionalParameters.addAll(List.of(config.get("jdbc_url_params").asText().split("&")));
    }

    if (!additionalParameters.isEmpty()) {
      final String connectionParams = String.join(getJdbcParameterDelimiter(), additionalParameters);
      configBuilder.put("connection_properties", connectionParams);
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  private Protocol obtainConnectionProtocol(final JsonNode encryption, final List<String> additionalParameters) {
    final String encryptionMethod = encryption.get("encryption_method").asText();
    switch (encryptionMethod) {
      case "unencrypted" -> {
        return Protocol.TCP;
      }
      case "client_nne" -> {
        final String algorithm = encryption.get("encryption_algorithm").asText();
        additionalParameters.add("oracle.net.encryption_client=REQUIRED");
        additionalParameters.add("oracle.net.encryption_types_client=( " + algorithm + " )");
        return Protocol.TCP;
      }
      case "encrypted_verify_certificate" -> {
        try {
          convertAndImportCertificate(encryption.get("ssl_certificate").asText());
        } catch (final IOException | InterruptedException e) {
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

  private static void convertAndImportCertificate(final String certificate) throws IOException, InterruptedException {
    final Runtime run = Runtime.getRuntime();
    try (final PrintWriter out = new PrintWriter("certificate.pem", StandardCharsets.UTF_8)) {
      out.print(certificate);
    }
    runProcess("openssl x509 -outform der -in certificate.pem -out certificate.der", run);
    runProcess(
        "keytool -import -alias rds-root -keystore " + KEY_STORE_FILE_PATH + " -file certificate.der -storepass " + KEY_STORE_PASS + " -noprompt",
        run);
  }

  private static void runProcess(final String cmd, final Runtime run) throws IOException, InterruptedException {
    final Process pr = run.exec(cmd);
    if (!pr.waitFor(30, TimeUnit.SECONDS)) {
      pr.destroy();
      throw new RuntimeException("Timeout while executing: " + cmd);
    } ;
  }

  @Override
  public List<TableInfo<CommonField<JDBCType>>> discoverInternal(final JdbcDatabase database) throws Exception {
    final List<TableInfo<CommonField<JDBCType>>> internals = new ArrayList<>();
    for (final String schema : schemas) {
      LOGGER.debug("Discovering schema: {}", schema);
      internals.addAll(super.discoverInternal(database, schema));
    }

    for (final TableInfo<CommonField<JDBCType>> info : internals) {
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

  @Override
  protected String getJdbcParameterDelimiter() {
    return ";";
  }

  public static void main(final String[] args) throws Exception {
    final Source source = OracleSource.sshWrappedSource();
    LOGGER.info("starting source: {}", OracleSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", OracleSource.class);
  }

}
