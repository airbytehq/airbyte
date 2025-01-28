/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.output

import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteLogMessage
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

/** [OutputConsumer] implementation for unit tests. Collects everything into thread-safe buffers. */
@Singleton
@Requires(notEnv = [Environment.CLI])
@Replaces(OutputConsumer::class)
class BufferingOutputConsumer(
    clock: Clock,
) : OutputConsumer(clock) {

    private val records = mutableListOf<AirbyteRecordMessage>()
    private val states = mutableListOf<AirbyteStateMessage>()
    private val logs = mutableListOf<AirbyteLogMessage>()
    private val specs = mutableListOf<ConnectorSpecification>()
    private val statuses = mutableListOf<AirbyteConnectionStatus>()
    private val catalogs = mutableListOf<AirbyteCatalog>()
    private val traces = mutableListOf<AirbyteTraceMessage>()
    private val messages = mutableListOf<AirbyteMessage>()
    private var messagesIndex: Int = 0

    var callback: (AirbyteMessage) -> Unit = {}
        set(value) {
            synchronized(this) { field = value }
        }

    override fun accept(input: AirbyteMessage) {
        // Deep copy the input, which may be reused and mutated later on.
        val m: AirbyteMessage =
            Jsons.readValue(Jsons.writeValueAsBytes(input), AirbyteMessage::class.java)
        synchronized(this) {
            messages.add(m)
            when (m.type) {
                AirbyteMessage.Type.RECORD -> records.add(m.record)
                AirbyteMessage.Type.STATE -> states.add(m.state)
                AirbyteMessage.Type.LOG -> logs.add(m.log)
                AirbyteMessage.Type.SPEC -> specs.add(m.spec)
                AirbyteMessage.Type.CONNECTION_STATUS -> statuses.add(m.connectionStatus)
                AirbyteMessage.Type.CATALOG -> catalogs.add(m.catalog)
                AirbyteMessage.Type.TRACE -> traces.add(m.trace)
                else -> TODO("${m.type} not supported")
            }
            callback(m)
        }
    }

    override fun close() {}

    fun records(): List<AirbyteRecordMessage> =
        synchronized(this) { listOf(*records.toTypedArray()) }

    fun states(): List<AirbyteStateMessage> = synchronized(this) { listOf(*states.toTypedArray()) }

    fun logs(): List<AirbyteLogMessage> = synchronized(this) { listOf(*logs.toTypedArray()) }

    fun specs(): List<ConnectorSpecification> = synchronized(this) { listOf(*specs.toTypedArray()) }

    fun statuses(): List<AirbyteConnectionStatus> =
        synchronized(this) { listOf(*statuses.toTypedArray()) }

    fun catalogs(): List<AirbyteCatalog> = synchronized(this) { listOf(*catalogs.toTypedArray()) }

    fun traces(): List<AirbyteTraceMessage> = synchronized(this) { listOf(*traces.toTypedArray()) }

    fun messages(): List<AirbyteMessage> = synchronized(this) { listOf(*messages.toTypedArray()) }

    fun newMessages(): List<AirbyteMessage> =
        synchronized(this) {
            val newMessages = messages.subList(messagesIndex, messages.size)
            messagesIndex = messages.size
            newMessages
        }

    fun resetNewMessagesCursor() {
        synchronized(this) { messagesIndex = 0 }
    }
}
