/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3

import com.google.common.annotations.VisibleForTesting
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import java.io.OutputStream
import java.security.InvalidAlgorithmParameterException
import java.security.InvalidKeyException
import java.security.NoSuchAlgorithmException
import java.security.SecureRandom
import java.util.Base64
import javax.crypto.BadPaddingException
import javax.crypto.Cipher
import javax.crypto.CipherOutputStream
import javax.crypto.IllegalBlockSizeException
import javax.crypto.KeyGenerator
import javax.crypto.NoSuchPaddingException
import javax.crypto.SecretKey
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec

/**
 * This class implements the envelope encryption that Redshift and Snowflake use when loading
 * encrypted files from S3 (or other blob stores):
 *
 * * A content-encrypting-key (CEK) is used to encrypt the actual data (i.e. the CSV file)
 * * A key-encrypting-key (KEK) is used to encrypt the CEK
 * * The encrypted CEK is stored in the S3 object metadata, along with the plaintext initialization
 * vector
 * * The COPY command includes the KEK (in plaintext). Redshift/Snowflake will use it to decrypt the
 * CEK, which it then uses to decrypt the CSV file.
 *
 * A new CEK is generated for each S3 object, but each sync uses a single KEK. The KEK may be either
 * user-provided (if the user wants to keep the data for further use), or generated per-sync (if
 * they simply want to add additional security around their COPY operation).
 *
 * Redshift does not support loading directly from GCS or Azure Blob Storage.
 *
 * Snowflake only supports client-side encryption in S3 and Azure Storage; it does not support this
 * feature in GCS (https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html). Azure
 * Storage uses a similar envelope encryption technique to S3
 * (https://docs.microsoft.com/en-us/azure/storage/common/storage-client-side-encryption?tabs=dotnet#encryption-via-the-envelope-technique).
 */
class AesCbcEnvelopeEncryptionBlobDecorator
@VisibleForTesting
internal constructor( // The real "secret key". Should be handled with great care.
    private val keyEncryptingKey:
        SecretKey?, // A random key generated for each file. Also should be handled with care.
    private val contentEncryptingKey:
        SecretKey, // Arbitrary bytes required by the CBC algorithm. Not a sensitive value.
    // The only requirement is that we never reuse an (IV, CEK) pair.
    private val initializationVector: ByteArray
) : BlobDecorator {
    constructor(
        keyEncryptingKey: SecretKey?
    ) : this(
        keyEncryptingKey,
        randomContentEncryptingKey(),
        randomInitializationVector(),
    )

    constructor(
        keyEncryptingKey: ByteArray?
    ) : this(
        SecretKeySpec(
            keyEncryptingKey,
            KEY_ENCRYPTING_ALGO,
        ),
    )

    @SuppressFBWarnings(
        value = ["PADORA", "CIPINT"],
        justification = "We're using this cipher for compatibility with Redshift/Snowflake.",
    )
    override fun wrap(stream: OutputStream): OutputStream {
        try {
            val dataCipher = Cipher.getInstance(CONTENT_ENCRYPTING_CIPHER_ALGO)
            dataCipher.init(
                Cipher.ENCRYPT_MODE,
                contentEncryptingKey,
                IvParameterSpec(
                    initializationVector,
                ),
            )
            return CipherOutputStream(stream, dataCipher)
        } catch (e: InvalidAlgorithmParameterException) {
            throw RuntimeException(e)
        } catch (e: NoSuchPaddingException) {
            throw RuntimeException(e)
        } catch (e: NoSuchAlgorithmException) {
            throw RuntimeException(e)
        } catch (e: InvalidKeyException) {
            throw RuntimeException(e)
        }
    }

    @SuppressFBWarnings(
        value = ["CIPINT", "SECECB"],
        justification = "We're using this cipher for compatibility with Redshift/Snowflake.",
    )
    override fun updateMetadata(
        metadata: MutableMap<String, String>,
        metadataKeyMapping: Map<String, String>
    ) {
        try {
            val keyCipher = Cipher.getInstance(KEY_ENCRYPTING_ALGO)
            keyCipher.init(Cipher.ENCRYPT_MODE, keyEncryptingKey)
            val encryptedCekBytes = keyCipher.doFinal(contentEncryptingKey.encoded)

            BlobDecorator.insertMetadata(
                metadata,
                metadataKeyMapping,
                ENCRYPTED_CONTENT_ENCRYPTING_KEY,
                BASE64_ENCODER.encodeToString(encryptedCekBytes),
            )
            BlobDecorator.insertMetadata(
                metadata,
                metadataKeyMapping,
                INITIALIZATION_VECTOR,
                BASE64_ENCODER.encodeToString(
                    initializationVector,
                ),
            )
        } catch (e: NoSuchPaddingException) {
            throw RuntimeException(e)
        } catch (e: NoSuchAlgorithmException) {
            throw RuntimeException(e)
        } catch (e: InvalidKeyException) {
            throw RuntimeException(e)
        } catch (e: IllegalBlockSizeException) {
            throw RuntimeException(e)
        } catch (e: BadPaddingException) {
            throw RuntimeException(e)
        }
    }

    companion object {
        const val ENCRYPTED_CONTENT_ENCRYPTING_KEY: String =
            "aes_cbc_envelope_encryption-content-encrypting-key"
        const val INITIALIZATION_VECTOR: String =
            "aes_cbc_envelope_encryption-initialization-vector"

        const val AES_KEY_SIZE_BITS: Int = 256
        private const val AES_CBC_INITIALIZATION_VECTOR_SIZE_BYTES = 16
        private val BASE64_ENCODER: Base64.Encoder = Base64.getEncoder()
        private val SECURE_RANDOM = SecureRandom()

        const val KEY_ENCRYPTING_ALGO: String = "AES"

        // There's no specific KeyGenerator for AES/CBC/PKCS5Padding, so we just use a normal AES
        // KeyGenerator
        private const val CONTENT_ENCRYPTING_KEY_ALGO = "AES"

        // Redshift's UNLOAD command uses this cipher mode, so we'll use it here as well.
        // TODO If we eventually want to expose client-side encryption in destination-s3, we should
        // probably
        // also implement
        // AES-GCM, since it's mostly superior to CBC mode. (if we do that: make sure that the
        // output is
        // compatible with
        // aws-java-sdk's AmazonS3EncryptionV2Client, which requires a slightly different set of
        // metadata)
        private const val CONTENT_ENCRYPTING_CIPHER_ALGO = "AES/CBC/PKCS5Padding"

        private fun randomContentEncryptingKey(): SecretKey {
            try {
                val cekGenerator =
                    KeyGenerator.getInstance(
                        CONTENT_ENCRYPTING_KEY_ALGO,
                    )
                cekGenerator.init(AES_KEY_SIZE_BITS)
                return cekGenerator.generateKey()
            } catch (e: NoSuchAlgorithmException) {
                throw RuntimeException(e)
            }
        }

        private fun randomInitializationVector(): ByteArray {
            val initializationVector = ByteArray(AES_CBC_INITIALIZATION_VECTOR_SIZE_BYTES)
            SECURE_RANDOM.nextBytes(initializationVector)
            return initializationVector
        }
    }
}
