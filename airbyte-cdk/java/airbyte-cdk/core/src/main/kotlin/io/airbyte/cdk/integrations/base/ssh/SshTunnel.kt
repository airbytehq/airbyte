/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base.ssh

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.base.Preconditions
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.functional.CheckedConsumer
import io.airbyte.commons.functional.CheckedFunction
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.string.Strings
import java.io.*
import java.net.InetSocketAddress
import java.net.MalformedURLException
import java.net.URI
import java.net.URL
import java.security.*
import java.time.Duration
import java.util.*
import javax.validation.constraints.NotNull
import org.apache.sshd.client.SshClient
import org.apache.sshd.client.keyverifier.AcceptAllServerKeyVerifier
import org.apache.sshd.client.session.ClientSession
import org.apache.sshd.common.SshException
import org.apache.sshd.common.session.SessionHeartbeatController
import org.apache.sshd.common.util.net.SshdSocketAddress
import org.apache.sshd.common.util.security.SecurityUtils
import org.apache.sshd.core.CoreModuleProperties
import org.apache.sshd.server.forward.AcceptAllForwardingFilter
import org.bouncycastle.jce.provider.BouncyCastleProvider
import org.slf4j.Logger
import org.slf4j.LoggerFactory

// todo (cgardens) - this needs unit tests. it is currently tested transitively via source postgres
// integration tests.
/**
 * Encapsulates the connection configuration for an ssh tunnel port forward through a proxy/bastion
 * host plus the remote host and remote port to forward to a specified local port.
 */
open class SshTunnel
@JvmOverloads
/**
 *
 * @param originalConfig
 * - the full config that was passed to the source.
 * @param hostKey
 * - a list of keys that point to the database host name. should be pointing to where in the config
 * remoteDatabaseHost is found.
 * @param portKey
 * - a list of keys that point to the database port. should be pointing to where in the config
 * remoteDatabasePort is found.
 * @param endPointKey
 * - key that points to the endpoint URL (this is commonly used for REST-based services such as
 * Elastic and MongoDB)
 * @param remoteServiceUrl
 * - URL of the remote endpoint (this is commonly used for REST-based * services such as Elastic and
 * MongoDB)
 * @param tunnelMethod
 * - the type of ssh method that should be used (includes not using SSH at all).
 * @param tunnelHost
 * - host name of the machine to which we will establish an ssh connection (e.g. hostname of the
 * bastion).
 * @param tunnelPort
 * - port of the machine to which we will establish an ssh connection. (e.g. port of the bastion).
 * @param tunnelUser
 * - user that is allowed to access the tunnelHost.
 * @param sshKey
 * - the ssh key that will be used to make the ssh connection. can be null if we are using
 * tunnelUserPassword instead.
 * @param tunnelUserPassword
 * - the password for the tunnelUser. can be null if we are using sshKey instead.
 * @param remoteServiceHost
 * - the actual host name of the remote service (as it is known to the tunnel host).
 * @param remoteServicePort
 * - the actual port of the remote service (as it is known to the tunnel host).
 * @param connectionOptions
 * - optional connection options for ssh client.
 */
constructor(
    val originalConfig: JsonNode,
    private val hostKey: List<String>?,
    private val portKey: List<String>?,
    private val endPointKey: String?,
    remoteServiceUrl: String?,
    tunnelMethod: TunnelMethod,
    tunnelHost: String?,
    tunnelPort: Int,
    tunnelUser: String?,
    sshKey: String?,
    tunnelUserPassword: String?,
    remoteServiceHost: String?,
    remoteServicePort: Int,
    connectionOptions: Optional<SshConnectionOptions>? = Optional.empty()
) : AutoCloseable {
    enum class TunnelMethod {
        NO_TUNNEL,
        SSH_PASSWORD_AUTH,
        SSH_KEY_AUTH
    }

    @JvmRecord
    data class SshConnectionOptions(
        val sessionHeartbeatInterval: Duration,
        val globalHeartbeatInterval: Duration,
        val idleTimeout: Duration
    )

    private val tunnelMethod: TunnelMethod
    private var tunnelHost: String? = null
    private var tunnelPort = 0
    private var tunnelUser: String? = null
    private var sshKey: String? = null
    private var remoteServiceProtocol: String? = null
    private var remoteServicePath: String? = null
    private var tunnelUserPassword: String? = null
    private var remoteServiceHost: String? = null
    private var remoteServicePort = 0
    protected var tunnelLocalPort: Int = 0

    private var sshclient: SshClient? = null
    private var tunnelSession: ClientSession? = null

    init {
        Preconditions.checkNotNull(tunnelMethod)
        this.tunnelMethod = tunnelMethod

        if (tunnelMethod == TunnelMethod.NO_TUNNEL) {
            this.tunnelHost = null
            this.tunnelPort = 0
            this.tunnelUser = null
            this.sshKey = null
            this.tunnelUserPassword = null
            this.remoteServiceHost = null
            this.remoteServicePort = 0
            this.remoteServiceProtocol = null
            this.remoteServicePath = null
        } else {
            Preconditions.checkNotNull(tunnelHost)
            Preconditions.checkArgument(tunnelPort > 0)
            Preconditions.checkNotNull(tunnelUser)
            if (tunnelMethod == TunnelMethod.SSH_KEY_AUTH) {
                Preconditions.checkNotNull(sshKey)
            }
            if (tunnelMethod == TunnelMethod.SSH_PASSWORD_AUTH) {
                Preconditions.checkNotNull(tunnelUserPassword)
            }
            // must provide either host/port or endpoint
            Preconditions.checkArgument((hostKey != null && portKey != null) || endPointKey != null)
            Preconditions.checkArgument(
                (remoteServiceHost != null && remoteServicePort > 0) || remoteServiceUrl != null
            )
            if (remoteServiceUrl != null) {
                val urlObject: URL
                try {
                    urlObject = URI(remoteServiceUrl).toURL()
                } catch (e: MalformedURLException) {
                    AirbyteTraceMessageUtility.emitConfigErrorTrace(
                        e,
                        String.format(
                            "Provided value for remote service URL is not valid: %s",
                            remoteServiceUrl
                        )
                    )
                    throw RuntimeException("Failed to parse URL of remote service")
                }
                this.remoteServiceHost = urlObject.host
                this.remoteServicePort = urlObject.port
                this.remoteServiceProtocol = urlObject.protocol
                this.remoteServicePath = urlObject.path
            } else {
                this.remoteServiceProtocol = null
                this.remoteServicePath = null
                this.remoteServiceHost = remoteServiceHost
                this.remoteServicePort = remoteServicePort
            }

            this.tunnelHost = tunnelHost
            this.tunnelPort = tunnelPort
            this.tunnelUser = tunnelUser
            this.sshKey = sshKey
            this.tunnelUserPassword = tunnelUserPassword
            this.sshclient =
                connectionOptions!!
                    .map { sshConnectionOptions: SshConnectionOptions ->
                        createClient(
                            sshConnectionOptions.sessionHeartbeatInterval,
                            sshConnectionOptions.globalHeartbeatInterval,
                            sshConnectionOptions.idleTimeout
                        )
                    }
                    .orElseGet { this.createClient() }
            this.tunnelSession = openTunnel(sshclient!!)
        }
    }

    @get:Throws(Exception::class)
    val configInTunnel: JsonNode
        get() {
            if (tunnelMethod == TunnelMethod.NO_TUNNEL) {
                return originalConfig
            } else {
                val clone = Jsons.clone(originalConfig)
                if (hostKey != null) {
                    Jsons.replaceNestedString(
                        clone,
                        hostKey,
                        SshdSocketAddress.LOCALHOST_ADDRESS.hostName
                    )
                }
                if (portKey != null) {
                    Jsons.replaceNestedInt(clone, portKey, tunnelLocalPort)
                }
                if (endPointKey != null) {
                    val tunnelEndPointURL =
                        URI(
                                remoteServiceProtocol,
                                null,
                                SshdSocketAddress.LOCALHOST_ADDRESS.hostName,
                                tunnelLocalPort,
                                remoteServicePath,
                                null,
                                null
                            )
                            .toURL()
                    Jsons.replaceNestedString(
                        clone,
                        listOf(endPointKey),
                        tunnelEndPointURL.toString()
                    )
                }
                return clone
            }
        }

    /** Closes a tunnel if one was open, and otherwise doesn't do anything (safe to run). */
    override fun close() {
        try {
            if (tunnelSession != null) {
                tunnelSession!!.close()
                tunnelSession = null
            }
            if (sshclient != null) {
                sshclient!!.stop()
                sshclient = null
            }
        } catch (t: Throwable) {
            throw RuntimeException(t)
        }
    }

    @get:Throws(IOException::class, GeneralSecurityException::class)
    val privateKeyPair: KeyPair
        /**
         * From the OPENSSH private key string, use mina-sshd to deserialize the key pair,
         * reconstruct the keys from the key info, and return the key pair for use in
         * authentication.
         *
         * @return The [KeyPair] to add - may not be `null`
         * @see [loadKeyPairs
         * ](https://javadoc.io/static/org.apache.sshd/sshd-common/2.8.0/org/apache/sshd/common/config/keys/loader/KeyPairResourceLoader.html.loadKeyPairs-org.apache.sshd.common.session.SessionContext-org.apache.sshd.common.util.io.resource.IoResource-org.apache.sshd.common.config.keys.FilePasswordProvider-)
         */
        get() {
            val validatedKey = validateKey()
            val keyPairs =
                SecurityUtils.getKeyPairResourceParser()
                    .loadKeyPairs(null, null, null, StringReader(validatedKey))

            if (keyPairs != null && keyPairs.iterator().hasNext()) {
                return keyPairs.iterator().next()
            }
            throw ConfigErrorException(
                "Unable to load private key pairs, verify key pairs are properly inputted"
            )
        }

    private fun validateKey(): String {
        return sshKey!!.replace("\\n", "\n")
    }

    /**
     * Generates a new ssh client and returns it, with forwarding set to accept all types; use this
     * before opening a tunnel.
     */
    private fun createClient(): SshClient {
        Security.addProvider(BouncyCastleProvider())
        val client = SshClient.setUpDefaultClient()
        client.forwardingFilter = AcceptAllForwardingFilter.INSTANCE
        client.serverKeyVerifier = AcceptAllServerKeyVerifier.INSTANCE
        return client
    }

    private fun createClient(
        sessionHeartbeatInterval: Duration,
        globalHeartbeatInterval: Duration,
        idleTimeout: Duration
    ): SshClient {
        LOGGER.info("Creating SSH client with Heartbeat and Keepalive enabled")
        val client = createClient()
        // Session level heartbeat using SSH_MSG_IGNORE every second.
        client.setSessionHeartbeat(
            SessionHeartbeatController.HeartbeatType.IGNORE,
            sessionHeartbeatInterval
        )
        // idle-timeout zero indicates NoTimeout.
        CoreModuleProperties.IDLE_TIMEOUT[client] = idleTimeout
        // Use tcp keep-alive mechanism.
        CoreModuleProperties.SOCKET_KEEPALIVE[client] = true
        // Additional delay used for ChannelOutputStream to wait for space in the remote socket send
        // buffer.
        CoreModuleProperties.WAIT_FOR_SPACE_TIMEOUT[client] = Duration.ofMinutes(2)
        // Global keepalive message sent every 2 seconds. This precedes the session level heartbeat.
        CoreModuleProperties.HEARTBEAT_INTERVAL[client] = globalHeartbeatInterval
        return client
    }

    /** Starts an ssh session; wrap this in a try-finally and use closeTunnel() to close it. */
    open fun openTunnel(client: SshClient): ClientSession? {
        try {
            client.start()
            val session =
                client
                    .connect(
                        tunnelUser!!.trim { it <= ' ' },
                        tunnelHost!!.trim { it <= ' ' },
                        tunnelPort
                    )
                    .verify(TIMEOUT_MILLIS.toLong())
                    .session
            if (tunnelMethod == TunnelMethod.SSH_KEY_AUTH) {
                session.addPublicKeyIdentity(privateKeyPair)
            }
            if (tunnelMethod == TunnelMethod.SSH_PASSWORD_AUTH) {
                session.addPasswordIdentity(tunnelUserPassword)
            }

            session.auth().verify(TIMEOUT_MILLIS.toLong())
            val address =
                session.startLocalPortForwarding( // entering 0 lets the OS pick a free port for us.
                    SshdSocketAddress(
                        InetSocketAddress.createUnresolved(
                            SshdSocketAddress.LOCALHOST_ADDRESS.hostName,
                            0
                        )
                    ),
                    SshdSocketAddress(remoteServiceHost, remoteServicePort)
                )

            // discover the port that the OS picked and remember it so that we can use it when we
            // try to connect
            tunnelLocalPort = address.port

            LOGGER.info(
                String.format(
                    "Established tunneling session to %s:%d. Port forwarding started on %s ",
                    remoteServiceHost,
                    remoteServicePort,
                    address.toInetSocketAddress()
                )
            )
            return session
        } catch (e: IOException) {
            if (
                e is SshException &&
                    e.message!!
                        .lowercase()
                        .contains("failed to get operation result within specified timeout")
            ) {
                throw ConfigErrorException(SSH_TIMEOUT_DISPLAY_MESSAGE, e)
            } else {
                throw RuntimeException(e)
            }
        } catch (e: GeneralSecurityException) {
            throw RuntimeException(e)
        }
    }

    override fun toString(): String {
        return "SshTunnel{" +
            "hostKey=" +
            hostKey +
            ", portKey=" +
            portKey +
            ", tunnelMethod=" +
            tunnelMethod +
            ", tunnelHost='" +
            tunnelHost +
            '\'' +
            ", tunnelPort=" +
            tunnelPort +
            ", tunnelUser='" +
            tunnelUser +
            '\'' +
            ", remoteServiceHost='" +
            remoteServiceHost +
            '\'' +
            ", remoteServicePort=" +
            remoteServicePort +
            ", tunnelLocalPort=" +
            tunnelLocalPort +
            '}'
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(SshTunnel::class.java)
        const val SSH_TIMEOUT_DISPLAY_MESSAGE: String =
            "Timed out while opening a SSH Tunnel. Please double check the given SSH configurations and try again."

        const val CONNECTION_OPTIONS_KEY: String = "ssh_connection_options"
        const val SESSION_HEARTBEAT_INTERVAL_KEY: String = "session_heartbeat_interval"
        const val SESSION_HEARTBEAT_INTERVAL_DEFAULT_IN_MILLIS: Long = 1000
        const val GLOBAL_HEARTBEAT_INTERVAL_KEY: String = "global_heartbeat_interval"
        const val GLOBAL_HEARTBEAT_INTERVAL_DEFAULT_IN_MILLIS: Long = 2000
        const val IDLE_TIMEOUT_KEY: String = "idle_timeout"
        const val IDLE_TIMEOUT_DEFAULT_INFINITE: Long = 0

        const val TIMEOUT_MILLIS: Int = 15000 // 15 seconds

        @JvmStatic
        fun getInstance(config: JsonNode, hostKey: List<String>, portKey: List<String>): SshTunnel {
            val tunnelMethod =
                Jsons.getOptional(config, "tunnel_method", "tunnel_method")
                    .map { method: JsonNode ->
                        TunnelMethod.valueOf(method.asText().trim { it <= ' ' })
                    }
                    .orElse(TunnelMethod.NO_TUNNEL)
            LOGGER.info("Starting connection with method: {}", tunnelMethod)

            return SshTunnel(
                config,
                hostKey,
                portKey,
                null,
                null,
                tunnelMethod,
                Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "tunnel_host")),
                Jsons.getIntOrZero(config, "tunnel_method", "tunnel_port"),
                Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "tunnel_user")),
                Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "ssh_key")),
                Strings.safeTrim(
                    Jsons.getStringOrNull(config, "tunnel_method", "tunnel_user_password")
                ),
                Strings.safeTrim(Jsons.getStringOrNull(config, hostKey)),
                Jsons.getIntOrZero(config, portKey),
                getSshConnectionOptions(config)
            )
        }

        private fun getSshConnectionOptions(
            config: JsonNode?
        ): @NotNull Optional<SshConnectionOptions> {
            // piggybacking on JsonNode config to make it configurable at connector level.
            val connectionOptionConfig = Jsons.getOptional(config, CONNECTION_OPTIONS_KEY)
            val connectionOptions: Optional<SshConnectionOptions>
            if (connectionOptionConfig.isPresent) {
                val connectionOptionsNode = connectionOptionConfig.get()
                val sessionHeartbeatInterval =
                    Jsons.getOptional(connectionOptionsNode, SESSION_HEARTBEAT_INTERVAL_KEY)
                        .map { interval: JsonNode -> Duration.ofMillis(interval.asLong()) }
                        .orElse(Duration.ofSeconds(1))
                val globalHeartbeatInterval =
                    Jsons.getOptional(connectionOptionsNode, GLOBAL_HEARTBEAT_INTERVAL_KEY)
                        .map { interval: JsonNode -> Duration.ofMillis(interval.asLong()) }
                        .orElse(Duration.ofSeconds(2))
                val idleTimeout =
                    Jsons.getOptional(connectionOptionsNode, IDLE_TIMEOUT_KEY)
                        .map { interval: JsonNode -> Duration.ofMillis(interval.asLong()) }
                        .orElse(Duration.ZERO)
                connectionOptions =
                    Optional.of(
                        SshConnectionOptions(
                            sessionHeartbeatInterval,
                            globalHeartbeatInterval,
                            idleTimeout
                        )
                    )
            } else {
                connectionOptions = Optional.empty()
            }
            return connectionOptions
        }

        @Throws(Exception::class)
        fun getInstance(config: JsonNode, endPointKey: String): SshTunnel {
            val tunnelMethod =
                Jsons.getOptional(config, "tunnel_method", "tunnel_method")
                    .map { method: JsonNode ->
                        TunnelMethod.valueOf(method.asText().trim { it <= ' ' })
                    }
                    .orElse(TunnelMethod.NO_TUNNEL)
            LOGGER.info("Starting connection with method: {}", tunnelMethod)

            return SshTunnel(
                config,
                null,
                null,
                endPointKey,
                Jsons.getStringOrNull(config, endPointKey),
                tunnelMethod,
                Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "tunnel_host")),
                Jsons.getIntOrZero(config, "tunnel_method", "tunnel_port"),
                Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "tunnel_user")),
                Strings.safeTrim(Jsons.getStringOrNull(config, "tunnel_method", "ssh_key")),
                Strings.safeTrim(
                    Jsons.getStringOrNull(config, "tunnel_method", "tunnel_user_password")
                ),
                null,
                0,
                getSshConnectionOptions(config)
            )
        }

        @JvmStatic
        @Throws(Exception::class)
        fun sshWrap(
            config: JsonNode,
            hostKey: List<String>,
            portKey: List<String>,
            wrapped: CheckedConsumer<JsonNode?, Exception?>
        ) {
            sshWrap<Any?>(config, hostKey, portKey) { configInTunnel: JsonNode ->
                wrapped.accept(configInTunnel)
                null
            }
        }

        @JvmStatic
        @Throws(Exception::class)
        fun sshWrap(
            config: JsonNode,
            endPointKey: String,
            wrapped: CheckedConsumer<JsonNode?, Exception?>
        ) {
            sshWrap<Any?>(config, endPointKey) { configInTunnel: JsonNode ->
                wrapped.accept(configInTunnel)
                null
            }
        }

        @JvmStatic
        @Throws(Exception::class)
        fun <T> sshWrap(
            config: JsonNode,
            hostKey: List<String>,
            portKey: List<String>,
            wrapped: CheckedFunction<JsonNode, T, Exception?>
        ): T {
            getInstance(config, hostKey, portKey).use { sshTunnel ->
                return wrapped.apply(sshTunnel.configInTunnel)
            }
        }

        @JvmStatic
        @Throws(Exception::class)
        fun <T> sshWrap(
            config: JsonNode,
            endPointKey: String,
            wrapped: CheckedFunction<JsonNode, T, Exception?>
        ): T {
            getInstance(config, endPointKey).use { sshTunnel ->
                return wrapped.apply(sshTunnel.configInTunnel)
            }
        }
    }
}
