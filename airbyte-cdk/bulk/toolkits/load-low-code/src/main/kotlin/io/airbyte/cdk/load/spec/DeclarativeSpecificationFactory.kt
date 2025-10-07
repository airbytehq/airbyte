/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.spec

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.dlq.ObjectStorageSpec
import io.airbyte.cdk.load.model.spec.Spec
import io.airbyte.cdk.spec.SpecificationFactory
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.protocol.models.v0.DestinationSyncMode

class DeclarativeSpecificationFactory(private val declarativeSpec: Spec) : SpecificationFactory {
    override fun create(): ConnectorSpecification {
        val connectionSpecificationCopy: ObjectNode =
            declarativeSpec.connectionSpecification.deepCopy()
        appendObjectStorageConfig(connectionSpecificationCopy)

        val spec =
            ConnectorSpecification()
                .withConnectionSpecification(connectionSpecificationCopy)
                // FIXME do we really need the following. I added those for backward compabitility
                // with destination-customer-io
                .withSupportsIncremental(true)
                .withSupportedDestinationSyncModes(listOf(DestinationSyncMode.APPEND))

        if (declarativeSpec.advancedAuth != null) {
            spec.withAdvancedAuth(declarativeSpec.advancedAuth)
        }

        return spec
    }

    private fun appendObjectStorageConfig(connectionSpecificationCopy: ObjectNode) {
        (connectionSpecificationCopy.get("properties") as ObjectNode).replace(
            "object_storage_config",
            ValidatedJsonUtils.generateAirbyteJsonSchema(ObjectStorageSpec::class.java),
        )
        (connectionSpecificationCopy.get("properties").get("object_storage_config") as ObjectNode)
            .remove("\$schema")
    }
}
