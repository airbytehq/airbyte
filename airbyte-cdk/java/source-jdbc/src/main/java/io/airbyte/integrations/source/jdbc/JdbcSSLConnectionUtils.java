/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.util.SSLCertificateUtils;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.CertificateException;
import java.security.spec.InvalidKeySpecException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JdbcSSLConnectionUtils {

  public static final String SSL_MODE = "sslMode";

  public static final String TRUST_KEY_STORE_URL = "trustCertificateKeyStoreUrl";
  public static final String TRUST_KEY_STORE_PASS = "trustCertificateKeyStorePassword";
  public static final String CLIENT_KEY_STORE_URL = "clientCertificateKeyStoreUrl";
  public static final String CLIENT_KEY_STORE_PASS = "clientCertificateKeyStorePassword";
  public static final String CLIENT_KEY_STORE_TYPE = "clientCertificateKeyStoreType";
  public static final String TRUST_KEY_STORE_TYPE = "trustCertificateKeyStoreType";
  public static final String KEY_STORE_TYPE_PKCS12 = "PKCS12";
  public static final String PARAM_MODE = "mode";
  Pair<URI, String> caCertKeyStorePair;
  Pair<URI, String> clientCertKeyStorePair;

  public enum SslMode {

    DISABLED("disable"),
    ALLOWED("allow"),
    PREFERRED("preferred", "prefer"),
    REQUIRED("required", "require"),
    VERIFY_CA("verify_ca", "verify-ca"),
    VERIFY_IDENTITY("verify_identity", "verify-full");

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

  private static final Logger LOGGER = LoggerFactory.getLogger(JdbcSSLConnectionUtils.class.getClass());
  public static final String PARAM_CA_CERTIFICATE = "ca_certificate";
  public static final String PARAM_CLIENT_CERTIFICATE = "client_certificate";
  public static final String PARAM_CLIENT_KEY = "client_key";
  public static final String PARAM_CLIENT_KEY_PASSWORD = "client_key_password";

  /**
   * Parses SSL related configuration and generates keystores to be used by connector
   *
   * @param config configuration
   * @return map containing relevant parsed values including location of keystore or an empty map
   */
  public static Map<String, String> parseSSLConfig(final JsonNode config) {
    LOGGER.debug("source config: {}", config);

    Pair<URI, String> caCertKeyStorePair = null;
    Pair<URI, String> clientCertKeyStorePair = null;
    final Map<String, String> additionalParameters = new HashMap<>();
    // assume ssl if not explicitly mentioned.
    if (!config.has(JdbcUtils.SSL_KEY) || config.get(JdbcUtils.SSL_KEY).asBoolean()) {
      if (config.has(JdbcUtils.SSL_MODE_KEY)) {
        final String specMode = config.get(JdbcUtils.SSL_MODE_KEY).get(PARAM_MODE).asText();
        additionalParameters.put(SSL_MODE,
            SslMode.bySpec(specMode).orElseThrow(() -> new IllegalArgumentException("unexpected ssl mode")).name());
        if (Objects.isNull(caCertKeyStorePair)) {
          caCertKeyStorePair = JdbcSSLConnectionUtils.prepareCACertificateKeyStore(config);
        }

        if (Objects.nonNull(caCertKeyStorePair)) {
          LOGGER.debug("uri for ca cert keystore: {}", caCertKeyStorePair.getLeft().toString());
          try {
            additionalParameters.putAll(Map.of(
                TRUST_KEY_STORE_URL, caCertKeyStorePair.getLeft().toURL().toString(),
                TRUST_KEY_STORE_PASS, caCertKeyStorePair.getRight(),
                TRUST_KEY_STORE_TYPE, KEY_STORE_TYPE_PKCS12));
          } catch (final MalformedURLException e) {
            throw new RuntimeException("Unable to get a URL for trust key store");
          }

        }

        if (Objects.isNull(clientCertKeyStorePair)) {
          clientCertKeyStorePair = JdbcSSLConnectionUtils.prepareClientCertificateKeyStore(config);
        }

        if (Objects.nonNull(clientCertKeyStorePair)) {
          LOGGER.debug("uri for client cert keystore: {} / {}", clientCertKeyStorePair.getLeft().toString(), clientCertKeyStorePair.getRight());
          try {
            additionalParameters.putAll(Map.of(
                CLIENT_KEY_STORE_URL, clientCertKeyStorePair.getLeft().toURL().toString(),
                CLIENT_KEY_STORE_PASS, clientCertKeyStorePair.getRight(),
                CLIENT_KEY_STORE_TYPE, KEY_STORE_TYPE_PKCS12));
          } catch (final MalformedURLException e) {
            throw new RuntimeException("Unable to get a URL for client key store");
          }
        }
      } else {
        additionalParameters.put(SSL_MODE, SslMode.DISABLED.name());
      }
    }
    LOGGER.debug("additional params: {}", additionalParameters);
    return additionalParameters;
  }

  public static Pair<URI, String> prepareCACertificateKeyStore(final JsonNode config) {
    // if config available
    // if has CA cert - make keystore
    // if has client cert
    // if has client password - make keystore using password
    // if no client password - make keystore using random password
    Pair<URI, String> caCertKeyStorePair = null;
    if (Objects.nonNull(config)) {
      if (!config.has(JdbcUtils.SSL_KEY) || config.get(JdbcUtils.SSL_KEY).asBoolean()) {
        final var encryption = config.get(JdbcUtils.SSL_MODE_KEY);
        if (encryption.has(PARAM_CA_CERTIFICATE) && !encryption.get(PARAM_CA_CERTIFICATE).asText().isEmpty()) {
          final String clientKeyPassword = getOrGeneratePassword(encryption);
          try {
            final URI caCertKeyStoreUri = SSLCertificateUtils.keyStoreFromCertificate(
                encryption.get(PARAM_CA_CERTIFICATE).asText(),
                clientKeyPassword,
                null,
                null);
            caCertKeyStorePair = new ImmutablePair<>(caCertKeyStoreUri, clientKeyPassword);
          } catch (final CertificateException | IOException | KeyStoreException | NoSuchAlgorithmException e) {
            throw new RuntimeException("Failed to create keystore for CA certificate", e);
          }
        }
      }
    }
    return caCertKeyStorePair;
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

  public static Pair<URI, String> prepareClientCertificateKeyStore(final JsonNode config) {
    Pair<URI, String> clientCertKeyStorePair = null;
    if (Objects.nonNull(config)) {
      if (!config.has(JdbcUtils.SSL_KEY) || config.get(JdbcUtils.SSL_KEY).asBoolean()) {
        final var encryption = config.get(JdbcUtils.SSL_MODE_KEY);
        if (encryption.has(PARAM_CLIENT_CERTIFICATE) && !encryption.get(PARAM_CLIENT_CERTIFICATE).asText().isEmpty()
            && encryption.has(PARAM_CLIENT_KEY) && !encryption.get(PARAM_CLIENT_KEY).asText().isEmpty()) {
          final String clientKeyPassword = getOrGeneratePassword(encryption);
          try {
            final URI clientCertKeyStoreUri = SSLCertificateUtils.keyStoreFromClientCertificate(encryption.get(PARAM_CLIENT_CERTIFICATE).asText(),
                encryption.get(PARAM_CLIENT_KEY).asText(),
                clientKeyPassword, null);
            clientCertKeyStorePair = new ImmutablePair<>(clientCertKeyStoreUri, clientKeyPassword);
          } catch (final CertificateException | IOException
              | KeyStoreException | NoSuchAlgorithmException
              | InvalidKeySpecException | InterruptedException e) {
            throw new RuntimeException("Failed to create keystore for Client certificate", e);
          }
        }
      }
    }
    return clientCertKeyStorePair;
  }

  public static Path fileFromCertPem(final String certPem) {
    try {
      final Path path = Files.createTempFile(null, ".crt");
      Files.writeString(path, certPem);
      path.toFile().deleteOnExit();
      return path;
    } catch (final IOException e) {
      throw new RuntimeException("Cannot save root certificate to file", e);
    }
  }

}
