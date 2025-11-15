/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.util

import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.*
import java.net.URI
import java.nio.charset.StandardCharsets
import java.nio.file.FileSystem
import java.nio.file.FileSystems
import java.nio.file.Files
import java.security.*
import java.security.cert.Certificate
import java.security.cert.CertificateException
import java.security.cert.CertificateFactory
import java.security.spec.InvalidKeySpecException
import java.security.spec.PKCS8EncodedKeySpec
import java.util.*
import java.util.concurrent.*
import javax.net.ssl.SSLContext
import org.apache.http.ssl.SSLContexts

private val LOGGER = KotlinLogging.logger {}
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

    @Throws(
        IOException::class,
        CertificateException::class,
        KeyStoreException::class,
        NoSuchAlgorithmException::class
    )
    private fun saveKeyStoreToFile(
        keyStore: KeyStore,
        keyStorePassword: String,
        filesystem: FileSystem?,
        directory: String?
    ): URI {
        val fs = Objects.requireNonNullElse(filesystem, FileSystems.getDefault())
        val pathToStore = fs!!.getPath(Objects.toString(directory, "/tmp"))
        val pathToFile =
            pathToStore.resolve(KEYSTORE_FILE_NAME + RANDOM.nextInt() + KEYSTORE_FILE_TYPE)
        val os = Files.newOutputStream(pathToFile)
        keyStore.store(os, keyStorePassword.toCharArray())
        assert(Files.exists(pathToFile) == true)
        return pathToFile.toUri()
    }

    @Throws(IOException::class, InterruptedException::class)
    private fun runProcess(cmd: String, run: Runtime) {
        LOGGER.debug { "running [$cmd]" }
        @Suppress("deprecation") val p = run.exec(cmd)
        if (!p.waitFor(30, TimeUnit.SECONDS)) {
            p.destroy()
            throw RuntimeException("Timeout while executing: $cmd")
        }
    }

    @Throws(CertificateException::class)
    private fun fromPEMString(certString: String): Certificate {
        val cf = CertificateFactory.getInstance(X509)
        val byteArrayInputStream =
            ByteArrayInputStream(certString.toByteArray(StandardCharsets.UTF_8))
        val bufferedInputStream = BufferedInputStream(byteArrayInputStream)
        return cf.generateCertificate(bufferedInputStream)
    }

    @Throws(
        KeyStoreException::class,
        CertificateException::class,
        IOException::class,
        NoSuchAlgorithmException::class
    )
    fun keyStoreFromCertificate(
        cert: Certificate?,
        keyStorePassword: String,
        filesystem: FileSystem?,
        directory: String?
    ): URI {
        val keyStore = KeyStore.getInstance(PKCS_12)
        keyStore.load(null)
        keyStore.setCertificateEntry(KEYSTORE_ENTRY_PREFIX + "1", cert)
        return saveKeyStoreToFile(keyStore, keyStorePassword, filesystem, directory)
    }

    @JvmStatic
    @Throws(
        CertificateException::class,
        IOException::class,
        KeyStoreException::class,
        NoSuchAlgorithmException::class
    )
    fun keyStoreFromCertificate(
        certString: String,
        keyStorePassword: String,
        filesystem: FileSystem?,
        directory: String?
    ): URI {
        return keyStoreFromCertificate(
            fromPEMString(certString),
            keyStorePassword,
            filesystem,
            directory
        )
    }

    @Throws(
        CertificateException::class,
        IOException::class,
        KeyStoreException::class,
        NoSuchAlgorithmException::class
    )
    fun keyStoreFromCertificate(certString: String, keyStorePassword: String): URI {
        return keyStoreFromCertificate(fromPEMString(certString), keyStorePassword, null, null)
    }

    @Throws(
        CertificateException::class,
        IOException::class,
        KeyStoreException::class,
        NoSuchAlgorithmException::class
    )
    fun keyStoreFromCertificate(
        certString: String,
        keyStorePassword: String,
        directory: String?
    ): URI {
        return keyStoreFromCertificate(
            certString,
            keyStorePassword,
            FileSystems.getDefault(),
            directory
        )
    }

    @Throws(
        KeyStoreException::class,
        CertificateException::class,
        IOException::class,
        NoSuchAlgorithmException::class
    )
    fun keyStoreFromClientCertificate(
        cert: Certificate,
        key: PrivateKey?,
        keyStorePassword: String,
        filesystem: FileSystem?,
        directory: String?
    ): URI {
        val keyStore = KeyStore.getInstance(PKCS_12)
        keyStore.load(null)
        keyStore.setKeyEntry(
            KEYSTORE_ENTRY_PREFIX,
            key,
            keyStorePassword.toCharArray(),
            arrayOf(cert)
        )
        return saveKeyStoreToFile(keyStore, keyStorePassword, filesystem, directory)
    }

    @Throws(
        IOException::class,
        InterruptedException::class,
        NoSuchAlgorithmException::class,
        InvalidKeySpecException::class,
        CertificateException::class,
        KeyStoreException::class
    )
    fun keyStoreFromClientCertificate(
        certString: String,
        keyString: String,
        keyStorePassword: String,
        filesystem: FileSystem?,
        directory: String?
    ): URI {
        // Convert RSA key (PKCS#1) to PKCS#8 key
        // Note: java.security doesn't have a built-in support of PKCS#1 format. A conversion using
        // openssl
        // is necessary.
        // Since this is a single operation it's better than adding an external lib (e.g
        // BouncyCastle)

        val tmpDir = Files.createTempDirectory(null)
        val pkcs1Key = Files.createTempFile(tmpDir, null, null)
        val pkcs8Key = Files.createTempFile(tmpDir, null, null)
        pkcs1Key.toFile().deleteOnExit()
        pkcs8Key.toFile().deleteOnExit()

        Files.write(pkcs1Key, keyString.toByteArray(StandardCharsets.UTF_8))
        runProcess(
            "openssl pkcs8 -topk8 -inform PEM -outform DER -in " +
                pkcs1Key.toAbsolutePath() +
                " -out " +
                pkcs8Key.toAbsolutePath() +
                " -nocrypt -passout pass:" +
                keyStorePassword,
            Runtime.getRuntime()
        )

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
            directory
        )
    }

    @JvmStatic
    @Throws(
        CertificateException::class,
        IOException::class,
        NoSuchAlgorithmException::class,
        InvalidKeySpecException::class,
        KeyStoreException::class,
        InterruptedException::class
    )
    fun keyStoreFromClientCertificate(
        certString: String,
        keyString: String,
        keyStorePassword: String,
        directory: String?
    ): URI {
        return keyStoreFromClientCertificate(
            certString,
            keyString,
            keyStorePassword,
            FileSystems.getDefault(),
            directory
        )
    }

    fun createContextFromCaCert(caCertificate: String): SSLContext {
        try {
            val factory = CertificateFactory.getInstance(X509)
            val trustedCa =
                factory.generateCertificate(
                    ByteArrayInputStream(caCertificate.toByteArray(StandardCharsets.UTF_8))
                )
            val trustStore = KeyStore.getInstance(PKCS_12)
            trustStore.load(null, null)
            trustStore.setCertificateEntry("ca", trustedCa)
            val sslContextBuilder = SSLContexts.custom().loadTrustMaterial(trustStore, null)
            return sslContextBuilder.build()
        } catch (e: Exception) {
            throw RuntimeException(e)
        }
    }
}
