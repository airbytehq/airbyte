/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import java.util.*

interface EncryptionConfig {
    companion object {
        @JvmStatic
        fun fromJson(encryptionNode: JsonNode?): EncryptionConfig {
            // For backwards-compatibility. Preexisting configs which don't contain the "encryption"
            // key will
            // pass a null JsonNode into this method.
            if (encryptionNode == null) {
                return NoEncryption()
            }

            return when (val encryptionType = encryptionNode["encryption_type"].asText()) {
                "none" -> NoEncryption()
                "aes_cbc_envelope" -> AesCbcEnvelopeEncryption.Companion.fromJson(encryptionNode)
                else -> throw IllegalArgumentException("Invalid encryption type: $encryptionType")
            }
        }

        val BASE64_DECODER: Base64.Decoder = Base64.getDecoder()
    }
}
