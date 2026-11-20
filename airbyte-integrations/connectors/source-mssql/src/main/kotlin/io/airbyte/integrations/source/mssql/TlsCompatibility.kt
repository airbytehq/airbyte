/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.github.oshai.kotlinlogging.KotlinLogging
import java.security.Security
import java.text.MessageFormat
import java.util.concurrent.ConcurrentHashMap
import java.util.logging.Handler
import java.util.logging.Level
import java.util.logging.LogRecord
import java.util.logging.Logger

private val log = KotlinLogging.logger {}

/**
 * Keeps the TLS behavior the connector had on its previous base image, and logs what each TLS
 * connection negotiates.
 *
 * JDK 21.0.10 added `TLS_RSA_*` (static-RSA key exchange cipher suites) and the SHA-1 handshake
 * signature schemes to `jdk.tls.disabledAlgorithms`. A SQL Server instance that only offers those
 * can no longer complete the TLS handshake, which SQL Server performs for the login packet in every
 * encryption mode. [install] removes exactly those entries again, so that the connector keeps
 * connecting to the instances it could connect to before the JDK upgrade.
 *
 * The handshake log lines tell which instances still depend on this: once no connection negotiates
 * a `TLS_RSA_WITH_*` cipher suite anymore, the compatibility setting can be removed.
 */
object TlsCompatibility {

    const val DISABLED_ALGORITHMS_PROPERTY = "jdk.tls.disabledAlgorithms"
    const val SECURITY_EVENT_LOGGER_NAME = "jdk.event.security"

    private const val STATIC_RSA_CIPHER_SUITES = "TLS_RSA_*"
    private val sha1HandshakeSignature =
        Regex(""".*_sha1\s+usage\s+HandshakeSignature""", RegexOption.IGNORE_CASE)

    private const val TLS_HANDSHAKE_EVENT = "TLSHandshake"
    private val formattedHandshakeEvent =
        Regex("""$TLS_HANDSHAKE_EVENT:\s*(.+):(\d+),\s*([^,\s]+),\s*([^,\s]+)""")

    /**
     * The JDK's security event log. `java.util.logging` only holds its loggers weakly: this
     * reference keeps the level and the handler set by [install] alive.
     */
    private val securityEventLogger: Logger = Logger.getLogger(SECURITY_EVENT_LOGGER_NAME)
    private val loggedHandshakes: MutableSet<Handshake> = ConcurrentHashMap.newKeySet()

    /** What one completed TLS handshake negotiated. */
    data class Handshake(
        val peerHost: String,
        val peerPort: String,
        val protocol: String,
        val cipherSuite: String,
    ) {
        val isStaticRsa: Boolean
            get() = cipherSuite.startsWith("TLS_RSA_WITH_")

        val logMessage: String
            get() =
                "TLS handshake: peer=$peerHost:$peerPort protocol=$protocol " +
                    "cipherSuite=$cipherSuite" +
                    if (isStaticRsa) {
                        " (static-RSA key exchange: no forward secrecy, disabled by default in " +
                            "current JDKs; enable ECDHE cipher suites on the server)"
                    } else {
                        ""
                    }
    }

    /**
     * Returns [current], a `jdk.tls.disabledAlgorithms` value, without its `TLS_RSA_*` and `*_sha1
     * usage HandshakeSignature` entries. All other entries are kept, in their original order.
     */
    fun relaxDisabledAlgorithms(current: String): String =
        entries(current).filterNot(::isReEnabled).joinToString(", ")

    /**
     * Maps a record of the JDK's security event log to the [Handshake] it reports, or to null when
     * it is not a readable `TLSHandshake` record. The JDK logs these records with the message
     * template ` TLSHandshake: {0}:{1,number,#}, {2}, {3}, {4,number,#}` and the parameters peer
     * host, peer port, protocol version, cipher suite, certificate id.
     */
    fun handshakeOf(message: String?, parameters: Array<out Any?>?): Handshake? {
        if (message == null || !message.contains(TLS_HANDSHAKE_EVENT)) {
            return null
        }
        if (parameters != null && parameters.size >= 4) {
            val host: Any? = parameters[0]
            val port: Any? = parameters[1]
            val protocol: Any? = parameters[2]
            val cipherSuite: Any? = parameters[3]
            if (host is String && port is Number && protocol is String && cipherSuite is String) {
                return Handshake(host, port.toLong().toString(), protocol, cipherSuite)
            }
        }
        // Not the expected parameters: read the values from the formatted message instead.
        val formatted: String =
            try {
                if (parameters.isNullOrEmpty()) message
                else MessageFormat.format(message, *parameters)
            } catch (_: IllegalArgumentException) {
                return null
            }
        val (host, port, protocol, cipherSuite) =
            formattedHandshakeEvent.find(formatted)?.destructured ?: return null
        return Handshake(host, port, protocol, cipherSuite)
    }

    /**
     * Starts logging the negotiated TLS protocol and cipher suite of each distinct peer, then
     * re-enables the static-RSA cipher suites and the SHA-1 handshake signatures when the JDK
     * disables them by default. Must run before anything in the JVM initializes TLS.
     */
    fun install() {
        // The JDK decides only once, at its first security event, whether its security event log
        // is enabled. Setting a security property is such an event, so this has to come first.
        if (securityEventLogger.handlers.none { it === HandshakeLogHandler }) {
            securityEventLogger.level = Level.FINE
            securityEventLogger.useParentHandlers = false
            securityEventLogger.addHandler(HandshakeLogHandler)
        }

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

    /**
     * Logs each distinct peer, protocol and cipher suite once per process. The same logger also
     * carries the JDK's certificate and security property events, which are ignored.
     */
    private object HandshakeLogHandler : Handler() {
        override fun publish(record: LogRecord?) {
            try {
                val message: String = record?.message ?: return
                if (!message.contains(TLS_HANDSHAKE_EVENT)) {
                    return
                }
                val handshake: Handshake = handshakeOf(message, record.parameters) ?: return
                if (!loggedHandshakes.add(handshake)) {
                    return
                }
                if (handshake.isStaticRsa) {
                    log.warn { handshake.logMessage }
                } else {
                    log.info { handshake.logMessage }
                }
            } catch (_: Exception) {
                // Logging must never fail the TLS handshake that is being reported.
            }
        }

        override fun flush() {}

        override fun close() {}
    }
}
