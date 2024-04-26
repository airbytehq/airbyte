/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.consumers

import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.time.Clock
import java.time.Instant

/** [OutputConsumer] implementation for unit tests. Collects everything into thread-safe buffers. */
@Singleton
@Requires(notEnv = [Environment.CLI])
@Replaces(OutputConsumer::class)
class BufferingOutputConsumer(clock: Clock) : OutputConsumer {

    override val emittedAt: Instant = Instant.now(clock)

    private val records = mutableListOf<AirbyteRecordMessage>()
    private val states = mutableListOf<AirbyteStateMessage>()
    private val specs = mutableListOf<ConnectorSpecification>()
    private val statuses = mutableListOf<AirbyteConnectionStatus>()
    private val catalogs = mutableListOf<AirbyteCatalog>()
    private val traces = mutableListOf<AirbyteTraceMessage>()

    override fun accept(m: AirbyteMessage) {
        synchronized(this) {
            when (m.type) {
                AirbyteMessage.Type.RECORD -> records.add(m.record)
                AirbyteMessage.Type.STATE -> states.add(m.state)
                AirbyteMessage.Type.SPEC -> specs.add(m.spec)
                AirbyteMessage.Type.CONNECTION_STATUS -> statuses.add(m.connectionStatus)
                AirbyteMessage.Type.CATALOG -> catalogs.add(m.catalog)
                AirbyteMessage.Type.TRACE -> traces.add(m.trace)
                else -> TODO("${m.type} not supported")
            }
        }
    }

    fun records(): List<AirbyteRecordMessage> =
        synchronized(this) { listOf(*records.toTypedArray()) }

    fun states(): List<AirbyteStateMessage> = synchronized(this) { listOf(*states.toTypedArray()) }

    fun specs(): List<ConnectorSpecification> = synchronized(this) { listOf(*specs.toTypedArray()) }

    fun statuses(): List<AirbyteConnectionStatus> =
        synchronized(this) { listOf(*statuses.toTypedArray()) }

    fun catalogs(): List<AirbyteCatalog> = synchronized(this) { listOf(*catalogs.toTypedArray()) }

    fun traces(): List<AirbyteTraceMessage> = synchronized(this) { listOf(*traces.toTypedArray()) }
}
