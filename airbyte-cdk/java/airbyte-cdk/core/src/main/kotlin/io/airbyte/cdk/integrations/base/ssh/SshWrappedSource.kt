/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base.ssh

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.cdk.integrations.base.Source
import io.airbyte.commons.functional.CheckedFunction
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.commons.util.AutoCloseableIterators
import io.airbyte.protocol.models.v0.*
import java.util.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class SshWrappedSource : Source {
    private val delegate: Source
    private val hostKey: List<String>
    private val portKey: List<String>
    private val sshGroup: Optional<String>

    constructor(delegate: Source, hostKey: List<String>, portKey: List<String>) {
        this.delegate = delegate
        this.hostKey = hostKey
        this.portKey = portKey
        this.sshGroup = Optional.empty()
    }

    constructor(delegate: Source, hostKey: List<String>, portKey: List<String>, sshGroup: String) {
        this.delegate = delegate
        this.hostKey = hostKey
        this.portKey = portKey
        this.sshGroup = Optional.of(sshGroup)
    }

    @Throws(Exception::class)
    override fun spec(): ConnectorSpecification {
        return SshHelpers.injectSshIntoSpec(delegate.spec(), sshGroup)
    }

    @Throws(Exception::class)
    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        try {
            return SshTunnel.Companion.sshWrap<AirbyteConnectionStatus?>(
                config,
                hostKey,
                portKey,
                CheckedFunction<JsonNode, AirbyteConnectionStatus?, Exception?> { config: JsonNode
                    ->
                    delegate.check(config)
                }
            )
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
    override fun discover(config: JsonNode): AirbyteCatalog {
        return SshTunnel.Companion.sshWrap<AirbyteCatalog>(
            config,
            hostKey,
            portKey,
            CheckedFunction<JsonNode, AirbyteCatalog, Exception?> { config: JsonNode ->
                delegate.discover(config)
            }
        )
    }

    @Throws(Exception::class)
    override fun read(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        state: JsonNode?
    ): AutoCloseableIterator<AirbyteMessage> {
        val tunnel: SshTunnel = SshTunnel.Companion.getInstance(config, hostKey, portKey)
        val delegateRead: AutoCloseableIterator<AirbyteMessage>
        try {
            delegateRead = delegate.read(tunnel.configInTunnel, catalog, state)
        } catch (e: Exception) {
            LOGGER.error(
                "Exception occurred while getting the delegate read iterator, closing SSH tunnel",
                e
            )
            tunnel.close()
            throw e
        }
        return AutoCloseableIterators.appendOnClose(delegateRead) { tunnel.close() }
    }

    @Throws(Exception::class)
    override fun readStreams(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        state: JsonNode?
    ): Collection<AutoCloseableIterator<AirbyteMessage>>? {
        val tunnel: SshTunnel = SshTunnel.Companion.getInstance(config, hostKey, portKey)
        try {
            return delegate.readStreams(tunnel.configInTunnel, catalog, state)
        } catch (e: Exception) {
            LOGGER.error(
                "Exception occurred while getting the delegate read stream iterators, closing SSH tunnel",
                e
            )
            tunnel.close()
            throw e
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(SshWrappedSource::class.java)
    }
}
