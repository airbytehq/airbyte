/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.features.FeatureFlags
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConnectorSpecification
import java.util.function.Consumer
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class TestingDestinations
@JvmOverloads
constructor(
    override val featureFlags: FeatureFlags = EnvVariableFeatureFlags(),
    private val destinationMap: Map<TestDestinationType, Destination> =
        ImmutableMap.builder<TestDestinationType, Destination>()
            .put(TestDestinationType.LOGGING, LoggingDestination())
            .put(TestDestinationType.THROTTLED, ThrottledDestination())
            .put(TestDestinationType.SILENT, SilentDestination())
            .put(TestDestinationType.FAILING, FailAfterNDestination())
            .build(),
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

    override fun spec(): ConnectorSpecification {
        if (!isCloudDeployment) {
            return super.spec()
        } else {
            /** 1. Update the title. 2. Only keep the "silent" mode. */
            val spec = super.spec()

            (spec.connectionSpecification as ObjectNode).put("title", DEV_NULL_DESTINATION_TITLE)

            val properties =
                spec.connectionSpecification["properties"]["test_destination"] as ObjectNode
            val types = properties["oneOf"] as ArrayNode
            val typesIterator = types.elements()
            while (typesIterator.hasNext()) {
                val typeNode = typesIterator.next()
                if (
                    !typeNode["properties"]["test_destination_type"]["const"]
                        .asText()
                        .equals("silent", ignoreCase = true)
                ) {
                    typesIterator.remove()
                }
            }
            return spec
        }
    }

    @Throws(Exception::class)
    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        return selectDestination(config)!!.getConsumer(config, catalog, outputRecordCollector)
    }

    @Throws(Exception::class)
    override fun check(config: JsonNode): AirbyteConnectionStatus? {
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
        private const val DEV_NULL_DESTINATION_TITLE = "E2E Test (/dev/null) Destination Spec"

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
