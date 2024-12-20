/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.jdbc.SSLCertificateUtils
import io.github.oshai.kotlinlogging.KotlinLogging
import java.net.MalformedURLException
import java.net.URI
import java.nio.file.FileSystems
import java.util.UUID

private val log = KotlinLogging.logger {}

class MySqlSourceEncryption(
    val sslMode: SslMode = SslMode.PREFERRED,
    val caCertificate: String? = null,
    val clientCertificate: String? = null,
    val clientKey: String? = null,
    val clientKeyPassword: String? = null,
) {

    /**
     * Enum representing the SSL mode for MySQL connections. The actual jdbc property name is the
     * lower case of the enum name.
     */
    enum class SslMode {
        PREFERRED,
        REQUIRED,
        VERIFY_CA,
        VERIFY_IDENTITY,
    }

    fun parseSSLConfig(): Map<String, String> {
        var caCertKeyStorePair: Pair<URI, String>?
        var clientCertKeyStorePair: Pair<URI, String>?
        val additionalParameters: MutableMap<String, String> = mutableMapOf()

        additionalParameters[SSL_MODE] = sslMode.name.lowercase()

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

    private fun getOrGeneratePassword(): String {
        if (!clientKeyPassword.isNullOrEmpty()) {
            return clientKeyPassword
        } else {
            return UUID.randomUUID().toString()
        }
    }

    private fun prepareCACertificateKeyStore(): Pair<URI, String>? {
        // if config is not available - done
        // if has CA cert - make keystore with given password or generate a new password.
        var caCertKeyStorePair: Pair<URI, String>? = null

        if (caCertificate.isNullOrEmpty()) {
            return caCertKeyStorePair
        }
        val clientKeyPassword = getOrGeneratePassword()
        try {
            val caCertKeyStoreUri =
                SSLCertificateUtils.keyStoreFromCertificate(
                    caCertificate,
                    clientKeyPassword,
                    FileSystems.getDefault(),
                    ""
                )
            return Pair(caCertKeyStoreUri, clientKeyPassword)
        } catch (ex: Exception) {
            throw ConfigErrorException("Failed to create keystore for CA certificate.", ex)
        }
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
                        ""
                    )
                clientCertKeyStorePair = Pair(clientCertKeyStoreUri, clientKeyPassword)
            } catch (ex: Exception) {
                throw RuntimeException("Failed to create keystore for Client certificate", ex)
            }
        }
        return clientCertKeyStorePair
    }

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
}
