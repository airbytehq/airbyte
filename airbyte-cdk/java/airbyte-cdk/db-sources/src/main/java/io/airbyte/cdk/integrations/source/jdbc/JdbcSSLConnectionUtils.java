/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.util.SSLCertificateUtils;
import java.io.IOException;
import java.net.URI;
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
import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JdbcSSLConnectionUtils {


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

    private static Optional<SslMode> bySpec(final String spec) {
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

  public enum ConfigKeys {
    SSL_MODE("ssl_mode"),
    TRUST_KEY_STORE_URI("trustCertificateKeyStoreUri"),
    TRUST_KEY_STORE_PASS("trustCertificateKeyStorePassword"),
    TRUST_KEY_STORE_TYPE("trustCertificateKeyStoreType"),

    CLIENT_KEY_STORE_URI("clientCertificateKeyStoreUri"),
    CLIENT_KEY_STORE_PASS("clientCertificateKeyStorePassword"),
    CLIENT_KEY_STORE_TYPE("clientCertificateKeyStoreType"),

    CA_CERTIFICATE_PATH("ca_certificate_path"),
    ;
    ConfigKeys(String val) {

    }
  }

  public static record KeyStoreInfo (URI uri, String password, String type) {}

  public static record SSLConfig(SslMode sslMode, KeyStoreInfo clientKeyStoreInfo, KeyStoreInfo caKeyStoreInfo) {
    SSLConfig(SslMode sslMode) {
      this(sslMode, null, null);
    }
  }

  /**
   * Parses SSL related configuration and generates keystores to be used by connector
   *
   * @param config configuration
   * @return map containing relevant parsed values including location of keystore or an empty map
   */
  @Deprecated
  public static Map<ConfigKeys, String> parseSSLConfig(final JsonNode config) {
    LOGGER.debug("source config: {}", config);

    final Map<ConfigKeys, String> additionalParameters = new HashMap<>();
    // assume ssl if not explicitly mentioned.
    if (!config.has(JdbcUtils.SSL_KEY) || config.get(JdbcUtils.SSL_KEY).asBoolean()) {
      if (config.has(JdbcUtils.SSL_MODE_KEY)) {
        final String specMode = config.get(JdbcUtils.SSL_MODE_KEY).get(PARAM_MODE).asText();
        additionalParameters.put(ConfigKeys.SSL_MODE,
            SslMode.bySpec(specMode).orElseThrow(() -> new IllegalArgumentException("unexpected ssl mode")).name());

        KeyStoreInfo caCertKeyStorePair = JdbcSSLConnectionUtils.prepareCACertificateKeyStore(config);
        if (Objects.nonNull(caCertKeyStorePair)) {
          LOGGER.debug("uri for ca cert keystore: {}", caCertKeyStorePair.uri().toString());

          additionalParameters.putAll(Map.of(
              ConfigKeys.TRUST_KEY_STORE_URI, caCertKeyStorePair.uri.toString(),
              ConfigKeys.TRUST_KEY_STORE_PASS, caCertKeyStorePair.password,
              ConfigKeys.TRUST_KEY_STORE_TYPE, caCertKeyStorePair.type));

        }

        KeyStoreInfo clientCertKeyStorePair = JdbcSSLConnectionUtils.prepareClientCertificateKeyStore(config);
        if (Objects.nonNull(clientCertKeyStorePair)) {
          LOGGER.debug("uri for client cert keystore: {} / {}", clientCertKeyStorePair.uri, clientCertKeyStorePair.password);
          additionalParameters.putAll(Map.of(
              ConfigKeys.CLIENT_KEY_STORE_URI, clientCertKeyStorePair.uri.toString(),
              ConfigKeys.CLIENT_KEY_STORE_PASS, clientCertKeyStorePair.password,
              ConfigKeys.CLIENT_KEY_STORE_TYPE, clientCertKeyStorePair.type));
        }
      } else {
        additionalParameters.put(ConfigKeys.SSL_MODE, SslMode.DISABLED.name());
      }
    }
    LOGGER.debug("additional params: {}", additionalParameters);
    return additionalParameters;
  }

  private static @Nullable KeyStoreInfo prepareCACertificateKeyStore(final JsonNode sslConfigAsJson) {
    // if has CA cert - make keystore
    // if has client cert
    // if has client password - make keystore using password
    // if no client password - make keystore using random password

    if (sslConfigAsJson.has(PARAM_CA_CERTIFICATE) && !sslConfigAsJson.get(PARAM_CA_CERTIFICATE).asText().isEmpty()) {
      final String clientKeyPassword = getOrGeneratePassword(sslConfigAsJson);
      try {
        final URI caCertKeyStoreUri = SSLCertificateUtils.keyStoreFromCertificate(
            sslConfigAsJson.get(PARAM_CA_CERTIFICATE).asText(),
            clientKeyPassword,
            null,
            null);
        return new KeyStoreInfo(caCertKeyStoreUri, clientKeyPassword, KEY_STORE_TYPE_PKCS12);
      } catch (final CertificateException | IOException | KeyStoreException | NoSuchAlgorithmException e) {
        throw new RuntimeException("Failed to create keystore for CA certificate", e);
      }
    } else {
      return null;
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

  private static @Nullable KeyStoreInfo prepareClientCertificateKeyStore(final @Nonnull JsonNode sslConfigAsJson) {
    Pair<URI, String> clientCertKeyStorePair = null;
    if (sslConfigAsJson.has(PARAM_CLIENT_CERTIFICATE) && !sslConfigAsJson.get(PARAM_CLIENT_CERTIFICATE).asText().isEmpty()
        && sslConfigAsJson.has(PARAM_CLIENT_KEY) && !sslConfigAsJson.get(PARAM_CLIENT_KEY).asText().isEmpty()) {
      final String clientKeyPassword = getOrGeneratePassword(sslConfigAsJson);
      try {
        final URI clientCertKeyStoreUri = SSLCertificateUtils.keyStoreFromClientCertificate(sslConfigAsJson.get(PARAM_CLIENT_CERTIFICATE).asText(),
            sslConfigAsJson.get(PARAM_CLIENT_KEY).asText(),
            clientKeyPassword, null);
        return new KeyStoreInfo(clientCertKeyStoreUri, clientKeyPassword, KEY_STORE_TYPE_PKCS12);
      } catch (final CertificateException | IOException
          | KeyStoreException | NoSuchAlgorithmException
          | InvalidKeySpecException | InterruptedException e) {
        throw new RuntimeException("Failed to create keystore for Client certificate", e);
      }
    }
    return null;
  }
}
