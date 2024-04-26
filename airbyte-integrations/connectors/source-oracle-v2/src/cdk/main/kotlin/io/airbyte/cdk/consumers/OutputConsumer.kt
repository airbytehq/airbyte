/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.consumers

import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.micronaut.context.annotation.DefaultImplementation
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.time.Instant
import java.util.function.Consumer

/** Emits the [AirbyteMessage] instances produced by the connector. */
@DefaultImplementation(StdoutOutputConsumer::class)
interface OutputConsumer : Consumer<AirbyteMessage> {

    val emittedAt: Instant

    fun accept(record: AirbyteRecordMessage) {
        record.emittedAt = emittedAt.toEpochMilli()
        accept(AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(record))
    }

    fun accept(state: AirbyteStateMessage) {
        accept(AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(state))
    }

    fun accept(spec: ConnectorSpecification) {
        accept(AirbyteMessage().withType(AirbyteMessage.Type.SPEC).withSpec(spec))
    }

    fun accept(status: AirbyteConnectionStatus) {
        accept(
            AirbyteMessage()
                .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                .withConnectionStatus(status)
        )
    }

    fun accept(catalog: AirbyteCatalog) {
        accept(AirbyteMessage().withType(AirbyteMessage.Type.CATALOG).withCatalog(catalog))
    }

    fun accept(trace: AirbyteTraceMessage) {
        accept(AirbyteMessage().withType(AirbyteMessage.Type.TRACE).withTrace(trace))
    }
}

// Used for integration tests.
const val CONNECTOR_OUTPUT_FILE = "airbyte.connector.output.file"

/** Default implementation of [OutputConsumer]. */
@Singleton
@Secondary
private class StdoutOutputConsumer : OutputConsumer {

    override val emittedAt: Instant = Instant.now()

    override fun accept(airbyteMessage: AirbyteMessage) {
        val json: String = Jsons.serialize(airbyteMessage)
        synchronized(this) { println(json) }
    }
}
