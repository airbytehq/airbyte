/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.db2;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.Db2JdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Db2Source extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(Db2Source.class);
  public static final String DRIVER_CLASS = "com.ibm.db2.jcc.DB2Driver";
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
        .put("username", config.get("username").asText())
        .put("password", config.get("password").asText())
        .build());

    // assume ssl if not explicitly mentioned.
    var additionalParams = obtainConnectionOptions(config.get("encryption"));
    if (!additionalParams.isEmpty()) {
      jdbcUrl.append(":").append(String.join(";", additionalParams));
      jdbcUrl.append(";");
      result = Jsons.jsonNode(ImmutableMap.builder()
          .put("jdbc_url", jdbcUrl.toString())
          .put("username", config.get("username").asText())
          .put("password", config.get("password").asText())
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

  /* Helpers */

  private List<String> obtainConnectionOptions(JsonNode encryption) {
    List<String> additionalParameters = new ArrayList<>();
    if (!encryption.isNull()) {
      String encryptionMethod = encryption.get("encryption_method").asText();
      if ("encrypted_verify_certificate".equals(encryptionMethod)) {
        var keyStorePassword = getKeyStorePassword(encryption.get("key_store_password"));
        try {
          convertAndImportCertificate(encryption.get("ssl_certificate").asText(), keyStorePassword);
        } catch (IOException | InterruptedException e) {
          throw new RuntimeException("Failed to import certificate into Java Keystore");
        }
        additionalParameters.add("sslConnection=true");
        additionalParameters.add("sslTrustStoreLocation=" + KEY_STORE_FILE_PATH);
        additionalParameters.add("sslTrustStorePassword=" + keyStorePassword);
      }
    }
    return additionalParameters;
  }

  private static String getKeyStorePassword(JsonNode encryptionKeyStorePassword) {
    var keyStorePassword = KEY_STORE_PASS;
    if (!encryptionKeyStorePassword.isNull() || !encryptionKeyStorePassword.isEmpty()) {
      keyStorePassword = encryptionKeyStorePassword.asText();
    }
    return keyStorePassword;
  }

  private static void convertAndImportCertificate(String certificate, String keyStorePassword)
      throws IOException, InterruptedException {
    Runtime run = Runtime.getRuntime();
    try (PrintWriter out = new PrintWriter("certificate.pem")) {
      out.print(certificate);
    }
    runProcess("openssl x509 -outform der -in certificate.pem -out certificate.der", run);
    runProcess(
        "keytool -import -alias rds-root -keystore " + KEY_STORE_FILE_PATH + " -file certificate.der -storepass " + keyStorePassword + " -noprompt",
        run);
  }

  private static void runProcess(String cmd, Runtime run) throws IOException, InterruptedException {
    Process pr = run.exec(cmd);
    if (!pr.waitFor(30, TimeUnit.SECONDS)) {
      pr.destroy();
      throw new RuntimeException("Timeout while executing: " + cmd);
    }
  }

}
