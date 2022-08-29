/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.util;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresSslConnectionUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSslConnectionUtils.class);
  private static final String CA_CERTIFICATE = "ca.crt";
  private static final String CLIENT_CERTIFICATE = "client.crt";
  private static final String CLIENT_KEY = "client.key";
  private static final String CLIENT_ENCRYPTED_KEY = "client.pk8";

  public static final String PARAM_MODE = "mode";
  public static final String PARAM_SSL = "ssl";
  public static final String PARAM_SSL_MODE = "ssl_mode";
  public static final String PARAM_SSLMODE = "sslmode";
  public static final String PARAM_CLIENT_KEY_PASSWORD = "client_key_password";
  public static final String PARAM_CA_CERTIFICATE = "ca_certificate";
  public static final String PARAM_CLIENT_CERTIFICATE = "client_certificate";
  public static final String PARAM_CLIENT_KEY = "client_key";

  public static final String VERIFY_CA = "verify-ca";
  public static final String VERIFY_FULL = "verify-full";
  public static final String DISABLE = "disable";
  public static final String TRUE_STRING_VALUE = "true";
  public static final String ENCRYPT_FILE_NAME = "encrypt";
  public static final String FACTORY_VALUE = "org.postgresql.ssl.DefaultJavaSSLFactory";

  public static Map<String, String> obtainConnectionOptions(final JsonNode encryption) {
    final Map<String, String> additionalParameters = new HashMap<>();
    if (!encryption.isNull()) {
      final var method = encryption.get(PARAM_MODE).asText();
      var keyStorePassword = checkOrCreatePassword(encryption);
      switch (method) {
        case VERIFY_CA -> {
          additionalParameters.putAll(obtainConnectionCaOptions(encryption, method, keyStorePassword));
        }
        case VERIFY_FULL -> {
          additionalParameters.putAll(obtainConnectionFullOptions(encryption, method, keyStorePassword));
        }
        default -> {
          additionalParameters.put(PARAM_SSL, TRUE_STRING_VALUE);
          additionalParameters.put(PARAM_SSLMODE, method);
        }
      }
    }
    return additionalParameters;
  }

  private static String checkOrCreatePassword(final JsonNode encryption) {
    String sslPassword = encryption.has(PARAM_CLIENT_KEY_PASSWORD) ? encryption.get(PARAM_CLIENT_KEY_PASSWORD).asText() : "";
    var keyStorePassword = RandomStringUtils.randomAlphanumeric(10);
    if (sslPassword.isEmpty()) {
      var file = new File(ENCRYPT_FILE_NAME);
      if (file.exists()) {
        keyStorePassword = readFile(file);
      } else {
        try {
          createCertificateFile(ENCRYPT_FILE_NAME, keyStorePassword);
        } catch (final IOException e) {
          throw new RuntimeException("Failed to create encryption file ");
        }
      }
    } else {
      keyStorePassword = sslPassword;
    }
    return keyStorePassword;
  }

  private static String readFile(final File file) {
    try {
      BufferedReader reader = new BufferedReader(new FileReader(file, StandardCharsets.UTF_8));
      String currentLine = reader.readLine();
      reader.close();
      return currentLine;
    } catch (final IOException e) {
      throw new RuntimeException("Failed to read file with encryption");
    }
  }

  private static Map<String, String> obtainConnectionFullOptions(final JsonNode encryption,
                                                                 final String method,
                                                                 final String clientKeyPassword) {
    final Map<String, String> additionalParameters = new HashMap<>();
    try {
      convertAndImportFullCertificate(encryption.get(PARAM_CA_CERTIFICATE).asText(),
          encryption.get(PARAM_CLIENT_CERTIFICATE).asText(), encryption.get(PARAM_CLIENT_KEY).asText(), clientKeyPassword);
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }
    additionalParameters.put("ssl", TRUE_STRING_VALUE);
    additionalParameters.put("sslmode", method);
    additionalParameters.put("sslrootcert", CA_CERTIFICATE);
    additionalParameters.put("sslcert", CLIENT_CERTIFICATE);
    additionalParameters.put("sslkey", CLIENT_ENCRYPTED_KEY);
    additionalParameters.put("sslfactory", FACTORY_VALUE);
    return additionalParameters;
  }

  private static Map<String, String> obtainConnectionCaOptions(final JsonNode encryption,
                                                               final String method,
                                                               final String clientKeyPassword) {
    final Map<String, String> additionalParameters = new HashMap<>();
    try {
      convertAndImportCaCertificate(encryption.get(PARAM_CA_CERTIFICATE).asText(), clientKeyPassword);
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }
    additionalParameters.put("ssl", TRUE_STRING_VALUE);
    additionalParameters.put("sslmode", method);
    additionalParameters.put("sslrootcert", CA_CERTIFICATE);
    additionalParameters.put("sslfactory", FACTORY_VALUE);
    return additionalParameters;
  }

  private static void convertAndImportFullCertificate(final String caCertificate,
                                                      final String clientCertificate,
                                                      final String clientKey,
                                                      final String clientKeyPassword)
      throws IOException, InterruptedException {
    final Runtime run = Runtime.getRuntime();
    createCaCertificate(caCertificate, clientKeyPassword, run);
    createCertificateFile(CLIENT_CERTIFICATE, clientCertificate);
    createCertificateFile(CLIENT_KEY, clientKey);
    // add client certificate to the custom keystore
    runProcess("keytool -alias client-certificate -keystore customkeystore"
        + " -import -file " + CLIENT_CERTIFICATE + " -storepass " + clientKeyPassword + " -noprompt", run);
    // convert client.key to client.pk8 based on the documentation
    runProcess("openssl pkcs8 -topk8 -inform PEM -in " + CLIENT_KEY + " -outform DER -out "
        + CLIENT_ENCRYPTED_KEY + " -nocrypt", run);
    runProcess("rm " + CLIENT_KEY, run);

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
    createCertificateFile(CA_CERTIFICATE, caCertificate);
    // add CA certificate to the custom keystore
    runProcess("keytool -import -alias rds-root -keystore customkeystore"
        + " -file " + CA_CERTIFICATE + " -storepass " + clientKeyPassword + " -noprompt", run);
  }

  private static void updateTrustStoreSystemProperty(final String clientKeyPassword) {
    String result = System.getProperty("user.dir") + "/customkeystore";
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
