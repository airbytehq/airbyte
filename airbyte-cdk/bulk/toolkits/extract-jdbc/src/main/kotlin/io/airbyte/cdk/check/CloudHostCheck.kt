/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.check

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import java.net.InetAddress
import java.net.UnknownHostException

/**
 * Validates the value a user typed into the `Host` field before any connection is attempted.
 *
 * On Airbyte Cloud ([FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT]) two mistakes are common enough to
 * deserve their own message instead of the generic unreachable-host error the driver produces:
 * - a loopback or unspecified address (`localhost`, `127.x.x.x`, `::1`, `0.0.0.0`) without an SSH
 *   tunnel, which Airbyte Cloud can never reach;
 * - a full URL, credentials or a `host:port` pair pasted into the field instead of a bare hostname.
 *
 * Outside Airbyte Cloud the check is a no-op: a self-managed deployment may well run next to its
 * database.
 *
 * [validateHostSyntax] runs the second half alone, with a connector-specific message, for a
 * connector whose `Host` can only ever be a public domain and which offers neither an SSH tunnel
 * nor a `Port` field (a cloud warehouse such as Snowflake): there the loopback message would send
 * the user to a tunnel option that does not exist.
 *
 * Call it before the JDBC connection is opened, typically at the start of
 * [io.airbyte.cdk.discover.MetadataQuerier.Factory.session]: with an unreachable host the
 * connection attempt fails first and [io.airbyte.cdk.discover.MetadataQuerier.extraChecks] is never
 * reached.
 */
object CloudHostCheck {

    const val LOCAL_HOST_MESSAGE: String =
        "Airbyte Cloud cannot reach a database on your own machine. " +
            "Use a hostname reachable from the internet, or configure an SSH tunnel."

    const val HOST_SYNTAX_MESSAGE: String =
        "Enter only the hostname in Host; put the port in the Port field."

    /**
     * @param host the host as the user typed it, not the address resolved through the tunnel.
     * @param sshTunnel the configured tunnel method; `null` and [SshNoTunnelMethod] mean no tunnel.
     * @param featureFlags the active feature flags; the check only runs with
     *   [FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT].
     * @throws ConfigErrorException with [HOST_SYNTAX_MESSAGE] when [host] carries a scheme, a path,
     *   credentials or an explicit port, or with [LOCAL_HOST_MESSAGE] when [host] is a loopback or
     *   unspecified address and no SSH tunnel is configured.
     */
    fun validate(
        host: String,
        sshTunnel: SshTunnelMethodConfiguration?,
        featureFlags: Set<FeatureFlag>,
    ) {
        if (FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT !in featureFlags) {
            return
        }
        validateHostSyntax(host, featureFlags)
        val hasTunnel: Boolean = sshTunnel != null && sshTunnel !is SshNoTunnelMethod
        if (!hasTunnel && isLoopbackOrUnspecified(host.trim())) {
            throw ConfigErrorException(LOCAL_HOST_MESSAGE)
        }
    }

    /**
     * The syntax half of [validate] on its own: no loopback check, and a [message] of the caller's
     * choosing instead of [HOST_SYNTAX_MESSAGE], which names a `Port` field.
     *
     * @param host the host as the user typed it.
     * @param featureFlags the active feature flags; the check only runs with
     *   [FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT].
     * @param message the text of the [ConfigErrorException].
     * @throws ConfigErrorException with [message] when [host] carries a scheme, a path, credentials
     *   or an explicit port.
     */
    fun validateHostSyntax(
        host: String,
        featureFlags: Set<FeatureFlag>,
        message: String = HOST_SYNTAX_MESSAGE,
    ) {
        if (FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT !in featureFlags) {
            return
        }
        if (hasExtraSyntax(host.trim())) {
            throw ConfigErrorException(message)
        }
    }

    /** True when [host] carries a scheme (`://`), a path (`/`), credentials (`@`) or a port. */
    internal fun hasExtraSyntax(host: String): Boolean =
        host.contains("://") || host.contains('/') || host.contains('@') || hasPortSuffix(host)

    private fun hasPortSuffix(host: String): Boolean =
        if (host.startsWith("[")) {
            // Bracketed IPv6 literal: a port can only follow the closing bracket.
            host.contains("]:")
        } else {
            // An unbracketed IPv6 literal has at least two colons, a host:port pair exactly one.
            host.count { it == ':' } == 1
        }

    /** True for `localhost`, any `127.x.x.x`, `0.0.0.0`, `::1` and `::`, bracketed or not. */
    internal fun isLoopbackOrUnspecified(host: String): Boolean {
        if (host.equals("localhost", ignoreCase = true)) {
            return true
        }
        val literal: String = host.removeSurrounding("[", "]")
        if (IPV4_LITERAL.matches(literal)) {
            return literal.startsWith("127.") || literal == "0.0.0.0"
        }
        if (!IPV6_LITERAL.matches(literal)) {
            // A hostname: never resolved here, resolving it is the driver's job.
            return false
        }
        // The regex guarantees a leading hex digit or colon and at least one colon, so
        // InetAddress parses this as an IPv6 literal and never performs a DNS lookup.
        val address: InetAddress =
            try {
                InetAddress.getByName(literal)
            } catch (_: UnknownHostException) {
                return false
            }
        return address.isLoopbackAddress || address.isAnyLocalAddress
    }

    private val IPV4_LITERAL = Regex("""\d{1,3}(\.\d{1,3}){3}""")
    private val IPV6_LITERAL = Regex("""[0-9A-Fa-f:][0-9A-Fa-f.]*:[0-9A-Fa-f:.]*""")
}
