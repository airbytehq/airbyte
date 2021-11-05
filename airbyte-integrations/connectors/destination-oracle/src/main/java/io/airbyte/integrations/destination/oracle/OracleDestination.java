/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OracleDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleDestination.class);
  public static final List<String> HOST_KEY = List.of("host");
  public static final List<String> PORT_KEY = List.of("port");

  public static final String DRIVER_CLASS = "oracle.jdbc.OracleDriver";

  public static final String COLUMN_NAME_AB_ID =
      "\"" + JavaBaseConstants.COLUMN_NAME_AB_ID.toUpperCase() + "\"";
  public static final String COLUMN_NAME_DATA =
      "\"" + JavaBaseConstants.COLUMN_NAME_DATA.toUpperCase() + "\"";
  public static final String COLUMN_NAME_EMITTED_AT =
      "\"" + JavaBaseConstants.COLUMN_NAME_EMITTED_AT.toUpperCase() + "\"";

  private static final String KEY_STORE_FILE_PATH = "clientkeystore.jks";
  private static final String KEY_STORE_PASS = RandomStringUtils.randomAlphanumeric(8);

  enum Protocol {
    TCP,
    TCPS
  }

  public OracleDestination() {
    super(DRIVER_CLASS, new OracleNameTransformer(), new OracleOperations("users"));
    System.setProperty("oracle.jdbc.timezoneAsRegion", "false");
  }

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new OracleDestination(), List.of("host"), List.of("port"));
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final List<String> additionalParameters = new ArrayList<>();

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

    if (!additionalParameters.isEmpty()) {
      final String connectionParams = String.join(";", additionalParameters);
      configBuilder.put("connection_properties", connectionParams);
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  private Protocol obtainConnectionProtocol(final JsonNode encryption,
                                            final List<String> additionalParameters) {
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

  private static void convertAndImportCertificate(final String certificate)
      throws IOException, InterruptedException {
    final Runtime run = Runtime.getRuntime();
    try (final PrintWriter out = new PrintWriter("certificate.pem")) {
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
