/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null.logging

import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.util.function.Consumer
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class LoggingConsumer(
    private val loggerFactory: TestingLoggerFactory,
    private val configuredCatalog: ConfiguredAirbyteCatalog,
    private val outputRecordCollector: Consumer<AirbyteMessage>
) : AirbyteMessageConsumer {
    private val loggers: MutableMap<AirbyteStreamNameNamespacePair, TestingLogger?> = HashMap()

    override fun start() {
        for (configuredStream in configuredCatalog.streams) {
            val stream = configuredStream.stream
            val streamNamePair = AirbyteStreamNameNamespacePair.fromAirbyteStream(stream)
            val logger = loggerFactory.create(streamNamePair)
            loggers[streamNamePair] = logger
        }
    }

    override fun accept(message: AirbyteMessage) {
        if (message.type == AirbyteMessage.Type.STATE) {
            LOGGER.info("Emitting state: {}", message)
            outputRecordCollector.accept(message)
        } else if (message.type == AirbyteMessage.Type.TRACE) {
            LOGGER.info("Received a trace: {}", message)
        } else if (message.type == AirbyteMessage.Type.RECORD) {
            val recordMessage = message.record
            val pair = AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage)

            require(loggers.containsKey(pair)) {
                String.format(
                    "Message contained record from a stream that was not in the catalog.\n  Catalog: %s\n  Message: %s",
                    Jsons.serialize(configuredCatalog),
                    Jsons.serialize(recordMessage)
                )
            }

            loggers[pair]!!.log(recordMessage)
        }
    }

    override fun close() {}

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(LoggingConsumer::class.java)
    }
}
