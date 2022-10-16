/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import javax.annotation.Nonnull;
import javax.crypto.KeyGenerator;
import org.apache.commons.lang3.StringUtils;

/**
 * @param key The key to use for encryption.
 * @param keyType Where the key came from.
 */
public record AesCbcEnvelopeEncryption(@Nonnull byte[] key, @Nonnull KeyType keyType) implements EncryptionConfig {

  public enum KeyType {
    EPHEMERAL,
    USER_PROVIDED
  }

  public static AesCbcEnvelopeEncryption fromJson(final JsonNode encryptionNode) {
    if (!encryptionNode.has("key_encrypting_key")) {
      return encryptionWithRandomKey();
    }
    final String kek = encryptionNode.get("key_encrypting_key").asText();
    if (StringUtils.isEmpty(kek)) {
      return encryptionWithRandomKey();
    } else {
      return new AesCbcEnvelopeEncryption(BASE64_DECODER.decode(kek), KeyType.USER_PROVIDED);
    }
  }

  private static AesCbcEnvelopeEncryption encryptionWithRandomKey() {
    try {
      final KeyGenerator kekGenerator = KeyGenerator.getInstance(AesCbcEnvelopeEncryptionBlobDecorator.KEY_ENCRYPTING_ALGO);
      kekGenerator.init(AesCbcEnvelopeEncryptionBlobDecorator.AES_KEY_SIZE_BITS);
      return new AesCbcEnvelopeEncryption(kekGenerator.generateKey().getEncoded(), KeyType.EPHEMERAL);
    } catch (final NoSuchAlgorithmException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }

    final AesCbcEnvelopeEncryption that = (AesCbcEnvelopeEncryption) o;

    if (!Arrays.equals(key, that.key)) {
      return false;
    }
    return keyType == that.keyType;
  }

  @Override
  public int hashCode() {
    int result = Arrays.hashCode(key);
    result = 31 * result + keyType.hashCode();
    return result;
  }

}
