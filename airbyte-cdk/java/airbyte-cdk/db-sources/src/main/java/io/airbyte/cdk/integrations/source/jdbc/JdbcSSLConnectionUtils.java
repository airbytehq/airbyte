/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.util.SSLCertificateUtils;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URI;
import java.net.URL;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.CertificateException;
import java.security.spec.InvalidKeySpecException;
import java.util.Arrays;
import java.util.Collections;
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

  public static record KeyStoreInfo (URL url, String password, String type) {}

  public static record SSLConfig(SslMode sslMode, KeyStoreInfo clientKeyStoreInfo, KeyStoreInfo caKeyStoreInfo) {
    SSLConfig(SslMode sslMode) {
      this(sslMode, null, null);
    }
  }

  public static Map<String, String> asParameterMap(SSLConfig sslConfig) {
    Map<String, String> retVal = new HashMap<>();
    if (sslConfig != null) {
      retVal.put(SSL_MODE, sslConfig.sslMode.name());
      if (sslConfig.clientKeyStoreInfo != null) {
        retVal.putAll(Map.of(
            CLIENT_KEY_STORE_URL, sslConfig.clientKeyStoreInfo.url.toString(),
            CLIENT_KEY_STORE_PASS, sslConfig.clientKeyStoreInfo.password,
            CLIENT_KEY_STORE_TYPE, sslConfig.clientKeyStoreInfo.type));
      }
      if (sslConfig.caKeyStoreInfo != null) {
        retVal.putAll(Map.of(
            TRUST_KEY_STORE_URL,sslConfig.caKeyStoreInfo.url.toString(),
            TRUST_KEY_STORE_PASS,sslConfig.caKeyStoreInfo.password,
            TRUST_KEY_STORE_TYPE,sslConfig.caKeyStoreInfo.type));
      }
    }
    return retVal;
  }

  /**
   * Parses SSL related configuration and generates keystores to be used by connector
   *
   * @param config configuration as a JSonNode
   * @return object containing relevant parsed values including location of keystore or an empty map
   */
  public static SSLConfig parseSSLConfig(final JsonNode config) {
    LOGGER.debug("source config: {}", config);
    if(config.has(JdbcUtils.SSL_KEY) && config.get(JdbcUtils.SSL_KEY).asBoolean() == Boolean.FALSE) {
      return null;
    }
    if (!config.has(JdbcUtils.SSL_MODE_KEY)) {
      return new SSLConfig(SslMode.DISABLED);
    }

    final String specMode = config.get(JdbcUtils.SSL_MODE_KEY).get(PARAM_MODE).asText();
    SslMode sslMode = SslMode.bySpec(specMode).orElseThrow(() -> new IllegalArgumentException("unexpected ssl mode"));

    KeyStoreInfo caCertKeyStorePair = JdbcSSLConnectionUtils.prepareCACertificateKeyStore(config);
    KeyStoreInfo clientCertKeyStorePair = JdbcSSLConnectionUtils.prepareClientCertificateKeyStore(config);
    if (Objects.nonNull(caCertKeyStorePair)) {
      LOGGER.debug("url for ca cert keystore: {}", caCertKeyStorePair.url.toString());
    }
    if (Objects.nonNull(clientCertKeyStorePair)) {
      LOGGER.debug("url for client cert keystore: {} / {}", clientCertKeyStorePair.url.toString(), clientCertKeyStorePair.password);
    }
    return new SSLConfig(sslMode, clientCertKeyStorePair, caCertKeyStorePair);
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
        return new KeyStoreInfo(caCertKeyStoreUri.toURL(), clientKeyPassword, KEY_STORE_TYPE_PKCS12);
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
        return new KeyStoreInfo(clientCertKeyStoreUri.toURL(), clientKeyPassword, KEY_STORE_TYPE_PKCS12);
      } catch (final CertificateException | IOException
          | KeyStoreException | NoSuchAlgorithmException
          | InvalidKeySpecException | InterruptedException e) {
        throw new RuntimeException("Failed to create keystore for Client certificate", e);
      }
    }
    return null;
  }
}
