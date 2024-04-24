/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3

import java.io.ByteArrayOutputStream
import java.io.IOException
import java.nio.charset.StandardCharsets
import java.util.Base64
import javax.crypto.spec.SecretKeySpec
import org.apache.commons.io.IOUtils
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class AesCbcEnvelopeEncryptionBlobDecoratorTest {

    companion object {
        private val BASE64_DECODER: Base64.Decoder = Base64.getDecoder()

        // A random base64-encoded 256-bit AES key
        const val KEY_ENCRYPTING_KEY: String = "oFf0LY0Zae9ksNZsPSJG8ZLGRRBUUhitaPKWRPPKTvM="

        // Another base64-encoded random 256-bit AES key
        const val CONTENT_ENCRYPTING_KEY: String = "9ZAVuZE8L4hJCFQS49OMNeFRGTCBUHAFOgkW3iZkOq8="

        // A random base64-encoded 16-byte array
        const val INITIALIZATION_VECTOR: String = "04YDvMCXpvTb2ilggLbDJQ=="

        // A small CSV file, which looks similar to what destination-s3 might upload
        val PLAINTEXT: String =
            """
                                             adc66b6e-6051-42db-b683-d978a51c3c02,"{""campaign.resource_name"":""cus""}",2022-04-04 22:32:50.046
                                             0e253b28-bec6-4a90-8622-629d3e542982,"{""campaign.resource_name"":""cus""}",2022-04-04 22:32:50.047
                                             
                                             """.trimIndent()

        // The encryption of the plaintext, using the CEK and IV defined above (base64-encoded).
        // Equivalent
        // to:
        // base64Encode(encrypt("AES-CBC", PLAINTEXT, CONTENT_ENCRYPTING_KEY, INITIALIZATION_VECTOR)
        const val CIPHERTEXT: String =
            "IRfz0FN05Y9yyne+0V+G14xYjA4B0+ter7qniDheIu9UM3Fdmu/mqjyFvYFIRTroP5kNJ1SH3FaArE5aHkrWMPwSkczkhArajfYX+UEfGH68YyWOSnpdxuviTTgK3Ee3OVTz3ZlziOB8jCMjupJ9pqkLnxg7Ghe3BQ1puOHGFDMmIgiP4Zfz0fkdlUyZOvsJ7xpncD24G6IIJNwOyo4CedULgueHdybmxr4oddhAja8QxJxZzlfZl4suJ+KWvt78MSdkRlp+Ip99U8n0O7BLJA=="

        // The encryption of the CEK, using the KEK defined above (base64-encoded). Equivalent to:
        // base64Encode(encrypt("AES-ECB", CONTENT_ENCRYPTING_KEY, KEY_ENCRYPTING_KEY)
        const val ENCRYPTED_CEK: String =
            "Ck5u5cKqcY+bcFBrpsPHHUNw5Qx8nYDJ2Vqt6XG6kwxjVAJQKKljPv9NDsG6Ncoc"
    }

    private lateinit var decorator: AesCbcEnvelopeEncryptionBlobDecorator

    @BeforeEach
    internal fun setup() {
        decorator =
            AesCbcEnvelopeEncryptionBlobDecorator(
                SecretKeySpec(BASE64_DECODER.decode(KEY_ENCRYPTING_KEY), "AES"),
                SecretKeySpec(BASE64_DECODER.decode(CONTENT_ENCRYPTING_KEY), "AES"),
                BASE64_DECODER.decode(INITIALIZATION_VECTOR),
            )
    }

    @Test
    @Throws(IOException::class)
    internal fun testEncryption() {
        val stream = ByteArrayOutputStream()

        decorator.wrap(stream).use { wrapped ->
            IOUtils.write(
                PLAINTEXT,
                wrapped,
                StandardCharsets.UTF_8,
            )
        }
        assertArrayEquals(
            BASE64_DECODER.decode(CIPHERTEXT),
            stream.toByteArray(),
        )
    }

    @Test
    internal fun testMetadataInsertion() {
        val metadata: MutableMap<String, String> = HashMap()

        decorator.updateMetadata(
            metadata,
            mapOf(
                AesCbcEnvelopeEncryptionBlobDecorator.ENCRYPTED_CONTENT_ENCRYPTING_KEY to "the_cek",
                AesCbcEnvelopeEncryptionBlobDecorator.INITIALIZATION_VECTOR to "the_iv",
            ),
        )

        assertEquals(
            mapOf(
                "the_cek" to ENCRYPTED_CEK,
                "the_iv" to INITIALIZATION_VECTOR,
            ),
            metadata,
        )
    }
}
