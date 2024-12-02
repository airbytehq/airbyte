/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.jdbc

import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.BufferedInputStream
import java.io.ByteArrayInputStream
import java.io.FileReader
import java.io.IOException
import java.net.URI
import java.nio.charset.StandardCharsets
import java.nio.file.FileSystem
import java.nio.file.FileSystems
import java.nio.file.Files
import java.nio.file.Path
import java.security.KeyFactory
import java.security.KeyStore
import java.security.KeyStoreException
import java.security.NoSuchAlgorithmException
import java.security.PrivateKey
import java.security.SecureRandom
import java.security.Security
import java.security.cert.Certificate
import java.security.cert.CertificateException
import java.security.cert.CertificateFactory
import java.security.spec.InvalidKeySpecException
import java.security.spec.PKCS8EncodedKeySpec
import java.util.*
import javax.net.ssl.SSLContext
import kotlin.text.Charsets.UTF_8
import org.bouncycastle.asn1.pkcs.PrivateKeyInfo
import org.bouncycastle.jce.provider.BouncyCastleProvider
import org.bouncycastle.openssl.PEMEncryptedKeyPair
import org.bouncycastle.openssl.PEMKeyPair
import org.bouncycastle.openssl.PEMParser
import org.bouncycastle.openssl.jcajce.JcaPEMKeyConverter
import org.bouncycastle.openssl.jcajce.JcePEMDecryptorProviderBuilder

private val log = KotlinLogging.logger {}

/**
 * General SSL utilities used for certificate and keystore operations related to secured db
 * connections.
 */
object SSLCertificateUtils {

    private const val PKCS_12 = "PKCS12"
    private const val X509 = "X.509"
    private val RANDOM: Random = SecureRandom()

    // #17000: postgres driver is hardcoded to only load an entry alias "user"
    const val KEYSTORE_ENTRY_PREFIX: String = "user"
    const val KEYSTORE_FILE_NAME: String = KEYSTORE_ENTRY_PREFIX + "keystore_"
    const val KEYSTORE_FILE_TYPE: String = ".p12"

    private fun saveKeyStoreToFile(
        keyStore: KeyStore,
        keyStorePassword: String,
        filesystem: FileSystem,
        directory: String
    ): URI {
        val pathToStore: Path = filesystem.getPath(directory)
        val pathToFile =
            pathToStore.resolve(KEYSTORE_FILE_NAME + RANDOM.nextInt() + KEYSTORE_FILE_TYPE)
        val os = Files.newOutputStream(pathToFile)
        keyStore.store(os, keyStorePassword.toCharArray())
        return pathToFile.toUri()
    }

    private fun fromPEMString(certString: String): Certificate {
        val cf = CertificateFactory.getInstance(X509)
        val byteArrayInputStream =
            ByteArrayInputStream(certString.toByteArray(StandardCharsets.UTF_8))
        val bufferedInputStream = BufferedInputStream(byteArrayInputStream)
        return cf.generateCertificate(bufferedInputStream)
    }

    fun keyStoreFromCertificate(
        cert: Certificate,
        keyStorePassword: String,
        filesystem: FileSystem,
        directory: String
    ): URI {
        val keyStore = KeyStore.getInstance(PKCS_12)
        keyStore.load(null)
        keyStore.setCertificateEntry(KEYSTORE_ENTRY_PREFIX + "1", cert)
        return saveKeyStoreToFile(keyStore, keyStorePassword, filesystem, directory)
    }

    fun keyStoreFromCertificate(
        certString: String,
        keyStorePassword: String,
        filesystem: FileSystem,
        directory: String
    ): URI {
        return keyStoreFromCertificate(
            fromPEMString(certString),
            keyStorePassword,
            filesystem,
            directory,
        )
    }

    fun keyStoreFromCertificate(certString: String, keyStorePassword: String): URI {
        return keyStoreFromCertificate(
            fromPEMString(certString),
            keyStorePassword,
            FileSystems.getDefault(),
            ""
        )
    }

    fun keyStoreFromCertificate(
        certString: String,
        keyStorePassword: String,
        directory: String
    ): URI {
        return keyStoreFromCertificate(
            certString,
            keyStorePassword,
            FileSystems.getDefault(),
            directory,
        )
    }

    fun keyStoreFromClientCertificate(
        cert: Certificate,
        key: PrivateKey,
        keyStorePassword: String,
        filesystem: FileSystem,
        directory: String
    ): URI {
        val keyStore = KeyStore.getInstance(PKCS_12)
        keyStore.load(null)
        keyStore.setKeyEntry(
            KEYSTORE_ENTRY_PREFIX,
            key,
            keyStorePassword.toCharArray(),
            arrayOf(cert),
        )
        return saveKeyStoreToFile(keyStore, keyStorePassword, filesystem, directory)
    }

    // Utility function to detect the key algorithm (RSA, DSA, EC) from the key bytes
    fun detectKeyAlgorithm(keyBytes: ByteArray): KeyFactory {
        return when {
            isRsaKey(keyBytes) -> KeyFactory.getInstance("RSA", "BC")
            isDsaKey(keyBytes) -> KeyFactory.getInstance("DSA", "BC")
            isEcKey(keyBytes) -> KeyFactory.getInstance("EC", "BC")
            else -> throw IllegalArgumentException("Unknown or unsupported key type")
        }
    }

    // Example heuristics for detecting the key type (you can adjust as needed)
    fun isRsaKey(keyBytes: ByteArray): Boolean {
        return keyBytes.size > 100 && keyBytes[0].toInt() == 0x30 // ASN.1 structure for RSA keys
    }

    fun isDsaKey(keyBytes: ByteArray): Boolean {
        return keyBytes.size > 50 &&
            keyBytes[0].toInt() == 0x30 // Adjust based on DSA key specifics
    }

    fun isEcKey(keyBytes: ByteArray): Boolean {
        return keyBytes.size > 50 && keyBytes[0].toInt() == 0x30 // ASN.1 structure for EC keys
    }

    @JvmStatic
    fun convertPKCS1ToPKCS8(pkcs1KeyPath: Path, pkcs8KeyPath: Path, keyStorePassword: String?) {
        Security.addProvider(BouncyCastleProvider())
        FileReader(pkcs1KeyPath.toFile(), UTF_8).use { reader ->
            val pemParser = PEMParser(reader)
            val pemObject = pemParser.readObject()
            // Convert PEM to a PrivateKey (JcaPEMKeyConverter handles different types like RSA,
            // DSA, EC)
            val converter = JcaPEMKeyConverter().setProvider("BC")
            val privateKey =
                when (pemObject) {
                    is PEMEncryptedKeyPair -> {
                        // Handle encrypted key (if it was encrypted with a password)
                        val decryptorProvider =
                            JcePEMDecryptorProviderBuilder().build(keyStorePassword?.toCharArray())
                        val keyPair = pemObject.decryptKeyPair(decryptorProvider)
                        converter.getPrivateKey(keyPair.privateKeyInfo)
                    }
                    is PEMKeyPair -> {
                        // Handle non-encrypted key
                        converter.getPrivateKey(pemObject.privateKeyInfo)
                    }
                    else -> throw IllegalArgumentException("Unsupported key format")
                }

            // Convert the private key to PKCS#8 format
            val pkcs8EncodedKey = convertToPkcs8(privateKey)

            // Write the PKCS#8 encoded key in DER format to the output path
            Files.write(pkcs8KeyPath, pkcs8EncodedKey)
        }
    }

    fun convertToPkcs8(privateKey: PrivateKey): ByteArray {
        // Convert the private key to PKCS#8 format using PrivateKeyInfo
        val privateKeyInfo = PrivateKeyInfo.getInstance(privateKey.encoded)
        return privateKeyInfo.encoded
    }

    @Throws(
        IOException::class,
        InterruptedException::class,
        NoSuchAlgorithmException::class,
        InvalidKeySpecException::class,
        CertificateException::class,
        KeyStoreException::class,
    )
    fun keyStoreFromClientCertificate(
        certString: String,
        keyString: String,
        keyStorePassword: String,
        filesystem: FileSystem,
        directory: String
    ): URI {
        // Convert RSA key (PKCS#1) to PKCS#8 key
        // Note: java.security doesn't have a built-in support of PKCS#1 format. Hence we need a
        // conversion using BouncyCastle.

        val tmpDir = Files.createTempDirectory(null)
        val pkcs1Key = Files.createTempFile(tmpDir, null, null)
        val pkcs8Key = Files.createTempFile(tmpDir, null, null)
        pkcs1Key.toFile().deleteOnExit()
        pkcs8Key.toFile().deleteOnExit()

        Files.write(pkcs1Key, keyString.toByteArray(StandardCharsets.UTF_8))
        convertPKCS1ToPKCS8(pkcs1Key.toAbsolutePath(), pkcs8Key.toAbsolutePath(), keyStorePassword)
        val spec = PKCS8EncodedKeySpec(Files.readAllBytes(pkcs8Key))
        var privateKey =
            try {
                KeyFactory.getInstance("RSA").generatePrivate(spec)
            } catch (ex1: InvalidKeySpecException) {
                try {
                    KeyFactory.getInstance("DSA").generatePrivate(spec)
                } catch (ex2: InvalidKeySpecException) {
                    KeyFactory.getInstance("EC").generatePrivate(spec)
                }
            }

        return keyStoreFromClientCertificate(
            fromPEMString(certString),
            privateKey,
            keyStorePassword,
            filesystem,
            directory,
        )
    }

    fun keyStoreFromClientCertificate(
        certString: String,
        keyString: String,
        keyStorePassword: String,
        directory: String
    ): URI {
        return keyStoreFromClientCertificate(
            certString,
            keyString,
            keyStorePassword,
            FileSystems.getDefault(),
            directory,
        )
    }

    fun createContextFromCaCert(caCertificate: String): SSLContext {
        try {
            val factory = CertificateFactory.getInstance(X509)
            val trustedCa =
                factory.generateCertificate(
                    ByteArrayInputStream(caCertificate.toByteArray(StandardCharsets.UTF_8)),
                )
            val trustStore = KeyStore.getInstance(PKCS_12)
            trustStore.load(null, null)
            trustStore.setCertificateEntry("ca", trustedCa)
            val sslContextBuilder =
                org.apache.http.ssl.SSLContexts.custom().loadTrustMaterial(trustStore, null)
            return sslContextBuilder.build()
        } catch (e: Exception) {
            throw RuntimeException(e)
        }
    }
}
