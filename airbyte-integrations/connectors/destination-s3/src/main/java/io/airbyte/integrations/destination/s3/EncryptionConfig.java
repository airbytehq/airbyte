/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Base64;
import java.util.Base64.Decoder;

public sealed interface EncryptionConfig permits AesCbcEnvelopeEncryption,NoEncryption {

  Decoder BASE64_DECODER = Base64.getDecoder();

  static EncryptionConfig fromJson(final JsonNode encryptionNode) {
    // For backwards-compatibility. Preexisting configs which don't contain the "encryption" key will
    // pass a null JsonNode into this method.
    if (encryptionNode == null) {
      return new NoEncryption();
    }

    final String encryptionType = encryptionNode.get("encryption_type").asText();
    return switch (encryptionType) {
      case "none" -> new NoEncryption();
      case "aes_cbc_envelope" -> AesCbcEnvelopeEncryption.fromJson(encryptionNode);
      default -> throw new IllegalArgumentException("Invalid encryption type: " + encryptionType);
    };
  }

}
