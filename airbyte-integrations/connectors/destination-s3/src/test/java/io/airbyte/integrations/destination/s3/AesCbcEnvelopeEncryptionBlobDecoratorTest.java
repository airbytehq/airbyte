package io.airbyte.integrations.destination.s3;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.Charset;
import java.util.Base64;
import java.util.Base64.Decoder;
import java.util.Base64.Encoder;
import java.util.HashMap;
import java.util.Map;
import javax.crypto.spec.SecretKeySpec;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AesCbcEnvelopeEncryptionBlobDecoratorTest {

  private static final Encoder BASE64_ENCODER = Base64.getEncoder();
  private static final Decoder BASE64_DECODER = Base64.getDecoder();

  private AesCbcEnvelopeEncryptionBlobDecorator decorator;

  @BeforeEach
  public void setup() {
    decorator = new AesCbcEnvelopeEncryptionBlobDecorator(
        new SecretKeySpec(BASE64_DECODER.decode("oFf0LY0Zae9ksNZsPSJG8ZLGRRBUUhitaPKWRPPKTvM="), "AES"),
        new SecretKeySpec(BASE64_DECODER.decode("9ZAVuZE8L4hJCFQS49OMNeFRGTCBUHAFOgkW3iZkOq8="), "AES"),
        BASE64_DECODER.decode("04YDvMCXpvTb2ilggLbDJQ==")
    );
  }

  private static final Logger LOGGER = LoggerFactory.getLogger(AesCbcEnvelopeEncryptionBlobDecoratorTest.class);
  @Test
  public void testEncryption() throws IOException {
    final ByteArrayOutputStream stream = new ByteArrayOutputStream();

    try (final OutputStream wrapped = decorator.wrap(stream)) {
      IOUtils.write(
          """
              adc66b6e-6051-42db-b683-d978a51c3c02,"{""campaign.resource_name"":""cus""}",2022-04-04 22:32:50.046
              0e253b28-bec6-4a90-8622-629d3e542982,"{""campaign.resource_name"":""cus""}",2022-04-04 22:32:50.047
              """,
          wrapped,
          Charset.defaultCharset()
      );
    }
    LOGGER.info(BASE64_ENCODER.encodeToString(stream.toByteArray()));


    Assertions.assertArrayEquals(
        BASE64_DECODER.decode("IRfz0FN05Y9yyne+0V+G14xYjA4B0+ter7qniDheIu9UM3Fdmu/mqjyFvYFIRTroP5kNJ1SH3FaArE5aHkrWMPwSkczkhArajfYX+UEfGH68YyWOSnpdxuviTTgK3Ee3OVTz3ZlziOB8jCMjupJ9pqkLnxg7Ghe3BQ1puOHGFDMmIgiP4Zfz0fkdlUyZOvsJ7xpncD24G6IIJNwOyo4CedULgueHdybmxr4oddhAja8QxJxZzlfZl4suJ+KWvt78MSdkRlp+Ip99U8n0O7BLJA=="),
        stream.toByteArray()
    );
  }

  @Test
  public void testMetadataInsertion() {
    final Map<String, String> metadata = new HashMap<>();

    decorator.updateMetadata(
        metadata,
        Map.of(
            AesCbcEnvelopeEncryptionBlobDecorator.ENCRYPTED_CONTENT_ENCRYPTING_KEY, "the_cek",
            AesCbcEnvelopeEncryptionBlobDecorator.INITIALIZATION_VECTOR, "the_iv"
        )
    );

    Assertions.assertEquals(
        Map.of(
            "the_cek", "Ck5u5cKqcY+bcFBrpsPHHUNw5Qx8nYDJ2Vqt6XG6kwxjVAJQKKljPv9NDsG6Ncoc",
            "the_iv", "04YDvMCXpvTb2ilggLbDJQ=="
        ),
        metadata
    );
  }
}
