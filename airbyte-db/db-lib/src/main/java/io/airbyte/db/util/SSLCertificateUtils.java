/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.util;

import java.io.BufferedInputStream;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystem;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.KeyFactory;
import java.security.KeyStore;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.SecureRandom;
import java.security.cert.Certificate;
import java.security.cert.CertificateException;
import java.security.cert.CertificateFactory;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * General SSL utilities used for certificate and keystore operations related to secured db
 * connections.
 */
public class SSLCertificateUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(SSLCertificateUtils.class);
  private static final String PKCS_12 = "PKCS12";
  private static final String X509 = "X.509";
  public static final String KEYSTORE_ENTRY_PREFIX = "ab_";
  public static final String KEYSTORE_FILE_NAME = KEYSTORE_ENTRY_PREFIX + "keystore_";
  public static final String KEYSTORE_FILE_TYPE = ".p12";

  private static URI saveKeyStoreToFile(final KeyStore keyStore, final String keyStorePassword, final FileSystem filesystem, final String directory)
      throws IOException, CertificateException, KeyStoreException, NoSuchAlgorithmException {
    final FileSystem fs = Objects.requireNonNullElse(filesystem, FileSystems.getDefault());
    final Path pathToStore = fs.getPath(Objects.toString(directory, ""));
    final Path pathToFile = pathToStore.resolve(KEYSTORE_FILE_NAME + SecureRandom.getInstanceStrong().nextInt() + KEYSTORE_FILE_TYPE);
    final OutputStream os = Files.newOutputStream(pathToFile);
    keyStore.store(os, keyStorePassword.toCharArray());
    assert (Files.exists(pathToFile) == true);

    return pathToFile.toUri();
  }

  private static void runProcess(final String cmd, final Runtime run) throws IOException, InterruptedException {
    LOGGER.debug("running [{}]", cmd);
    final Process p = run.exec(cmd);
    if (!p.waitFor(30, TimeUnit.SECONDS)) {
      p.destroy();
      throw new RuntimeException("Timeout while executing: " + cmd);
    }
  }

  private static Certificate fromPEMString(final String certString) throws CertificateException {
    final CertificateFactory cf = CertificateFactory.getInstance(X509);
    final ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(certString.getBytes(StandardCharsets.UTF_8));
    final BufferedInputStream bufferedInputStream = new BufferedInputStream(byteArrayInputStream);
    return cf.generateCertificate(bufferedInputStream);
  }

  public static URI keyStoreFromCertificate(final Certificate cert,
                                            final String keyStorePassword,
                                            final FileSystem filesystem,
                                            final String directory)
      throws KeyStoreException, CertificateException, IOException, NoSuchAlgorithmException {
    final KeyStore keyStore = KeyStore.getInstance(PKCS_12);
    keyStore.load(null);
    keyStore.setCertificateEntry(KEYSTORE_ENTRY_PREFIX + "1", cert);
    return saveKeyStoreToFile(keyStore, keyStorePassword, filesystem, directory);
  }

  public static URI keyStoreFromCertificate(final String certString,
                                            final String keyStorePassword,
                                            final FileSystem filesystem,
                                            final String directory)
      throws CertificateException, IOException, KeyStoreException, NoSuchAlgorithmException {
    return keyStoreFromCertificate(fromPEMString(certString), keyStorePassword, filesystem, directory);
  }

  public static URI keyStoreFromCertificate(final String certString, final String keyStorePassword, final String directory)
      throws CertificateException, IOException, KeyStoreException, NoSuchAlgorithmException {
    return keyStoreFromCertificate(certString, keyStorePassword, FileSystems.getDefault(), directory);
  }

  public static URI keyStoreFromClientCertificate(
                                                  final Certificate cert,
                                                  final PrivateKey key,
                                                  final String keyStorePassword,
                                                  final FileSystem filesystem,
                                                  final String directory)
      throws KeyStoreException, CertificateException, IOException, NoSuchAlgorithmException {
    final KeyStore keyStore = KeyStore.getInstance(PKCS_12);
    keyStore.load(null);
    keyStore.setKeyEntry(KEYSTORE_ENTRY_PREFIX, key, keyStorePassword.toCharArray(), new Certificate[] {cert});
    return saveKeyStoreToFile(keyStore, keyStorePassword, filesystem, directory);
  }

  public static URI keyStoreFromClientCertificate(
                                                  final String certString,
                                                  final String keyString,
                                                  final String keyStorePassword,
                                                  final FileSystem filesystem,
                                                  final String directory)
      throws IOException, InterruptedException, NoSuchAlgorithmException, InvalidKeySpecException, CertificateException, KeyStoreException {

    // Convert RSA key (PKCS#1) to PKCS#8 key
    // Note: java.security doesn't have a built-in support of PKCS#1 format. A conversion using openssl
    // is necessary.
    // Since this is a single operation it's better than adding an external lib (e.g BouncyCastle)
    final Path tmpDir = Files.createTempDirectory(null);
    final Path pkcs1Key = Files.createTempFile(tmpDir, null, null);
    final Path pkcs8Key = Files.createTempFile(tmpDir, null, null);
    pkcs1Key.toFile().deleteOnExit();
    pkcs8Key.toFile().deleteOnExit();

    Files.write(pkcs1Key, keyString.getBytes(StandardCharsets.UTF_8));
    runProcess(
        "openssl pkcs8 -topk8 -inform PEM -outform DER -in " + pkcs1Key.toAbsolutePath() + " -out " + pkcs8Key.toAbsolutePath()
            + " -nocrypt -passout pass:" + keyStorePassword,
        Runtime.getRuntime());

    final PKCS8EncodedKeySpec spec = new PKCS8EncodedKeySpec(Files.readAllBytes(pkcs8Key));
    PrivateKey privateKey;
    try {
      privateKey = KeyFactory.getInstance("RSA").generatePrivate(spec);
    } catch (final InvalidKeySpecException ex1) {
      try {
        privateKey = KeyFactory.getInstance("DSA").generatePrivate(spec);
      } catch (final InvalidKeySpecException ex2) {
        privateKey = KeyFactory.getInstance("EC").generatePrivate(spec);
      }
    }

    return keyStoreFromClientCertificate(fromPEMString(certString), privateKey, keyStorePassword, filesystem, directory);

  }

  public static URI keyStoreFromClientCertificate(
                                                  final String certString,
                                                  final String keyString,
                                                  final String keyStorePassword,
                                                  final String directory)
      throws CertificateException, IOException, NoSuchAlgorithmException, InvalidKeySpecException, KeyStoreException, InterruptedException {
    return keyStoreFromClientCertificate(certString, keyString, keyStorePassword, FileSystems.getDefault(), directory);
  }

}
