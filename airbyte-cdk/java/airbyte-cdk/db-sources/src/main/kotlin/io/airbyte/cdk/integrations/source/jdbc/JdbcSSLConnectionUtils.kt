/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.jdbc

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.db.util.SSLCertificateUtils.keyStoreFromCertificate
import io.airbyte.cdk.db.util.SSLCertificateUtils.keyStoreFromClientCertificate
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.net.MalformedURLException
import java.net.URI
import java.nio.file.Files
import java.nio.file.Path
import java.security.KeyStoreException
import java.security.NoSuchAlgorithmException
import java.security.cert.CertificateException
import java.security.spec.InvalidKeySpecException
import java.util.*
import org.apache.commons.lang3.RandomStringUtils
import org.apache.commons.lang3.tuple.ImmutablePair
import org.apache.commons.lang3.tuple.Pair

private val LOGGER = KotlinLogging.logger {}

class JdbcSSLConnectionUtils {
    var caCertKeyStorePair: Pair<URI, String>? = null
    var clientCertKeyStorePair: Pair<URI, String>? = null

    enum class SslMode(vararg spec: String) {
        DISABLED("disable"),
        ALLOWED("allow"),
        PREFERRED("preferred", "prefer"),
        REQUIRED("required", "require"),
        VERIFY_CA("verify_ca", "verify-ca"),
        VERIFY_IDENTITY("verify_identity", "verify-full");

        val spec: List<String> = Arrays.asList(*spec)

        companion object {
            fun bySpec(spec: String): Optional<SslMode> {
                return Arrays.stream(entries.toTypedArray())
                    .filter { sslMode: SslMode -> sslMode.spec.contains(spec) }
                    .findFirst()
            }
        }
    }

    companion object {
        const val SSL_MODE: String = "sslMode"

        const val TRUST_KEY_STORE_URL: String = "trustCertificateKeyStoreUrl"
        const val TRUST_KEY_STORE_PASS: String = "trustCertificateKeyStorePassword"
        const val CLIENT_KEY_STORE_URL: String = "clientCertificateKeyStoreUrl"
        const val CLIENT_KEY_STORE_PASS: String = "clientCertificateKeyStorePassword"
        const val CLIENT_KEY_STORE_TYPE: String = "clientCertificateKeyStoreType"
        const val TRUST_KEY_STORE_TYPE: String = "trustCertificateKeyStoreType"
        const val KEY_STORE_TYPE_PKCS12: String = "PKCS12"
        const val PARAM_MODE: String = "mode"

        const val PARAM_CA_CERTIFICATE: String = "ca_certificate"
        const val PARAM_CLIENT_CERTIFICATE: String = "client_certificate"
        const val PARAM_CLIENT_KEY: String = "client_key"
        const val PARAM_CLIENT_KEY_PASSWORD: String = "client_key_password"

        /**
         * Parses SSL related configuration and generates keystores to be used by connector
         *
         * @param config configuration
         * @return map containing relevant parsed values including location of keystore or an empty
         * map
         */
        @JvmStatic
        fun parseSSLConfig(config: JsonNode): Map<String, String> {
            LOGGER.debug { "source config: $config" }

            var caCertKeyStorePair: Pair<URI, String>?
            var clientCertKeyStorePair: Pair<URI, String>?
            val additionalParameters: MutableMap<String, String> = HashMap()
            // assume ssl if not explicitly mentioned.
            if (!config.has(JdbcUtils.SSL_KEY) || config[JdbcUtils.SSL_KEY].asBoolean()) {
                if (config.has(JdbcUtils.SSL_MODE_KEY)) {
                    val specMode = config[JdbcUtils.SSL_MODE_KEY][PARAM_MODE].asText()
                    additionalParameters[SSL_MODE] =
                        SslMode.bySpec(specMode)
                            .orElseThrow { IllegalArgumentException("unexpected ssl mode") }
                            .name
                    caCertKeyStorePair = prepareCACertificateKeyStore(config)

                    if (null != caCertKeyStorePair) {
                        LOGGER.debug { "uri for ca cert keystore: ${caCertKeyStorePair.left}" }
                        try {
                            additionalParameters.putAll(
                                java.util.Map.of(
                                    TRUST_KEY_STORE_URL,
                                    caCertKeyStorePair.left.toURL().toString(),
                                    TRUST_KEY_STORE_PASS,
                                    caCertKeyStorePair.right,
                                    TRUST_KEY_STORE_TYPE,
                                    KEY_STORE_TYPE_PKCS12
                                )
                            )
                        } catch (e: MalformedURLException) {
                            throw RuntimeException("Unable to get a URL for trust key store")
                        }
                    }

                    clientCertKeyStorePair = prepareClientCertificateKeyStore(config)

                    if (null != clientCertKeyStorePair) {
                        LOGGER.debug {
                            "uri for client cert keystore: ${clientCertKeyStorePair.left} / ${clientCertKeyStorePair.right}"
                        }
                        try {
                            additionalParameters.putAll(
                                java.util.Map.of(
                                    CLIENT_KEY_STORE_URL,
                                    clientCertKeyStorePair.left.toURL().toString(),
                                    CLIENT_KEY_STORE_PASS,
                                    clientCertKeyStorePair.right,
                                    CLIENT_KEY_STORE_TYPE,
                                    KEY_STORE_TYPE_PKCS12
                                )
                            )
                        } catch (e: MalformedURLException) {
                            throw RuntimeException("Unable to get a URL for client key store")
                        }
                    }
                } else {
                    additionalParameters[SSL_MODE] = SslMode.DISABLED.name
                }
            }
            LOGGER.debug { "additional params: $additionalParameters" }
            return additionalParameters
        }

        @JvmStatic
        fun prepareCACertificateKeyStore(config: JsonNode): Pair<URI, String>? {
            // if config available
            // if has CA cert - make keystore
            // if has client cert
            // if has client password - make keystore using password
            // if no client password - make keystore using random password
            var caCertKeyStorePair: Pair<URI, String>? = null
            if (Objects.nonNull(config)) {
                if (!config.has(JdbcUtils.SSL_KEY) || config[JdbcUtils.SSL_KEY].asBoolean()) {
                    val encryption = config[JdbcUtils.SSL_MODE_KEY]
                    if (
                        encryption.has(PARAM_CA_CERTIFICATE) &&
                            !encryption[PARAM_CA_CERTIFICATE].asText().isEmpty()
                    ) {
                        val clientKeyPassword = getOrGeneratePassword(encryption)
                        try {
                            val caCertKeyStoreUri =
                                keyStoreFromCertificate(
                                    encryption[PARAM_CA_CERTIFICATE].asText(),
                                    clientKeyPassword,
                                    null,
                                    null
                                )
                            caCertKeyStorePair = ImmutablePair(caCertKeyStoreUri, clientKeyPassword)
                        } catch (e: CertificateException) {
                            throw RuntimeException(
                                "Failed to create keystore for CA certificate",
                                e
                            )
                        } catch (e: IOException) {
                            throw RuntimeException(
                                "Failed to create keystore for CA certificate",
                                e
                            )
                        } catch (e: KeyStoreException) {
                            throw RuntimeException(
                                "Failed to create keystore for CA certificate",
                                e
                            )
                        } catch (e: NoSuchAlgorithmException) {
                            throw RuntimeException(
                                "Failed to create keystore for CA certificate",
                                e
                            )
                        }
                    }
                }
            }
            return caCertKeyStorePair
        }

        private fun getOrGeneratePassword(sslModeConfig: JsonNode): String {
            val clientKeyPassword =
                if (
                    sslModeConfig.has(PARAM_CLIENT_KEY_PASSWORD) &&
                        !sslModeConfig[PARAM_CLIENT_KEY_PASSWORD].asText().isEmpty()
                ) {
                    sslModeConfig[PARAM_CLIENT_KEY_PASSWORD].asText()
                } else {
                    RandomStringUtils.randomAlphanumeric(10)
                }
            return clientKeyPassword
        }

        fun prepareClientCertificateKeyStore(config: JsonNode): Pair<URI, String>? {
            var clientCertKeyStorePair: Pair<URI, String>? = null
            if (Objects.nonNull(config)) {
                if (!config.has(JdbcUtils.SSL_KEY) || config[JdbcUtils.SSL_KEY].asBoolean()) {
                    val encryption = config[JdbcUtils.SSL_MODE_KEY]
                    if (
                        encryption.has(PARAM_CLIENT_CERTIFICATE) &&
                            !encryption[PARAM_CLIENT_CERTIFICATE].asText().isEmpty() &&
                            encryption.has(PARAM_CLIENT_KEY) &&
                            !encryption[PARAM_CLIENT_KEY].asText().isEmpty()
                    ) {
                        val clientKeyPassword = getOrGeneratePassword(encryption)
                        try {
                            val clientCertKeyStoreUri =
                                keyStoreFromClientCertificate(
                                    encryption[PARAM_CLIENT_CERTIFICATE].asText(),
                                    encryption[PARAM_CLIENT_KEY].asText(),
                                    clientKeyPassword,
                                    null
                                )
                            clientCertKeyStorePair =
                                ImmutablePair(clientCertKeyStoreUri, clientKeyPassword)
                        } catch (e: CertificateException) {
                            throw RuntimeException(
                                "Failed to create keystore for Client certificate",
                                e
                            )
                        } catch (e: IOException) {
                            throw RuntimeException(
                                "Failed to create keystore for Client certificate",
                                e
                            )
                        } catch (e: KeyStoreException) {
                            throw RuntimeException(
                                "Failed to create keystore for Client certificate",
                                e
                            )
                        } catch (e: NoSuchAlgorithmException) {
                            throw RuntimeException(
                                "Failed to create keystore for Client certificate",
                                e
                            )
                        } catch (e: InvalidKeySpecException) {
                            throw RuntimeException(
                                "Failed to create keystore for Client certificate",
                                e
                            )
                        } catch (e: InterruptedException) {
                            throw RuntimeException(
                                "Failed to create keystore for Client certificate",
                                e
                            )
                        }
                    }
                }
            }
            return clientCertKeyStorePair
        }

        @JvmStatic
        fun fileFromCertPem(certPem: String?): Path {
            try {
                val path = Files.createTempFile(null, ".crt")
                Files.writeString(path, certPem)
                path.toFile().deleteOnExit()
                return path
            } catch (e: IOException) {
                throw RuntimeException("Cannot save root certificate to file", e)
            }
        }
    }
}
