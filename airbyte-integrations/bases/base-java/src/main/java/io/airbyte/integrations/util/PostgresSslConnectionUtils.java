/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.util;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.RandomStringUtils;

public class PostgresSslConnectionUtils {

  private static final String KEY_STORE_PASS = RandomStringUtils.randomAlphanumeric(8);
  private static final String CA_CERTIFICATE = "ca.crt";
  private static final String CLIENT_CERTIFICATE = "client.crt";
  private static final String CLIENT_KEY = "client.key";
  private static final String CLIENT_ENCRYPTED_KEY = "client.pk8";

  public static final String MODE_KEY = "mode";
  public static final String SSL_KEY = "ssl";
  public static final String SSL_MODE_KEY = "ssl_mode";
  public static final String CLIENT_KEY_PASSWORD_KEY = "client_key_password";
  public static final String CA_CERTIFICATE_KEY = "ca_certificate";
  public static final String CLIENT_CERTIFICATE_KEY = "client_certificate";
  public static final String CLIENT_KEY_KEY = "client_key";

  public static final String VERIFY_CA = "verify-ca";
  public static final String VERIFY_FULL = "verify-full";
  public static final String DISABLE = "disable";

  public static Map<String, String> obtainConnectionOptions(final JsonNode encryption) {
    final Map<String, String> additionalParameters = new HashMap<>();
    if (!encryption.isNull()) {
      final var method = encryption.get(MODE_KEY).asText();
      final var clientKeyPassword = getKeyStorePassword(encryption.get(CLIENT_KEY_PASSWORD_KEY));
      switch (method) {
        case VERIFY_CA -> additionalParameters.putAll(obtainConnectionCaOptions(encryption, method, clientKeyPassword));
        case VERIFY_FULL -> additionalParameters.putAll(obtainConnectionFullOptions(encryption, method, clientKeyPassword));
        default -> {
          additionalParameters.put("ssl", "true");
          additionalParameters.put("sslmode", method);
        }
      }
    }
    return additionalParameters;
  }

  private static Map<String, String> obtainConnectionFullOptions(final JsonNode encryption,
                                                                 final String method,
                                                                 final String clientKeyPassword) {
    final Map<String, String> additionalParameters = new HashMap<>();
    try {
      convertAndImportFullCertificate(encryption.get(CA_CERTIFICATE_KEY).asText(),
          encryption.get(CLIENT_CERTIFICATE_KEY).asText(), encryption.get(CLIENT_KEY_KEY).asText(), clientKeyPassword);
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }
    additionalParameters.put("ssl", "true");
    additionalParameters.put("sslmode", method);
    additionalParameters.put("sslrootcert", CA_CERTIFICATE);
    additionalParameters.put("sslcert", CLIENT_CERTIFICATE);
    additionalParameters.put("sslkey", CLIENT_ENCRYPTED_KEY);
    additionalParameters.put("sslfactory", "org.postgresql.ssl.DefaultJavaSSLFactory");
    return additionalParameters;
  }

  private static Map<String, String> obtainConnectionCaOptions(final JsonNode encryption,
                                                               final String method,
                                                               final String clientKeyPassword) {
    final Map<String, String> additionalParameters = new HashMap<>();
    try {
      convertAndImportCaCertificate(encryption.get(CA_CERTIFICATE_KEY).asText(), clientKeyPassword);
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }
    additionalParameters.put("ssl", "true");
    additionalParameters.put("sslmode", method);
    additionalParameters.put("sslrootcert", CA_CERTIFICATE);
    additionalParameters.put("sslfactory", "org.postgresql.ssl.DefaultJavaSSLFactory");
    return additionalParameters;
  }

  private static void convertAndImportFullCertificate(final String caCertificate,
                                                      final String clientCertificate,
                                                      final String clientKey,
                                                      final String clientKeyPassword)
      throws IOException, InterruptedException {
    final Runtime run = Runtime.getRuntime();
    createCertificateFile(CA_CERTIFICATE, caCertificate);
    createCertificateFile(CLIENT_CERTIFICATE, clientCertificate);
    createCertificateFile(CLIENT_KEY, clientKey);
    // add CA certificate to the custom keystore
    runProcess("keytool -alias ca-certificate -keystore customkeystore"
        + " -import -file " + CA_CERTIFICATE + " -storepass " + clientKeyPassword + " -noprompt", run);
    // add client certificate to the custom keystore
    runProcess("keytool -alias client-certificate -keystore customkeystore"
        + " -import -file " + CLIENT_CERTIFICATE + " -storepass " + clientKeyPassword + " -noprompt", run);
    // convert client.key to client.pk8 based on the documentation
    runProcess("openssl pkcs8 -topk8 -inform PEM -in " + CLIENT_KEY + " -outform DER -out "
        + CLIENT_ENCRYPTED_KEY + " -nocrypt", run);
    runProcess("rm " + CLIENT_KEY, run);

    String result = System.getProperty("user.dir") + "/customkeystore";
    System.setProperty("javax.net.ssl.trustStore", result);
    System.setProperty("javax.net.ssl.trustStorePassword", clientKeyPassword);
  }

  private static void convertAndImportCaCertificate(final String caCertificate,
                                                    final String clientKeyPassword)
      throws IOException, InterruptedException {
    final Runtime run = Runtime.getRuntime();
    createCertificateFile(CA_CERTIFICATE, caCertificate);
    runProcess("keytool -import -alias rds-root -keystore customkeystore"
        + " -file " + CA_CERTIFICATE + " -storepass " + clientKeyPassword + " -noprompt", run);

    String result = System.getProperty("user.dir") + "/customkeystore";
    System.setProperty("javax.net.ssl.trustStore", result);
    System.setProperty("javax.net.ssl.trustStorePassword", clientKeyPassword);
  }

  private static void createCertificateFile(String fileName, String fileValue) throws IOException {
    try (final PrintWriter out = new PrintWriter(fileName, StandardCharsets.UTF_8)) {
      out.print(fileValue);
    }
  }

  private static String getKeyStorePassword(final JsonNode sslMode) {
    var keyStorePassword = KEY_STORE_PASS;
    if (!sslMode.isNull() || !sslMode.isEmpty()) {
      keyStorePassword = sslMode.asText();
    }
    return keyStorePassword;
  }

  private static void runProcess(final String cmd, final Runtime run) throws IOException, InterruptedException {
    final Process pr = run.exec(cmd);
    if (!pr.waitFor(50, TimeUnit.SECONDS)) {
      pr.destroy();
      throw new RuntimeException("Timeout while executing: " + cmd);
    }
  }

}
