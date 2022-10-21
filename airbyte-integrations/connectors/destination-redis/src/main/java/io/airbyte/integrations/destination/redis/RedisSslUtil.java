package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.RandomStringUtils;

public class RedisSslUtil {

  public static final String PARAM_CLIENT_CERTIFICATE = "client_certificate";
  public static final String PARAM_CLIENT_KEY = "client_key";
  public static final String PARAM_CA_CERTIFICATE = "ca_certificate";
  public static final String PARAM_CLIENT_KEY_PASSWORD = "client_key_password";
  public static final String PARAM_SSL_MODE = "mode";
  public static final String PARAM_SSL_MODE_VERIFY_FULL = "verify-full";

  private static final String CLIENT_CERTIFICATE = "client.crt";
  private static final String CLIENT_CA_CERTIFICATE = "client-ca.crt";
  private static final String CLIENT_KEY = "client.key";
  private static final String CLIENT_KEY_STORE = "client_key_store.p12";
  private static final String KEY_STORE_TYPE = "PKCS12";
  private static final String TRUST_STORE = "truststore.jks";
  private static final String TRUST_PASSWORD = "truststore_pwd";
  private static final String TRUST_TYPE = "JKS";

  public static void setupSsl(final JsonNode encryption) {
    try {
      if (encryption.has(PARAM_SSL_MODE) && encryption.get(PARAM_SSL_MODE).asText().equals(PARAM_SSL_MODE_VERIFY_FULL)) {
        final String clientKeyPassword = getOrGeneratePassword(encryption);
        initCertificateStores(encryption.get(PARAM_CA_CERTIFICATE).asText(),
            encryption.get(PARAM_CLIENT_CERTIFICATE).asText(), encryption.get(PARAM_CLIENT_KEY).asText(), clientKeyPassword);
      }
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }
  }

  private static String getOrGeneratePassword(final JsonNode sslModeConfig) {
    final String clientKeyPassword;
    if (sslModeConfig.has(PARAM_CLIENT_KEY_PASSWORD) && !sslModeConfig.get(PARAM_CLIENT_KEY_PASSWORD).asText().isEmpty()) {
      clientKeyPassword = sslModeConfig.get(PARAM_CLIENT_KEY_PASSWORD).asText();
    } else {
      clientKeyPassword = RandomStringUtils.randomAlphanumeric(10);
    }
    return clientKeyPassword;
  }

  private static void initCertificateStores(
      final String caCertificate,
      final String clientCertificate,
      final String clientKey,
      final String clientKeyPassword)
      throws IOException, InterruptedException {

    createFile(CLIENT_CERTIFICATE, clientCertificate);
    createFile(CLIENT_KEY, clientKey);
    runProcess("openssl pkcs12 -export -in " + CLIENT_CERTIFICATE + " -inkey " + CLIENT_KEY + " -out " + CLIENT_KEY_STORE + " -passout pass:"
        + clientKeyPassword + "", Runtime.getRuntime());

    createFile(CLIENT_CA_CERTIFICATE, caCertificate);
    runProcess("keytool -import -file " + CLIENT_CA_CERTIFICATE + " -alias redis-ca -keystore " + TRUST_STORE + " -storepass " + TRUST_PASSWORD
        + "  -noprompt", Runtime.getRuntime());

    setSystemProperty(clientKeyPassword);
  }

  private static void runProcess(final String cmd, final Runtime run) throws IOException, InterruptedException {
    final Process pr = run.exec(cmd);
    if (!pr.waitFor(30, TimeUnit.SECONDS)) {
      pr.destroy();
      throw new RuntimeException("Timeout while executing: " + cmd);
    }
  }

  private static void createFile(final String fileName, final String fileValue) throws IOException {
    try (final PrintWriter out = new PrintWriter(fileName, StandardCharsets.UTF_8)) {
      out.print(fileValue);
    }
  }

  private static void setSystemProperty(final String clientKeyPassword) {
    System.setProperty("javax.net.ssl.keyStoreType", KEY_STORE_TYPE);
    System.setProperty("javax.net.ssl.keyStore", CLIENT_KEY_STORE);
    System.setProperty("javax.net.ssl.keyStorePassword", clientKeyPassword);
    System.setProperty("javax.net.ssl.trustStoreType", TRUST_TYPE);
    System.setProperty("javax.net.ssl.trustStore", TRUST_STORE);
    System.setProperty("javax.net.ssl.trustStorePassword", TRUST_PASSWORD);
  }

}
