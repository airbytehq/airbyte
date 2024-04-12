package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.MongoSslUtils.SslMode.CCV;
import static io.airbyte.integrations.source.mongodb.MongoSslUtils.SslMode.DISABLED;
import static io.airbyte.integrations.source.mongodb.MongoConstants.PARAM_SSL_MODE_CCV;
import static io.airbyte.integrations.source.mongodb.MongoConstants.CLIENT_CERTIFICATE;
import static io.airbyte.integrations.source.mongodb.MongoConstants.CLIENT_CA_CERTIFICATE;
import static io.airbyte.integrations.source.mongodb.MongoConstants.CLIENT_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.CLIENT_KEY_STORE;
import static io.airbyte.integrations.source.mongodb.MongoConstants.KEY_STORE_TYPE;
import static io.airbyte.integrations.source.mongodb.MongoConstants.TRUST_STORE;
import static io.airbyte.integrations.source.mongodb.MongoConstants.TRUST_PASSWORD;
import static io.airbyte.integrations.source.mongodb.MongoConstants.TRUST_TYPE;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoSslUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoSslUtils.class);

  public static void setupCertificates(
    final String sslMode,
    final String caCertificate,
    final String clientCertificate,
    final String clientKey,
    final String clientKeyPassword
  ) {
    try {
      if (getSslVerifyMode(sslMode) == CCV) {
        LOGGER.info("Preparing SSL certificates for '{}' mode", PARAM_SSL_MODE_CCV);
        initCertificateStores(
          caCertificate,
          clientCertificate,
          clientKey,
          getOrGeneratePassword(clientKeyPassword)
        );
      }
    } catch (final IOException | InterruptedException e) {
      throw new RuntimeException("Failed to import certificate into Java Keystore");
    }
  }
  
  private static String getOrGeneratePassword(final String clientKeyPassword) {
    return clientKeyPassword != null && !clientKeyPassword.isEmpty() ? clientKeyPassword : RandomStringUtils.randomAlphanumeric(10);
  }

  private static void initCertificateStores(
    final String caCertificate,
    final String clientCertificate,
    final String clientKey,
    final String clientKeyPassword
  )
  throws IOException, InterruptedException {

    LOGGER.info("Try to generate '{}'", CLIENT_KEY_STORE);
    createCertificateFile(CLIENT_CERTIFICATE, clientCertificate);
    createCertificateFile(CLIENT_KEY, clientKey);

    runProcess(String.format("openssl pkcs12 -export -in %s -inkey %s -out %s -passout pass:%s",
        CLIENT_CERTIFICATE,
        CLIENT_KEY,
        CLIENT_KEY_STORE,
        clientKeyPassword));
    LOGGER.info("'{}' Generated", CLIENT_KEY_STORE);

    // Import the SSL certiﬁcate in the truststore

    LOGGER.info("Try to generate '{}'", CLIENT_CA_CERTIFICATE);
    createCertificateFile(CLIENT_CA_CERTIFICATE, caCertificate);
    LOGGER.info("'{}' Generated", CLIENT_CA_CERTIFICATE);
    
    LOGGER.info("Try to generate '{}'", TRUST_STORE);
    runProcess(String.format("keytool -import -file %s -alias mongoClient -keystore %s -storepass %s -noprompt",
        CLIENT_CA_CERTIFICATE,
        TRUST_STORE,
        TRUST_PASSWORD));
    LOGGER.info("'{}' Generated", TRUST_STORE);

    setSystemProperty(clientKeyPassword);
  }

  private static void runProcess(final String cmd) throws IOException, InterruptedException {
    ProcessBuilder processBuilder = new ProcessBuilder(cmd.split("\\s+"));
    Process process = processBuilder.start();    
    if (!process.waitFor(30, TimeUnit.SECONDS)) {
        process.destroy();
        throw new RuntimeException("Timeout while executing: " + cmd);
    }
  }

  private static void createCertificateFile(final String fileName, final String fileValue) throws IOException {
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

  public static boolean isValidSslMode(final String sslMode) {
    return sslMode != null && !sslMode.isEmpty() && !sslMode.equals(DISABLED.toString());
  }

  private static SslMode getSslVerifyMode(final String sslMode) {
    return SslMode.bySpec(sslMode).orElseThrow(() -> new IllegalArgumentException("unexpected ssl mode"));
  }

  public enum SslMode {

    DISABLED("disable"),
    CCV("CCV");

    public final List<String> spec;

    SslMode(final String... spec) {
      this.spec = Arrays.asList(spec);
    }

    public static Optional<SslMode> bySpec(final String spec) {
      return Arrays.stream(SslMode.values())
          .filter(sslMode -> sslMode.spec.contains(spec))
          .findFirst();
    }

  }

}
