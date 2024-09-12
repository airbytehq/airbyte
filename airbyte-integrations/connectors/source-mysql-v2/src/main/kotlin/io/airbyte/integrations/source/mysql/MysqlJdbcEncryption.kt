/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.jdbc.SSLCertificateUtils
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.net.MalformedURLException
import java.net.URI
import java.security.KeyStoreException
import java.security.NoSuchAlgorithmException
import java.security.cert.CertificateException
import java.security.spec.InvalidKeySpecException
import java.util.HashMap
import org.apache.commons.lang3.RandomStringUtils

private val log = KotlinLogging.logger {}

class MysqlJdbcEncryption(
    val sslMode: SSLMode = SSLMode.PREFERRED,
    val caCertificate: String? = null,
    val clientCertificate: String? = null,
    val clientKey: String? = null,
    val clientKeyPassword: String? = null,
) {
    companion object {
        const val TRUST_KEY_STORE_URL: String = "trustCertificateKeyStoreUrl"
        const val TRUST_KEY_STORE_PASS: String = "trustCertificateKeyStorePassword"
        const val CLIENT_KEY_STORE_URL: String = "clientCertificateKeyStoreUrl"
        const val CLIENT_KEY_STORE_PASS: String = "clientCertificateKeyStorePassword"
        const val CLIENT_KEY_STORE_TYPE: String = "clientCertificateKeyStoreType"
        const val TRUST_KEY_STORE_TYPE: String = "trustCertificateKeyStoreType"
        const val KEY_STORE_TYPE_PKCS12: String = "PKCS12"
        const val SSL_MODE: String = "sslMode"
    }

    private fun getOrGeneratePassword(): String {
        if (!clientKeyPassword.isNullOrEmpty()) {
            return clientKeyPassword
        } else {
            return RandomStringUtils.randomAlphanumeric(10)
        }
    }

    private fun prepareCACertificateKeyStore(): Pair<URI, String>? {
        // if config available
        // if has CA cert - make keystore
        // if has client cert
        // if has client password - make keystore using password
        // if no client password - make keystore using random password
        var caCertKeyStorePair: Pair<URI, String>? = null

        if (!caCertificate.isNullOrEmpty()) {
            val clientKeyPassword = getOrGeneratePassword()
            try {
                val caCertKeyStoreUri =
                    SSLCertificateUtils.keyStoreFromCertificate(
                        caCertificate,
                        clientKeyPassword,
                        null,
                        null
                    )
                caCertKeyStorePair = Pair(caCertKeyStoreUri, clientKeyPassword)
            } catch (ex: Exception) {
                when (ex) {
                    is CertificateException,
                    is IOException,
                    is KeyStoreException,
                    is NoSuchAlgorithmException,
                    is InvalidKeySpecException,
                    is InterruptedException -> {
                        throw RuntimeException("Failed to create keystore for CA certificate", ex)
                    }
                }
            }
        }

        return caCertKeyStorePair
    }

    private fun prepareClientCertificateKeyStore(): Pair<URI, String>? {
        var clientCertKeyStorePair: Pair<URI, String>? = null

        if (!clientCertificate.isNullOrEmpty() && !clientKey.isNullOrEmpty()) {
            val clientKeyPassword = getOrGeneratePassword()
            try {
                val clientCertKeyStoreUri =
                    SSLCertificateUtils.keyStoreFromClientCertificate(
                        clientCertificate,
                        clientKey,
                        clientKeyPassword,
                        null
                    )
                clientCertKeyStorePair = Pair(clientCertKeyStoreUri, clientKeyPassword)
            } catch (ex: Exception) {
                when (ex) {
                    is CertificateException,
                    is IOException,
                    is KeyStoreException,
                    is NoSuchAlgorithmException,
                    is InvalidKeySpecException,
                    is InterruptedException -> {
                        throw RuntimeException(
                            "Failed to create keystore for Client certificate",
                            ex
                        )
                    }
                }
            }
        }
        return clientCertKeyStorePair
    }

    fun parseSSLConfig(): Map<String, String> {
        var caCertKeyStorePair: Pair<URI, String>?
        var clientCertKeyStorePair: Pair<URI, String>?
        val additionalParameters: MutableMap<String, String> = HashMap()

        additionalParameters[SSL_MODE] = sslMode.jdbcPropertyName

        caCertKeyStorePair = prepareCACertificateKeyStore()

        if (null != caCertKeyStorePair) {
            log.debug { "uri for ca cert keystore: ${caCertKeyStorePair.first}" }
            try {
                additionalParameters.putAll(
                    mapOf(
                        TRUST_KEY_STORE_URL to caCertKeyStorePair.first.toURL().toString(),
                        TRUST_KEY_STORE_PASS to caCertKeyStorePair.second,
                        TRUST_KEY_STORE_TYPE to KEY_STORE_TYPE_PKCS12
                    )
                )
            } catch (e: MalformedURLException) {
                throw ConfigErrorException("Unable to get a URL for trust key store")
            }

            clientCertKeyStorePair = prepareClientCertificateKeyStore()

            if (null != clientCertKeyStorePair) {
                log.debug {
                    "uri for client cert keystore: ${clientCertKeyStorePair.first} / ${clientCertKeyStorePair.second}"
                }
                try {
                    additionalParameters.putAll(
                        mapOf(
                            CLIENT_KEY_STORE_URL to clientCertKeyStorePair.first.toURL().toString(),
                            CLIENT_KEY_STORE_PASS to clientCertKeyStorePair.second,
                            CLIENT_KEY_STORE_TYPE to KEY_STORE_TYPE_PKCS12
                        )
                    )
                } catch (e: MalformedURLException) {
                    throw ConfigErrorException("Unable to get a URL for client key store")
                }
            }
        }
        return additionalParameters
    }
}

enum class SSLMode(val jdbcPropertyName: String) {
    PREFERRED("preferred"),
    REQUIRED("required"),
    VERIFY_CA("verify_ca"),
    VERIFY_IDENTITY("verify_identity");

    companion object {

        fun fromJdbcPropertyName(jdbcPropertyName: String): SSLMode {
            return SSLMode.values().find { it.jdbcPropertyName == jdbcPropertyName }
                ?: throw SystemErrorException("Unknown SSL mode: $jdbcPropertyName")
        }
    }
}
