/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.google.common.annotations.VisibleForTesting;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import java.io.OutputStream;
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;
import java.util.Base64.Encoder;
import java.util.Map;
import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.CipherOutputStream;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.KeyGenerator;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.SecretKey;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/**
 * This class implements the envelope encryption that Redshift and Snowflake use when loading
 * encrypted files from S3 (or other blob stores):
 * <ul>
 * <li>A content-encrypting-key (CEK) is used to encrypt the actual data (i.e. the CSV file)</li>
 * <li>A key-encrypting-key (KEK) is used to encrypt the CEK</li>
 * <li>The encrypted CEK is stored in the S3 object metadata, along with the plaintext
 * initialization vector</li>
 * <li>The COPY command includes the KEK (in plaintext). Redshift/Snowflake will use it to decrypt
 * the CEK, which it then uses to decrypt the CSV file.</li>
 * </ul>
 * <p>
 * A new CEK is generated for each S3 object, but each sync uses a single KEK. The KEK may be either
 * user-provided (if the user wants to keep the data for further use), or generated per-sync (if
 * they simply want to add additional security around their COPY operation).
 * <p>
 * Redshift does not support loading directly from GCS or Azure Blob Storage.
 * <p>
 * Snowflake only supports client-side encryption in S3 and Azure Storage; it does not support this
 * feature in GCS (https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html). Azure
 * Storage uses a similar envelope encryption technique to S3
 * (https://docs.microsoft.com/en-us/azure/storage/common/storage-client-side-encryption?tabs=dotnet#encryption-via-the-envelope-technique).
 */
public class AesCbcEnvelopeEncryptionBlobDecorator implements BlobDecorator {

  public static final String ENCRYPTED_CONTENT_ENCRYPTING_KEY = "aes_cbc_envelope_encryption-content-encrypting-key";
  public static final String INITIALIZATION_VECTOR = "aes_cbc_envelope_encryption-initialization-vector";

  public static final int AES_KEY_SIZE_BITS = 256;
  private static final int AES_CBC_INITIALIZATION_VECTOR_SIZE_BYTES = 16;
  private static final Encoder BASE64_ENCODER = Base64.getEncoder();
  private static final SecureRandom SECURE_RANDOM = new SecureRandom();

  public static final String KEY_ENCRYPTING_ALGO = "AES";

  // There's no specific KeyGenerator for AES/CBC/PKCS5Padding, so we just use a normal AES
  // KeyGenerator
  private static final String CONTENT_ENCRYPTING_KEY_ALGO = "AES";
  // Redshift's UNLOAD command uses this cipher mode, so we'll use it here as well.
  // TODO If we eventually want to expose client-side encryption in destination-s3, we should probably
  // also implement
  // AES-GCM, since it's mostly superior to CBC mode. (if we do that: make sure that the output is
  // compatible with
  // aws-java-sdk's AmazonS3EncryptionV2Client, which requires a slightly different set of metadata)
  private static final String CONTENT_ENCRYPTING_CIPHER_ALGO = "AES/CBC/PKCS5Padding";

  // The real "secret key". Should be handled with great care.
  private final SecretKey keyEncryptingKey;
  // A random key generated for each file. Also should be handled with care.
  private final SecretKey contentEncryptingKey;
  // Arbitrary bytes required by the CBC algorithm. Not a sensitive value.
  // The only requirement is that we never reuse an (IV, CEK) pair.
  private final byte[] initializationVector;

  public AesCbcEnvelopeEncryptionBlobDecorator(final SecretKey keyEncryptingKey) {
    this(keyEncryptingKey, randomContentEncryptingKey(), randomInitializationVector());
  }

  public AesCbcEnvelopeEncryptionBlobDecorator(final byte[] keyEncryptingKey) {
    this(new SecretKeySpec(keyEncryptingKey, KEY_ENCRYPTING_ALGO));
  }

  @VisibleForTesting
  AesCbcEnvelopeEncryptionBlobDecorator(final SecretKey keyEncryptingKey, final SecretKey contentEncryptingKey, final byte[] initializationVector) {
    this.keyEncryptingKey = keyEncryptingKey;
    this.contentEncryptingKey = contentEncryptingKey;

    this.initializationVector = initializationVector;
  }

  @SuppressFBWarnings(
                      value = {"PADORA", "CIPINT"},
                      justification = "We're using this cipher for compatibility with Redshift/Snowflake.")
  @Override
  public OutputStream wrap(final OutputStream stream) {
    try {
      final Cipher dataCipher = Cipher.getInstance(CONTENT_ENCRYPTING_CIPHER_ALGO);
      dataCipher.init(Cipher.ENCRYPT_MODE, contentEncryptingKey, new IvParameterSpec(initializationVector));
      return new CipherOutputStream(stream, dataCipher);
    } catch (final InvalidAlgorithmParameterException | NoSuchPaddingException | NoSuchAlgorithmException | InvalidKeyException e) {
      throw new RuntimeException(e);
    }
  }

  @SuppressFBWarnings(
                      value = {"CIPINT", "SECECB"},
                      justification = "We're using this cipher for compatibility with Redshift/Snowflake.")
  @Override
  public void updateMetadata(final Map<String, String> metadata, final Map<String, String> metadataKeyMapping) {
    try {
      final Cipher keyCipher = Cipher.getInstance(KEY_ENCRYPTING_ALGO);
      keyCipher.init(Cipher.ENCRYPT_MODE, keyEncryptingKey);
      final byte[] encryptedCekBytes = keyCipher.doFinal(contentEncryptingKey.getEncoded());

      BlobDecorator.insertMetadata(metadata, metadataKeyMapping, ENCRYPTED_CONTENT_ENCRYPTING_KEY, BASE64_ENCODER.encodeToString(encryptedCekBytes));
      BlobDecorator.insertMetadata(metadata, metadataKeyMapping, INITIALIZATION_VECTOR, BASE64_ENCODER.encodeToString(initializationVector));
    } catch (final NoSuchPaddingException | NoSuchAlgorithmException | InvalidKeyException | IllegalBlockSizeException | BadPaddingException e) {
      throw new RuntimeException(e);
    }
  }

  private static SecretKey randomContentEncryptingKey() {
    try {
      final KeyGenerator cekGenerator = KeyGenerator.getInstance(CONTENT_ENCRYPTING_KEY_ALGO);
      cekGenerator.init(AES_KEY_SIZE_BITS);
      return cekGenerator.generateKey();
    } catch (final NoSuchAlgorithmException e) {
      throw new RuntimeException(e);
    }
  }

  private static byte[] randomInitializationVector() {
    final byte[] initializationVector = new byte[AES_CBC_INITIALIZATION_VECTOR_SIZE_BYTES];
    SECURE_RANDOM.nextBytes(initializationVector);
    return initializationVector;
  }

}
