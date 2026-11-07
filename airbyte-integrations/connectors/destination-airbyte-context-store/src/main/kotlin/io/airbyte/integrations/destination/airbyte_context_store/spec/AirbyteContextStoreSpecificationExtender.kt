/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.airbyte_context_store.spec

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.spec.DestinationSpecificationExtender
import io.airbyte.cdk.spec.SpecificationExtender
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/**
 * Publishes a spec that contains the managed storage acknowledgement and nothing else. The storage,
 * catalog and credential properties of [AirbyteContextStoreSpecification] are supplied by Airbyte
 * at runtime, so they must not be part of the customer-facing spec.
 */
@Singleton
@Replaces(DestinationSpecificationExtender::class)
@Requires(env = ["destination"])
class AirbyteContextStoreSpecificationExtender : SpecificationExtender {
    override fun invoke(specification: ConnectorSpecification): ConnectorSpecification {
        val schema = specification.connectionSpecification as ObjectNode
        val acknowledgement =
            schema.get("properties")?.get(ACKNOWLEDGE_MANAGED_STORAGE_PROPERTY)
                ?: throw IllegalStateException(
                    "Spec is missing the $ACKNOWLEDGE_MANAGED_STORAGE_PROPERTY property."
                )

        schema.set<ObjectNode>(
            "properties",
            Jsons.objectNode().apply {
                set<JsonNode>(ACKNOWLEDGE_MANAGED_STORAGE_PROPERTY, acknowledgement)
            }
        )
        schema.put(
            "description",
            "Airbyte fully manages the storage backing this destination. There is nothing to configure."
        )
        schema.set<ObjectNode>(
            "required",
            Jsons.arrayNode().apply { add(ACKNOWLEDGE_MANAGED_STORAGE_PROPERTY) }
        )

        return specification
            .withConnectionSpecification(schema)
            .withSupportedDestinationSyncModes(
                listOf(
                    DestinationSyncMode.OVERWRITE,
                    DestinationSyncMode.APPEND,
                    DestinationSyncMode.APPEND_DEDUP,
                )
            )
            .withSupportsIncremental(true)
    }
}
