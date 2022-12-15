/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Base64.Decoder;
import java.util.HashMap;
import java.util.Map;
import javax.crypto.spec.SecretKeySpec;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class AesCbcEnvelopeEncryptionBlobDecoratorTest {

  private static final Decoder BASE64_DECODER = Base64.getDecoder();
  // A random base64-encoded 256-bit AES key
  public static final String KEY_ENCRYPTING_KEY = "oFf0LY0Zae9ksNZsPSJG8ZLGRRBUUhitaPKWRPPKTvM=";
  // Another base64-encoded random 256-bit AES key
  public static final String CONTENT_ENCRYPTING_KEY = "9ZAVuZE8L4hJCFQS49OMNeFRGTCBUHAFOgkW3iZkOq8=";
  // A random base64-encoded 16-byte array
  public static final String INITIALIZATION_VECTOR = "04YDvMCXpvTb2ilggLbDJQ==";
  // A small CSV file, which looks similar to what destination-s3 might upload
  public static final String PLAINTEXT = """
                                         adc66b6e-6051-42db-b683-d978a51c3c02,"{""campaign.resource_name"":""cus""}",2022-04-04 22:32:50.046
                                         0e253b28-bec6-4a90-8622-629d3e542982,"{""campaign.resource_name"":""cus""}",2022-04-04 22:32:50.047
                                         """;
  // The encryption of the plaintext, using the CEK and IV defined above (base64-encoded). Equivalent
  // to:
  // base64Encode(encrypt("AES-CBC", PLAINTEXT, CONTENT_ENCRYPTING_KEY, INITIALIZATION_VECTOR)
  public static final String CIPHERTEXT =
      "IRfz0FN05Y9yyne+0V+G14xYjA4B0+ter7qniDheIu9UM3Fdmu/mqjyFvYFIRTroP5kNJ1SH3FaArE5aHkrWMPwSkczkhArajfYX+UEfGH68YyWOSnpdxuviTTgK3Ee3OVTz3ZlziOB8jCMjupJ9pqkLnxg7Ghe3BQ1puOHGFDMmIgiP4Zfz0fkdlUyZOvsJ7xpncD24G6IIJNwOyo4CedULgueHdybmxr4oddhAja8QxJxZzlfZl4suJ+KWvt78MSdkRlp+Ip99U8n0O7BLJA==";
  // The encryption of the CEK, using the KEK defined above (base64-encoded). Equivalent to:
  // base64Encode(encrypt("AES-ECB", CONTENT_ENCRYPTING_KEY, KEY_ENCRYPTING_KEY)
  public static final String ENCRYPTED_CEK = "Ck5u5cKqcY+bcFBrpsPHHUNw5Qx8nYDJ2Vqt6XG6kwxjVAJQKKljPv9NDsG6Ncoc";

  private AesCbcEnvelopeEncryptionBlobDecorator decorator;

  @BeforeEach
  public void setup() {
    decorator = new AesCbcEnvelopeEncryptionBlobDecorator(
        new SecretKeySpec(BASE64_DECODER.decode(KEY_ENCRYPTING_KEY), "AES"),
        new SecretKeySpec(BASE64_DECODER.decode(CONTENT_ENCRYPTING_KEY), "AES"),
        BASE64_DECODER.decode(INITIALIZATION_VECTOR));
  }

  @Test
  public void testEncryption() throws IOException {
    final ByteArrayOutputStream stream = new ByteArrayOutputStream();

    try (final OutputStream wrapped = decorator.wrap(stream)) {
      IOUtils.write(
          PLAINTEXT,
          wrapped,
          StandardCharsets.UTF_8);
    }

    Assertions.assertArrayEquals(
        BASE64_DECODER.decode(CIPHERTEXT),
        stream.toByteArray());
  }

  @Test
  public void testMetadataInsertion() {
    final Map<String, String> metadata = new HashMap<>();

    decorator.updateMetadata(
        metadata,
        Map.of(
            AesCbcEnvelopeEncryptionBlobDecorator.ENCRYPTED_CONTENT_ENCRYPTING_KEY, "the_cek",
            AesCbcEnvelopeEncryptionBlobDecorator.INITIALIZATION_VECTOR, "the_iv"));

    Assertions.assertEquals(
        Map.of(
            "the_cek", ENCRYPTED_CEK,
            "the_iv", INITIALIZATION_VECTOR),
        metadata);
  }

}
