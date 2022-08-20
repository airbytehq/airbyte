/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.util.SSLCertificateUtils;
import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.nio.file.FileSystem;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.Key;
import java.security.KeyStore;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
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

  public static URI prepareCACertificateKeyStore(final JsonNode config, final FileSystem fileSystem) {
    // if config available
    // if has CA cert - make keystore
    // if has client cert
    //   if has client password - make keystore using password
    //   if no client password -  make keystore using random password
    URI caCertKeyStoreUri = null;
    if (Objects.nonNull(config)) {
      if (!config.has(JdbcUtils.SSL_KEY) || config.get(JdbcUtils.SSL_KEY).asBoolean()) {
        final var encryption = config.get(JdbcUtils.SSL_MODE_KEY);
        if (encryption.has(PARAM_CA_CERTIFICATE) && !encryption.get(PARAM_CA_CERTIFICATE).asText().isEmpty()) {
          try {
            caCertKeyStoreUri = SSLCertificateUtils.keyStoreFromCertificate(
                encryption.get(PARAM_CA_CERTIFICATE).asText(),
                "",
                fileSystem,
                null);
          } catch (final CertificateException | IOException | KeyStoreException | NoSuchAlgorithmException e) {
            throw new RuntimeException("Failed to create keystore for CA certificate", e);
          }
        }
      }
    }
    return caCertKeyStoreUri;
  }

  public static Pair<URI, String> prepareClientCertificateKeyStore(final JsonNode config, final FileSystem fileSystem) {
    Pair<URI, String> clientCertKeyStorePair = null;
    if (Objects.nonNull(config)) {
      if (!config.has(JdbcUtils.SSL_KEY) || config.get(JdbcUtils.SSL_KEY).asBoolean()) {
        final var encryption = config.get(JdbcUtils.SSL_MODE_KEY);
        if (encryption.has(PARAM_CLIENT_CERTIFICATE) && !encryption.get(PARAM_CLIENT_CERTIFICATE).asText().isEmpty()
        && encryption.has(PARAM_CLIENT_KEY) && !encryption.get(PARAM_CLIENT_KEY).asText().isEmpty()) {
          final String clientKeyPassword;
          if (encryption.has(PARAM_CLIENT_KEY_PASSWORD) && !encryption.get(PARAM_CLIENT_KEY_PASSWORD).asText().isEmpty()) {
            clientKeyPassword = encryption.get(PARAM_CLIENT_KEY_PASSWORD).asText();
          } else {
            clientKeyPassword = RandomStringUtils.randomAlphanumeric(10);
          }
          try {
            final URI clientCertKeyStoreUri = SSLCertificateUtils.keyStoreFromClientCertificate(encryption.get(PARAM_CLIENT_CERTIFICATE).asText(),
                encryption.get(PARAM_CLIENT_KEY).asText(),
                clientKeyPassword,
                fileSystem, null);

//            //////TEMP: verify
//            final KeyStore ks = KeyStore.getInstance("PKCS12");
//            final InputStream inputStream = Files.newInputStream(Path.of(clientCertKeyStoreUri));
//            ks.load(inputStream, clientKeyPassword.toCharArray());
//            LOGGER.info("size: {}", ks.size());
//            LOGGER.info("aliases: {}", ks.aliases().nextElement());
//            try {
//              final Key k = ks.getKey("ab_", clientKeyPassword.toCharArray());
//            } catch (final Exception ex) {
//              LOGGER.info("can't get key");
//            }

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
}
