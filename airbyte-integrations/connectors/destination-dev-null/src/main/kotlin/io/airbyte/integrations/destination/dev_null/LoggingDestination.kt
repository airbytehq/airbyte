/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.integrations.destination.dev_null.logging.LoggingConsumer
import io.airbyte.integrations.destination.dev_null.logging.TestingLoggerFactory
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.util.function.Consumer
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/** This destination logs each record it receives. */
class LoggingDestination : BaseConnector(), Destination {
    override fun check(config: JsonNode): AirbyteConnectionStatus {
        return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
    }

    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer {
        return LoggingConsumer(TestingLoggerFactory(config), catalog, outputRecordCollector)
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(LoggingDestination::class.java)
    }
}
