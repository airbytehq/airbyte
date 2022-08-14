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
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlSslConnectionUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlSslConnectionUtils.class);

  public static final String PARAM_MODE = "mode";
  public static final String PARAM_CLIENT_KEY_PASSWORD = "client_key_password";
  public static final String PARAM_CA_CERTIFICATE = "ca_certificate";
  public static final String PARAM_CLIENT_CERTIFICATE = "client_certificate";
  public static final String PARAM_CLIENT_KEY = "client_key";
  public static final String TRUST_KEY_STORE_URL = "trustCertificateKeyStoreUrl";
  public static final String TRUST_KEY_STORE_PASS = "trustCertificateKeyStorePassword";
  public static final String CLIENT_KEY_STORE_URL = "clientCertificateKeyStoreUrl";
  public static final String CLIENT_KEY_STORE_PASS = "clientCertificateKeyStorePassword";
  public static final String CUSTOM_TRUST_STORE = "customtruststore.jks";
  public static final String CUSTOM_KEY_STORE = "customkeystore.jks";
  public static final String SSL_MODE = "sslMode";
  public static final String VERIFY_CA = "VERIFY_CA";
  public static final String VERIFY_IDENTITY = "VERIFY_IDENTITY";
  public static final String ROOT_CERTIFICARE_NAME = "ca-cert.pem";
  public static final String ROOT_CERTIFICARE_DER_NAME = "ca-cert.der";
  public static final String CLIENT_CERTIFICARE_NAME = "client-cert.pem";
  public static final String CLIENT_KEY_NAME = "client-key.pem";
  public static final String CLIENT_CERT_P12 = "certificate.p12";
  public static final String ENCRYPT_FILE_NAME = "encrypt";

  public static Map<String, String> obtainConnection(final JsonNode encryption) {
    Map<String, String> additionalParameters = new HashMap<>();
    if (!encryption.isNull()) {
      final var method = encryption.get(PARAM_MODE).asText().toUpperCase();
      var keyStorePassword = checkOrCreatePassword(encryption);
      if (method.equals(VERIFY_CA) || method.equals(VERIFY_IDENTITY)) {
        additionalParameters.putAll(checkCertificatesAndObtainConnection(encryption, method, keyStorePassword));
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
    BufferedReader reader = new BufferedReader(new FileReader(file));
    String currentLine = reader.readLine();
    reader.close();
    return currentLine;
    } catch (final IOException e) {
      throw new RuntimeException("Failed to read file with encryption");
    }
  }

  private static Map<String, String> checkCertificatesAndObtainConnection(final JsonNode encryption,
                                                                          final String mode,
                                                                          final String clientKeyPassword) {
    var clientCert = encryption.has(PARAM_CLIENT_CERTIFICATE) &&
            !encryption.get(PARAM_CLIENT_CERTIFICATE).asText().isEmpty() ? encryption.get(PARAM_CLIENT_CERTIFICATE).asText() : null;
    var clientKey = encryption.has(PARAM_CLIENT_KEY) &&
            !encryption.get(PARAM_CLIENT_KEY).asText().isEmpty() ? encryption.get(PARAM_CLIENT_KEY).asText() : null;
    if (Objects.nonNull(clientCert) && Objects.nonNull(clientKey)) {
      return obtainConnectionWithFullCertificatesOptions(encryption, mode, clientKeyPassword);
    } else if (Objects.isNull(clientCert) && Objects.isNull(clientKey)) {
      return obtainConnectionWithCaCertificateOptions(encryption, mode, clientKeyPassword);
    } else {
      throw new RuntimeException("Both fields \"Client certificate\" and \"Client key\" must be added to connect with client certificates.");
    }
  }

  private static Map<String, String> obtainConnectionWithFullCertificatesOptions(final JsonNode encryption,
                                                                                 final String mode,
                                                                                 final String clientKeyPassword) {
    Map<String, String> additionalParameters = new HashMap<>();
    try {
      convertAndImportFullCertificate(encryption.get(PARAM_CA_CERTIFICATE).asText(),
          encryption.get(PARAM_CLIENT_CERTIFICATE).asText(),
          encryption.get(PARAM_CLIENT_KEY).asText(), clientKeyPassword);
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }
    additionalParameters.put(TRUST_KEY_STORE_URL, "file:" + CUSTOM_TRUST_STORE);
    additionalParameters.put(TRUST_KEY_STORE_PASS, clientKeyPassword);
    additionalParameters.put(CLIENT_KEY_STORE_URL, "file:" + CUSTOM_KEY_STORE);
    additionalParameters.put(CLIENT_KEY_STORE_PASS, clientKeyPassword);
    additionalParameters.put(SSL_MODE, mode);

    updateTrustStoreSystemProperty(clientKeyPassword);
    System.setProperty("javax.net.ssl.keyStore", CUSTOM_KEY_STORE);
    System.setProperty("javax.net.ssl.keyStorePassword", clientKeyPassword);

    return additionalParameters;
  }

  private static Map<String, String> obtainConnectionWithCaCertificateOptions(final JsonNode encryption,
                                                                              final String mode,
                                                                              final String clientKeyPassword) {
    Map<String, String> additionalParameters = new HashMap<>();
    try {
      convertAndImportCaCertificate(encryption.get(PARAM_CA_CERTIFICATE).asText(), clientKeyPassword);
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }
    additionalParameters.put(TRUST_KEY_STORE_URL, "file:" + CUSTOM_TRUST_STORE);
    additionalParameters.put(TRUST_KEY_STORE_PASS, clientKeyPassword);
    additionalParameters.put(SSL_MODE, mode);

    updateTrustStoreSystemProperty(clientKeyPassword);

    return additionalParameters;
  }

  private static void convertAndImportFullCertificate(final String caCertificate,
                                                      final String clientCertificate,
                                                      final String clientKey,
                                                      final String clientKeyPassword)
      throws IOException, InterruptedException {
    final Runtime run = Runtime.getRuntime();
    convertAndImportCaCertificate(caCertificate, clientKeyPassword);
    createCertificateFile(CLIENT_CERTIFICARE_NAME, clientCertificate);
    createCertificateFile(CLIENT_KEY_NAME, clientKey);
    // add client certificate to the custom keystore
    runProcess("openssl pkcs12 -export -in " + CLIENT_CERTIFICARE_NAME + " -inkey " + CLIENT_KEY_NAME +
        " -out " + CLIENT_CERT_P12 + " -name \"certificate\" -passout pass:" + clientKeyPassword, run);
    // add client key to the custom keystore
    runProcess("keytool -importkeystore -srckeystore " + CLIENT_CERT_P12 +
        " -srcstoretype pkcs12 -destkeystore " + CUSTOM_KEY_STORE + " -srcstorepass " + clientKeyPassword +
        " -deststoretype JKS -deststorepass " + clientKeyPassword + " -noprompt", run);
  }

  private static void convertAndImportCaCertificate(final String caCertificate,
                                                    final String clientKeyPassword)
      throws IOException, InterruptedException {
    final Runtime run = Runtime.getRuntime();
    createCaCertificate(caCertificate, clientKeyPassword, run);
  }

  private static void createCaCertificate(final String caCertificate,
                                          final String clientKeyPassword,
                                          final Runtime run)
      throws IOException, InterruptedException {
    createCertificateFile(ROOT_CERTIFICARE_NAME, caCertificate);
    // add CA certificate to the custom keystore
    runProcess("openssl x509 -outform der -in " + ROOT_CERTIFICARE_NAME + " -out " + ROOT_CERTIFICARE_DER_NAME, run);
    runProcess("keytool -importcert -alias root-certificate -keystore " + CUSTOM_TRUST_STORE
        + " -file " + ROOT_CERTIFICARE_DER_NAME + " -storepass " + clientKeyPassword + " -noprompt", run);
  }

  private static void updateTrustStoreSystemProperty(final String clientKeyPassword) {
    System.setProperty("javax.net.ssl.trustStore", CUSTOM_TRUST_STORE);
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
