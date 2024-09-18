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

class FailAfterNDestination : BaseConnector(), Destination {
    override fun check(config: JsonNode): AirbyteConnectionStatus {
        return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
    }

    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer {
        return FailAfterNConsumer(
            config["test_destination"]["num_messages"].asLong(),
            outputRecordCollector
        )
    }

    class FailAfterNConsumer(
        private val numMessagesAfterWhichToFail: Long,
        private val outputRecordCollector: Consumer<AirbyteMessage>
    ) : AirbyteMessageConsumer {
        private var numMessagesSoFar: Long = 0

        init {
            LOGGER.info("Will fail after {} messages", numMessagesAfterWhichToFail)
        }

        override fun start() {}

        override fun accept(message: AirbyteMessage) {
            numMessagesSoFar += 1

            check(numMessagesSoFar <= numMessagesAfterWhichToFail) {
                "Forcing a fail after processing $numMessagesAfterWhichToFail messages."
            }

            if (message.type == AirbyteMessage.Type.STATE) {
                LOGGER.info("Emitting state: {}", message)
                outputRecordCollector.accept(message)
            }
        }

        override fun close() {}
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(FailAfterNDestination::class.java)
    }
}
