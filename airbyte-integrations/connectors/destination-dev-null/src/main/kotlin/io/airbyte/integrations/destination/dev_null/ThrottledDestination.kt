/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.util.function.Consumer
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * This destination logs each record it receives. It sleeps for millis_per_record between accepting
 * each record. Useful for simulating backpressure / slow destination writes.
 */
class ThrottledDestination() : BaseConnector(), Destination {
    override fun check(config: JsonNode): AirbyteConnectionStatus {
        return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
    }

    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer {
        return ThrottledConsumer(
            config["test_destination"]["millis_per_record"].asLong(),
            outputRecordCollector
        )
    }

    class ThrottledConsumer(
        private val millisPerRecord: Long,
        private val outputRecordCollector: Consumer<AirbyteMessage>
    ) : AirbyteMessageConsumer {
        init {
            LOGGER.info("Will sleep {} millis before processing every record", millisPerRecord)
        }

        override fun start() {}

        @Throws(Exception::class)
        override fun accept(message: AirbyteMessage) {
            Thread.sleep(millisPerRecord)

            if (message.type == AirbyteMessage.Type.STATE) {
                LOGGER.info("Emitting state: {}", message)
                outputRecordCollector.accept(message)
            }
        }

        override fun close() {}
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(ThrottledDestination::class.java)
    }
}
