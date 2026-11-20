/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.github.oshai.kotlinlogging.KotlinLogging
import java.security.Security

private val log = KotlinLogging.logger {}

/**
 * Keeps the TLS behavior the connector had on its previous base image.
 *
 * JDK 21.0.10 added `TLS_RSA_*` (static-RSA key exchange cipher suites) and the SHA-1 handshake
 * signature schemes to `jdk.tls.disabledAlgorithms`. A SQL Server instance that only offers those
 * can no longer complete the TLS handshake, which SQL Server performs for the login packet in every
 * encryption mode. [install] removes exactly those entries again, so that the connector keeps
 * connecting to the instances it could connect to before the JDK upgrade.
 */
object TlsCompatibility {

    const val DISABLED_ALGORITHMS_PROPERTY = "jdk.tls.disabledAlgorithms"

    private const val STATIC_RSA_CIPHER_SUITES = "TLS_RSA_*"
    private val sha1HandshakeSignature =
        Regex(""".*_sha1\s+usage\s+HandshakeSignature""", RegexOption.IGNORE_CASE)

    /**
     * Returns [current], a `jdk.tls.disabledAlgorithms` value, without its `TLS_RSA_*` and `*_sha1
     * usage HandshakeSignature` entries. All other entries are kept, in their original order.
     */
    fun relaxDisabledAlgorithms(current: String): String =
        entries(current).filterNot(::isReEnabled).joinToString(", ")

    /**
     * Re-enables the static-RSA cipher suites and the SHA-1 handshake signatures when the JDK
     * disables them by default. Must run before anything in the JVM initializes TLS.
     */
    fun install() {
        val current: String = Security.getProperty(DISABLED_ALGORITHMS_PROPERTY) ?: return
        val reEnabled: List<String> = entries(current).filter(::isReEnabled)
        if (reEnabled.isEmpty()) {
            return
        }
        Security.setProperty(DISABLED_ALGORITHMS_PROPERTY, relaxDisabledAlgorithms(current))
        log.info {
            "TLS compatibility: re-enabled ${reEnabled.joinToString(", ")} " +
                "(disabled by default since JDK 21.0.10) to keep connecting to SQL Server " +
                "instances that only offer them."
        }
    }

    private fun entries(disabledAlgorithms: String): List<String> =
        disabledAlgorithms.split(',').map { it.trim() }.filter { it.isNotEmpty() }

    private fun isReEnabled(entry: String): Boolean =
        entry.equals(STATIC_RSA_CIPHER_SUITES, ignoreCase = true) ||
            sha1HandshakeSignature.matches(entry)
}
