/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.util;

import com.fasterxml.jackson.databind.JsonNode;

import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
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
  public static final String CUSTOM_TRUST_STORE = "customtruststore";
  public static final String CUSTOM_KEY_STORE = "customkeystore";
  public static final String SSL_MODE = "sslMode";
  public static final String DISABLE = "disable";
  public static final String VERIFY_CA = "VERIFY_CA";
  public static final String VERIFY_IDENTITY = "VERIFY_IDENTITY";
  public static final String ROOT_CERTIFICARE_NAME = "ca.pem";
  public static final String CLIENT_CERTIFICARE_NAME = "client-cert.pem";
  public static final String CLIENT_KEY_NAME = "client-key.pem";

  public static Map<String, String> obtainConnectionOptions(final JsonNode encryption) {
    Map<String, String> additionalParameters = new HashMap<>();
    if (!encryption.isNull()) {
      final var method = encryption.get(PARAM_MODE).asText().toUpperCase();
      String sslPassword = encryption.has(PARAM_CLIENT_KEY_PASSWORD) ? encryption.get(PARAM_CLIENT_KEY_PASSWORD).asText() : "";
      var keyStorePassword = RandomStringUtils.randomAlphanumeric(10);
      if (!sslPassword.isEmpty()) {
        keyStorePassword = sslPassword;
      }
      switch (method) {
        case VERIFY_CA -> {
          additionalParameters.putAll(obtainConnectionCaOptions(encryption, method, keyStorePassword));
        }
        case VERIFY_IDENTITY -> {
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
      convertAndImportFullCertificate(encryption.get(PARAM_CA_CERTIFICATE).asText(),
          encryption.get(PARAM_CLIENT_CERTIFICATE).asText(),
              encryption.get(PARAM_CLIENT_KEY).asText(), clientKeyPassword);
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }
    additionalParameters.put(TRUST_KEY_STORE_URL, CUSTOM_TRUST_STORE);
    additionalParameters.put(TRUST_KEY_STORE_PASS, clientKeyPassword);
    additionalParameters.put(CLIENT_KEY_STORE_URL, CUSTOM_KEY_STORE);
    additionalParameters.put(CLIENT_KEY_STORE_PASS, clientKeyPassword);
    additionalParameters.put(SSL_MODE, method.toUpperCase());
    return additionalParameters;
  }

  private static Map<String, String> obtainConnectionCaOptions(final JsonNode encryption,
                                                               final String method,
                                                               final String clientKeyPassword) {
    Map<String, String> additionalParameters = new HashMap<>();
    try {
      convertAndImportCaCertificate(encryption.get(PARAM_CA_CERTIFICATE).asText(), clientKeyPassword);
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }
    additionalParameters.put(TRUST_KEY_STORE_URL, CUSTOM_TRUST_STORE);
    additionalParameters.put(TRUST_KEY_STORE_PASS, clientKeyPassword);
    additionalParameters.put(SSL_MODE, method.toUpperCase());
    return additionalParameters;
  }

  private static void convertAndImportFullCertificate(final String caCertificate,
                                                      final String clientCertificate,
                                                      final String clientKey,
                                                      final String clientKeyPassword)
      throws IOException, InterruptedException {
    final Runtime run = Runtime.getRuntime();
    convertAndImportCaCertificate(caCertificate, clientKeyPassword);
    LOGGER.error("==>> check if KEY store exist");
    File f = new File(System.getProperty("user.dir") + "/" + CUSTOM_KEY_STORE);
    if (!f.exists()) {
      LOGGER.error("==> need create KEY store!!");
      createCertificateFile(CLIENT_CERTIFICARE_NAME, clientCertificate);
      createCertificateFile(CLIENT_KEY_NAME, clientKey);
      // add client certificate to the custom keystore
      runProcess("openssl pkcs12 -export -in client-cert.pem -inkey client-key.pem -out certificate.p12 -name \"certificate\" -passout pass:Passw0rd", run);
      // add client key to the custom keystore
      runProcess("keytool -importkeystore -srckeystore certificate.p12 -srcstoretype pkcs12 -destkeystore customkeystore -srcstorepass Passw0rd -deststoretype JKS -deststorepass Passw0rd", run);
      runProcess("rm " + CLIENT_KEY_NAME, run);

      String result = System.getProperty("user.dir") + "/" + CUSTOM_KEY_STORE;
      System.setProperty("javax.net.ssl.keyStore", result);
      System.setProperty("javax.net.ssl.keyStorePassword", clientKeyPassword);
    }
  }

  private static void convertAndImportCaCertificate(final String caCertificate,
                                                    final String clientKeyPassword)
      throws IOException, InterruptedException {
    LOGGER.error("==>> check if TRUST store exist");
    File f = new File(System.getProperty("user.dir") + "/" + CUSTOM_TRUST_STORE);
    if (!f.exists()) {
      LOGGER.error("==> need create TRUST tore!!");
      final Runtime run = Runtime.getRuntime();
      createCaCertificate(caCertificate, clientKeyPassword, run);
      updateTrustStoreSystemProperty(clientKeyPassword);
    }
  }

  private static void createCaCertificate(final String caCertificate,
                                          final String clientKeyPassword,
                                          final Runtime run)
      throws IOException, InterruptedException {
    createCertificateFile(ROOT_CERTIFICARE_NAME, caCertificate);
    // add CA certificate to the custom keystore
    runProcess("keytool -import -alias root-certificate -keystore " + CUSTOM_TRUST_STORE
        + " -file " + ROOT_CERTIFICARE_NAME + " -storepass " + clientKeyPassword + " -noprompt", run);
  }

  private static void updateTrustStoreSystemProperty(final String clientKeyPassword) {
    String result = System.getProperty("user.dir") + "/" + CUSTOM_TRUST_STORE;
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
