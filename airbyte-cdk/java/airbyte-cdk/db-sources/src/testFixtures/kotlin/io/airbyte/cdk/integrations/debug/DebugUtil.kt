/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debug

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.base.Source
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog

/**
 * Utility class defined to debug a source. Copy over any relevant configurations, catalogs & state
 * in the resources/debug_resources directory.
 */
object DebugUtil {
    @Suppress("deprecation")
    @Throws(Exception::class)
    @JvmStatic
    fun debug(debugSource: Source) {
        val debugConfig = config
        val configuredAirbyteCatalog = catalog
        var state =
            try {
                state
            } catch (e: Exception) {
                null
            }

        debugSource.check(debugConfig)
        debugSource.discover(debugConfig)

        val messageIterator = debugSource.read(debugConfig, configuredAirbyteCatalog, state)
        messageIterator.forEachRemaining { message: AirbyteMessage -> }
    }

    @get:Throws(Exception::class)
    private val config: JsonNode
        get() {
            val originalConfig =
                ObjectMapper().readTree(MoreResources.readResource("debug_resources/config.json"))
            val debugConfig: JsonNode =
                (originalConfig.deepCopy<JsonNode>() as ObjectNode).put("debug_mode", true)
            return debugConfig
        }

    @get:Throws(Exception::class)
    private val catalog: ConfiguredAirbyteCatalog
        get() {
            val catalog = MoreResources.readResource("debug_resources/configured_catalog.json")
            return Jsons.deserialize(catalog, ConfiguredAirbyteCatalog::class.java)
        }

    @get:Throws(Exception::class)
    private val state: JsonNode
        get() {
            val message =
                Jsons.deserialize(
                    MoreResources.readResource("debug_resources/state.json"),
                    AirbyteStateMessage::class.java
                )
            return Jsons.jsonNode(listOf(message))
        }
}
