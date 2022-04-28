package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import java.security.NoSuchAlgorithmException;
import javax.annotation.Nonnull;
import javax.crypto.KeyGenerator;

/**
 * @param key     The key to use for encryption.
 * @param keyType Where the key came from.
 */
public record AesCbcEnvelopeEncryption(@Nonnull byte[] key, @Nonnull KeyType keyType) implements EncryptionConfig {

  public enum KeyType {
    EPHEMERAL,
    USER_PROVIDED
  }

  public static AesCbcEnvelopeEncryption fromJson(final JsonNode encryptionNode) {
    final JsonNode kekNode = encryptionNode.get("key_encrypting_key");
    final String keyType = kekNode.get("key_type").asText();
    return switch (keyType) {
      case "user_provided" -> new AesCbcEnvelopeEncryption(BASE64_DECODER.decode(kekNode.get("key").asText()), KeyType.USER_PROVIDED);
      case "ephemeral" -> encryptionWithRandomKey();
      default -> throw new IllegalArgumentException("Invalid key type: " + keyType);
    };
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
}
