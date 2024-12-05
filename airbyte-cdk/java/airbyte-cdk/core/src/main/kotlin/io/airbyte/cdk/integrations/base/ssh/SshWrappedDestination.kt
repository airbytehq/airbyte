/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base.ssh

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.commons.concurrency.VoidCallable
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.function.Consumer

private val LOGGER = KotlinLogging.logger {}
/**
 * Decorates a Destination with an SSH Tunnel using the standard configuration that Airbyte uses for
 * configuring SSH.
 */
class SshWrappedDestination : Destination {
    private val delegate: Destination
    private val hostKey: List<String>?
    private val portKey: List<String>?
    private val endPointKey: String?

    constructor(delegate: Destination, hostKey: List<String>, portKey: List<String>) {
        this.delegate = delegate
        this.hostKey = hostKey
        this.portKey = portKey
        this.endPointKey = null
    }

    constructor(delegate: Destination, endPointKey: String) {
        this.delegate = delegate
        this.endPointKey = endPointKey
        this.portKey = null
        this.hostKey = null
    }

    @Throws(Exception::class)
    override fun spec(): ConnectorSpecification {
        // inject the standard ssh configuration into the spec.
        val originalSpec = delegate.spec()
        val propNode = originalSpec.connectionSpecification["properties"] as ObjectNode
        propNode.set<JsonNode>(
            "tunnel_method",
            Jsons.deserialize(MoreResources.readResource("ssh-tunnel-spec.json"))
        )
        return originalSpec
    }

    @Throws(Exception::class)
    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        try {
            return if ((endPointKey != null))
                SshTunnel.sshWrap(config, endPointKey) { c: JsonNode -> delegate.check(c) }
            else
                SshTunnel.sshWrap(config, hostKey!!, portKey!!) { c: JsonNode -> delegate.check(c) }
        } catch (e: RuntimeException) {
            val sshErrorMessage =
                "Could not connect with provided SSH configuration. Error: " + e.message
            AirbyteTraceMessageUtility.emitConfigErrorTrace(e, sshErrorMessage)
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(sshErrorMessage)
        }
    }

    @Throws(Exception::class)
    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        val tunnel = getTunnelInstance(config)

        val delegateConsumer: AirbyteMessageConsumer?
        try {
            delegateConsumer =
                delegate.getConsumer(tunnel.configInTunnel, catalog, outputRecordCollector)
        } catch (e: Exception) {
            LOGGER.error(e) {
                "Exception occurred while getting the delegate consumer, closing SSH tunnel"
            }
            tunnel.close()
            throw e
        }
        return AirbyteMessageConsumer.Companion.appendOnClose(
            delegateConsumer,
            VoidCallable { tunnel.close() }
        )
    }

    @Throws(Exception::class)
    override fun getSerializedMessageConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): SerializedAirbyteMessageConsumer? {
        val clone = Jsons.clone(config)
        val connectionOptionsConfig: Optional<JsonNode> =
            Jsons.getOptional(clone, SshTunnel.Companion.CONNECTION_OPTIONS_KEY)
        if (connectionOptionsConfig.isEmpty) {
            LOGGER.info { "No SSH connection options found, using defaults" }
            if (clone is ObjectNode) { // Defensive check, it will always be object node
                val connectionOptions = clone.putObject(SshTunnel.Companion.CONNECTION_OPTIONS_KEY)
                connectionOptions.put(
                    SshTunnel.Companion.SESSION_HEARTBEAT_INTERVAL_KEY,
                    SshTunnel.Companion.SESSION_HEARTBEAT_INTERVAL_DEFAULT_IN_MILLIS
                )
                connectionOptions.put(
                    SshTunnel.Companion.GLOBAL_HEARTBEAT_INTERVAL_KEY,
                    SshTunnel.Companion.GLOBAL_HEARTBEAT_INTERVAL_DEFAULT_IN_MILLIS
                )
            }
        }
        val tunnel = getTunnelInstance(clone)
        val delegateConsumer: SerializedAirbyteMessageConsumer?
        try {
            delegateConsumer =
                delegate.getSerializedMessageConsumer(
                    tunnel.configInTunnel,
                    catalog,
                    outputRecordCollector
                )
        } catch (e: Exception) {
            LOGGER.error(e) {
                "Exception occurred while getting the delegate consumer, closing SSH tunnel"
            }
            tunnel.close()
            throw e
        }
        return SerializedAirbyteMessageConsumer.Companion.appendOnClose(
            delegateConsumer,
            VoidCallable { tunnel.close() }
        )
    }

    @Throws(Exception::class)
    protected fun getTunnelInstance(config: JsonNode): SshTunnel {
        return if ((endPointKey != null)) SshTunnel.Companion.getInstance(config, endPointKey)
        else SshTunnel.Companion.getInstance(config, hostKey!!, portKey!!)
    }

    override val isV2Destination: Boolean
        get() = delegate.isV2Destination

    companion object {}
}
