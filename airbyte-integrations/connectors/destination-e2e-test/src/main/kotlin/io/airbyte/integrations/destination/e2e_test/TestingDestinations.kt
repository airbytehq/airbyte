/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.e2e_test

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.util.function.Consumer
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class TestingDestinations
@JvmOverloads
constructor(
    private val destinationMap: Map<TestDestinationType, Destination> =
        ImmutableMap.builder<TestDestinationType, Destination>()
            .put(TestDestinationType.LOGGING, LoggingDestination())
            .put(TestDestinationType.THROTTLED, ThrottledDestination())
            .put(TestDestinationType.SILENT, SilentDestination())
            .put(TestDestinationType.FAILING, FailAfterNDestination())
            .build()
) : BaseConnector(), Destination {
    enum class TestDestinationType {
        LOGGING,
        THROTTLED,
        SILENT,
        FAILING
    }

    private fun selectDestination(config: JsonNode): Destination? {
        return destinationMap[
            TestDestinationType.valueOf(
                config["test_destination"]["test_destination_type"].asText()
            )
        ]
    }

    @Throws(Exception::class)
    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer {
        return selectDestination(config)!!.getConsumer(config, catalog, outputRecordCollector)
    }

    @Throws(Exception::class)
    override fun check(config: JsonNode): AirbyteConnectionStatus {
        return try {
            selectDestination(config)!!.check(config)
        } catch (e: Exception) {
            AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(e.message)
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(TestingDestinations::class.java)

        @Throws(Exception::class)
        @JvmStatic
        fun main(args: Array<String>) {
            val destination: Destination = TestingDestinations()
            LOGGER.info("starting destination: {}", TestingDestinations::class.java)
            IntegrationRunner(destination).run(args)
            LOGGER.info("completed destination: {}", TestingDestinations::class.java)
        }
    }
}
