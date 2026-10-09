/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.airbyte_context_store.spec

import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.protocol.models.v0.DestinationSyncMode
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class AirbyteContextStoreSpecificationExtenderTest {
    private val extender = AirbyteContextStoreSpecificationExtender()

    private fun schemaOf(vararg propertyNames: String) =
        Jsons.objectNode().apply {
            set<com.fasterxml.jackson.databind.JsonNode>(
                "properties",
                Jsons.objectNode().apply {
                    propertyNames.forEach { name ->
                        set<com.fasterxml.jackson.databind.JsonNode>(
                            name,
                            Jsons.objectNode().put("type", "string")
                        )
                    }
                }
            )
            set<com.fasterxml.jackson.databind.JsonNode>(
                "required",
                Jsons.arrayNode().apply { propertyNames.forEach { add(it) } }
            )
        }

    @Test
    fun `publishes only the managed storage acknowledgement`() {
        val spec =
            extender(
                ConnectorSpecification()
                    .withConnectionSpecification(
                        schemaOf(
                            ACKNOWLEDGE_MANAGED_STORAGE_PROPERTY,
                            "access_key_id",
                            "secret_access_key",
                            "s3_bucket_name",
                            "warehouse_location",
                            "catalog_type",
                        )
                    )
            )

        val properties = spec.connectionSpecification.get("properties")
        assertEquals(1, properties.size())
        assertTrue(properties.has(ACKNOWLEDGE_MANAGED_STORAGE_PROPERTY))
        assertEquals(
            listOf(ACKNOWLEDGE_MANAGED_STORAGE_PROPERTY),
            spec.connectionSpecification.get("required").map { it.asText() }
        )
    }

    @Test
    fun `advertises the sync modes of the underlying data lake destination`() {
        val spec =
            extender(
                ConnectorSpecification()
                    .withConnectionSpecification(schemaOf(ACKNOWLEDGE_MANAGED_STORAGE_PROPERTY))
            )

        assertEquals(
            listOf(
                DestinationSyncMode.OVERWRITE,
                DestinationSyncMode.APPEND,
                DestinationSyncMode.APPEND_DEDUP,
            ),
            spec.supportedDestinationSyncModes
        )
        assertTrue(spec.supportsIncremental)
    }

    @Test
    fun `fails when the acknowledgement property is missing`() {
        assertThrows(IllegalStateException::class.java) {
            extender(
                ConnectorSpecification().withConnectionSpecification(schemaOf("s3_bucket_name"))
            )
        }
    }
}
