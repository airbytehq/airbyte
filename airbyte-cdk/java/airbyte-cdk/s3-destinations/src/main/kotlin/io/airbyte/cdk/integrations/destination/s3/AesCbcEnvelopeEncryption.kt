/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import java.security.NoSuchAlgorithmException
import javax.annotation.Nonnull
import javax.crypto.KeyGenerator
import org.apache.commons.lang3.StringUtils

/**
 * @param key The key to use for encryption.
 * @param keyType Where the key came from.
 */
@JvmRecord
data class AesCbcEnvelopeEncryption(
    @field:Nonnull @param:Nonnull val key: ByteArray,
    @field:Nonnull @param:Nonnull val keyType: KeyType
) : EncryptionConfig {
    enum class KeyType {
        EPHEMERAL,
        USER_PROVIDED
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) {
            return true
        }
        if (other == null || javaClass != other.javaClass) {
            return false
        }

        val that = other as AesCbcEnvelopeEncryption

        if (!key.contentEquals(that.key)) {
            return false
        }
        return keyType == that.keyType
    }

    override fun hashCode(): Int {
        var result = key.contentHashCode()
        result = 31 * result + keyType.hashCode()
        return result
    }

    companion object {
        fun fromJson(encryptionNode: JsonNode): AesCbcEnvelopeEncryption {
            if (!encryptionNode.has("key_encrypting_key")) {
                return encryptionWithRandomKey()
            }
            val kek = encryptionNode["key_encrypting_key"].asText()
            return if (StringUtils.isEmpty(kek)) {
                encryptionWithRandomKey()
            } else {
                AesCbcEnvelopeEncryption(
                    EncryptionConfig.Companion.BASE64_DECODER.decode(kek),
                    KeyType.USER_PROVIDED
                )
            }
        }

        private fun encryptionWithRandomKey(): AesCbcEnvelopeEncryption {
            try {
                val kekGenerator =
                    KeyGenerator.getInstance(
                        AesCbcEnvelopeEncryptionBlobDecorator.KEY_ENCRYPTING_ALGO
                    )
                kekGenerator.init(AesCbcEnvelopeEncryptionBlobDecorator.AES_KEY_SIZE_BITS)
                return AesCbcEnvelopeEncryption(
                    kekGenerator.generateKey().encoded,
                    KeyType.EPHEMERAL
                )
            } catch (e: NoSuchAlgorithmException) {
                throw RuntimeException(e)
            }
        }
    }
}
