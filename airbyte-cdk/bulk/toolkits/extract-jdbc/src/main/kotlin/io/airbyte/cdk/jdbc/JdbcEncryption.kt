/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.jdbc

import io.airbyte.cdk.jdbc.SSLCertificateUtils.keyStoreFromCertificate
import io.airbyte.cdk.jdbc.SSLCertificateUtils.keyStoreFromClientCertificate
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

private val LOGGER = KotlinLogging.logger {}

class JdbcEncryption(    val sslMode: String?= null,
                         val caCertificate: String? = null,
                         val clientCertificate: String? = null,
                         val clientKey: String? = null,
                         val clientKeyPassword: String? = null,
                         val sslKey: String ?= null) {

    val TRUST_KEY_STORE_URL: String = "trustCertificateKeyStoreUrl"
    val TRUST_KEY_STORE_PASS: String = "trustCertificateKeyStorePassword"
     val CLIENT_KEY_STORE_URL: String = "clientCertificateKeyStoreUrl"
     val CLIENT_KEY_STORE_PASS: String = "clientCertificateKeyStorePassword"
     val CLIENT_KEY_STORE_TYPE: String = "clientCertificateKeyStoreType"
     val TRUST_KEY_STORE_TYPE: String = "trustCertificateKeyStoreType"
     val KEY_STORE_TYPE_PKCS12: String = "PKCS12"
     val SSL_MODE: String = "sslMode"

    private fun getOrGeneratePassword(): String {
        if (!clientKeyPassword.isNullOrEmpty()) {
            return clientKeyPassword
        } else {
            return RandomStringUtils.randomAlphanumeric(10)
        }
    }

    fun prepareCACertificateKeyStore(): Pair<URI, String>? {
        // if config available
        // if has CA cert - make keystore
        // if has client cert
        // if has client password - make keystore using password
        // if no client password - make keystore using random password
        var caCertKeyStorePair: Pair<URI, String>? = null
        if (sslKey.isNullOrEmpty()) {
            return null
        }

        if (!caCertificate.isNullOrEmpty()) {
            val clientKeyPassword = getOrGeneratePassword()
            try {
                val caCertKeyStoreUri =
                    keyStoreFromCertificate(caCertificate, clientKeyPassword, null, null)
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

    fun prepareClientCertificateKeyStore(): Pair<URI, String>? {
        var clientCertKeyStorePair: Pair<URI, String>? = null
        if (!sslKey.isNullOrEmpty()) {
            return clientCertKeyStorePair
        }

        if (!clientCertificate.isNullOrEmpty() && !clientKey.isNullOrEmpty()) {
            val clientKeyPassword = getOrGeneratePassword()
            try {
                val clientCertKeyStoreUri =
                    keyStoreFromClientCertificate(
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
        // assume ssl if not explicitly mentioned.
        if (!sslKey.isNullOrEmpty()) {
            return additionalParameters
        }
        if (!sslMode.isNullOrEmpty()) {
            additionalParameters[SSL_MODE] = sslMode

            caCertKeyStorePair = prepareCACertificateKeyStore()

            if (null != caCertKeyStorePair) {
                LOGGER.debug { "uri for ca cert keystore: ${caCertKeyStorePair.first}" }
                try {
                    additionalParameters.putAll(
                        java.util.Map.of(
                            TRUST_KEY_STORE_URL,
                            caCertKeyStorePair.first.toURL().toString(),
                            TRUST_KEY_STORE_PASS,
                            caCertKeyStorePair.second,
                            TRUST_KEY_STORE_TYPE,
                            KEY_STORE_TYPE_PKCS12
                        )
                    )
                } catch (e: MalformedURLException) {
                    throw RuntimeException("Unable to get a URL for trust key store")
                }
            }

            clientCertKeyStorePair = prepareClientCertificateKeyStore()

            if (null != clientCertKeyStorePair) {
                LOGGER.debug {
                    "uri for client cert keystore: ${clientCertKeyStorePair.first} / ${clientCertKeyStorePair.second}"
                }
                try {
                    additionalParameters.putAll(
                        mapOf(
                            CLIENT_KEY_STORE_URL to
                                clientCertKeyStorePair.first.toURL().toString(),
                            CLIENT_KEY_STORE_PASS to clientCertKeyStorePair.second,
                            CLIENT_KEY_STORE_TYPE to KEY_STORE_TYPE_PKCS12
                        )
                    )
                } catch (e: MalformedURLException) {
                    throw RuntimeException("Unable to get a URL for client key store")
                }
            }
        }

        LOGGER.debug { "additional params: $additionalParameters" }
        return additionalParameters
    }

    class Builder {
        var sslMode: String = ""
        var caCertificate: String = ""
        var clientCertificate: String = ""
        var clientKey: String = ""
        var clientKeyPassword: String = ""
        var sslKey = ""

        fun setSslMode(sslMode: String) = apply { this.sslMode = sslMode }
        fun setCaCertificate(caCertificate: String) = apply { this.caCertificate = caCertificate }
        fun setClientCertificate(clientCertificate: String) = apply { this.clientCertificate = clientCertificate }
        fun setClientKey(clientKey: String) = apply { this.clientKey = clientKey }
        fun setClientKeyPassword(clientKeyPassword: String) = apply { this.clientKeyPassword = clientKeyPassword }
        fun setSslKey(sslKey: String) = apply { this.sslKey = sslKey }

        fun build() = JdbcEncryption(sslMode, caCertificate, clientCertificate, clientKey, clientKeyPassword, sslKey)
    }
}
