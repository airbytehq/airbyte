/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.ssh

import io.airbyte.cdk.ConfigErrorException
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.StringReader
import java.net.InetSocketAddress
import java.security.Security
import java.time.Duration
import kotlin.time.toJavaDuration
import org.apache.sshd.client.SshClient
import org.apache.sshd.client.future.ConnectFuture
import org.apache.sshd.client.keyverifier.AcceptAllServerKeyVerifier
import org.apache.sshd.client.session.ClientSession
import org.apache.sshd.common.SshException
import org.apache.sshd.common.session.SessionHeartbeatController
import org.apache.sshd.common.util.net.SshdSocketAddress
import org.apache.sshd.common.util.security.SecurityUtils
import org.apache.sshd.core.CoreModuleProperties
import org.apache.sshd.server.forward.AcceptAllForwardingFilter
import org.bouncycastle.jce.provider.BouncyCastleProvider

private val log = KotlinLogging.logger {}

/**
 * Encapsulates a possible SSH tunnel.
 *
 * Create using [createTunnelSession].
 */
class TunnelSession
internal constructor(
    val address: InetSocketAddress,
    private val client: SshClient?,
    private val clientSession: ClientSession?,
) : AutoCloseable {
    override fun close() {
        clientSession?.let {
            log.info { "Closing SSH client session." }
            it.close()
        }
        client?.let {
            log.info { "Closing SSH client." }
            it.stop()
        }
    }
}

/** Creates an open [TunnelSession]. */
fun createTunnelSession(
    remote: SshdSocketAddress,
    sshTunnel: SshTunnelMethodConfiguration,
    connectionOptions: SshConnectionOptions,
): TunnelSession {
    if (sshTunnel is SshNoTunnelMethod) {
        return TunnelSession(remote.toInetSocketAddress(), null, null)
    }
    log.info { "Creating SSH client." }
    val client: SshClient = createClient(connectionOptions)
    try {
        client.start()
        // Create session.
        log.info { "Creating SSH client session." }
        val connectFuture: ConnectFuture =
            when (sshTunnel) {
                SshNoTunnelMethod -> TODO("unreachable code")
                is SshKeyAuthTunnelMethod ->
                    client.connect(sshTunnel.user.trim(), sshTunnel.host.trim(), sshTunnel.port)
                is SshPasswordAuthTunnelMethod ->
                    client.connect(sshTunnel.user.trim(), sshTunnel.host.trim(), sshTunnel.port)
            }
        val session: ClientSession = connectFuture.verify(tunnelSessionTimeout).session
        when (sshTunnel) {
            SshNoTunnelMethod -> Unit
            is SshKeyAuthTunnelMethod -> {
                val key: String = sshTunnel.key.replace("\\n", "\n")
                val keyPair =
                    SecurityUtils.getKeyPairResourceParser()
                        .loadKeyPairs(null, null, null, StringReader(key))
                        ?.firstOrNull()
                        ?: throw ConfigErrorException(
                            "Unable to load private key pairs, " +
                                "verify key pairs are properly inputted",
                        )
                session.addPublicKeyIdentity(keyPair)
            }
            is SshPasswordAuthTunnelMethod -> {
                // remove default key provider looking at the machine's real ssh key
                session.keyIdentityProvider = null
                session.addPasswordIdentity(sshTunnel.password)
            }
        }
        session.auth().verify(tunnelSessionTimeout)
        log.info { "Established tunneling session to $remote." }
        // Start port forwarding.
        val localhost: String = SshdSocketAddress.LOCALHOST_ADDRESS.hostName
        val address: SshdSocketAddress =
            session.startLocalPortForwarding(
                SshdSocketAddress(InetSocketAddress.createUnresolved(localhost, 0)),
                remote,
            )
        log.info { "Port forwarding started on $address." }
        return TunnelSession(address.toInetSocketAddress(), client, session)
    } catch (e: SshException) {
        if (
            (e.message ?: "")
                .lowercase()
                .contains("failed to get operation result within specified timeout")
        ) {
            throw ConfigErrorException(SSH_TIMEOUT_DISPLAY_MESSAGE, e)
        } else {
            throw RuntimeException(e)
        }
    }
}

const val SSH_TIMEOUT_DISPLAY_MESSAGE: String =
    "Timed out while opening a SSH Tunnel. " +
        "Please double check the given SSH configurations and try again."

private val tunnelSessionTimeout: Duration = Duration.ofMillis(15_000)

private fun createClient(connectionOptions: SshConnectionOptions): SshClient {
    Security.addProvider(BouncyCastleProvider())
    val client: SshClient = SshClient.setUpDefaultClient()
    client.forwardingFilter = AcceptAllForwardingFilter.INSTANCE
    client.serverKeyVerifier = AcceptAllServerKeyVerifier.INSTANCE
    // Session level heartbeat using SSH_MSG_IGNORE every second.
    client.setSessionHeartbeat(
        SessionHeartbeatController.HeartbeatType.IGNORE,
        connectionOptions.sessionHeartbeatInterval.toJavaDuration(),
    )
    // idle-timeout zero indicates NoTimeout.
    CoreModuleProperties.IDLE_TIMEOUT[client] = connectionOptions.idleTimeout.toJavaDuration()
    // Use tcp keep-alive mechanism.
    CoreModuleProperties.SOCKET_KEEPALIVE[client] = true
    // Additional delay used for ChannelOutputStream to wait for space in the remote socket
    // send buffer.
    CoreModuleProperties.WAIT_FOR_SPACE_TIMEOUT[client] = Duration.ofMinutes(2)
    // Global keepalive message sent every 2 seconds.
    // This precedes the session level heartbeat.
    CoreModuleProperties.HEARTBEAT_INTERVAL[client] =
        connectionOptions.globalHeartbeatInterval.toJavaDuration()
    return client
}
