/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.util.SSLCertificateUtils;
import java.io.IOException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.CertificateException;
import java.security.spec.InvalidKeySpecException;
import java.util.Objects;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JdbcSSLConnectionUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(JdbcSSLConnectionUtils.class.getClass());
  public static final String PARAM_CA_CERTIFICATE = "ca_certificate";
  public static final String PARAM_CLIENT_CERTIFICATE = "client_certificate";
  public static final String PARAM_CLIENT_KEY = "client_key";
  public static final String PARAM_CLIENT_KEY_PASSWORD = "client_key_password";

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
