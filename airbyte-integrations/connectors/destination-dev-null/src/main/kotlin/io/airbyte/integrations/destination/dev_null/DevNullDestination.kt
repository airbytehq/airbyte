/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null

import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.spec_modification.SpecModifyingDestination
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.destination.e2e_test.TestingDestinations
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class DevNullDestination : SpecModifyingDestination(TestingDestinations()), Destination {
    /** 1. Update the title. 2. Only keep the "silent" mode. */
    override fun modifySpec(originalSpec: ConnectorSpecification): ConnectorSpecification {
        val spec = Jsons.clone(originalSpec)

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

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(DevNullDestination::class.java)
        private const val DEV_NULL_DESTINATION_TITLE = "E2E Test (/dev/null) Destination Spec"

        @Throws(Exception::class)
        @JvmStatic
        fun main(args: Array<String>) {
            LOGGER.info("Starting destination: {}", DevNullDestination::class.java)
            IntegrationRunner(DevNullDestination()).run(args)
            LOGGER.info("Completed destination: {}", DevNullDestination::class.java)
        }
    }
}
