/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import io.github.oshai.kotlinlogging.KotlinLogging

private val LOGGER = KotlinLogging.logger {}
/** Singleton of destination config for easy lookup of values. */
class DestinationConfig private constructor() {
    // whether the destination fully supports Destinations V2
    var isV2Destination: Boolean = false
        private set

    @VisibleForTesting var root: JsonNode? = null

    fun getNodeValue(key: String?): JsonNode? {
        val node = config!!.root!![key]
        if (node == null) {
            LOGGER.debug { "Cannot find node with key $key" }
        }
        return node
    }

    // string value, otherwise empty string
    fun getTextValue(key: String?): String {
        val node = getNodeValue(key)
        if (node == null || !node.isTextual) {
            LOGGER.debug { "Cannot retrieve text value for node with key $key" }
            return ""
        }
        return node.asText()
    }

    // boolean value, otherwise false
    fun getBooleanValue(key: String?): Boolean {
        val node = getNodeValue(key)
        if (node == null || !node.isBoolean) {
            LOGGER.debug { "Cannot retrieve boolean value for node with key $key" }
            return false
        }
        return node.asBoolean()
    }

    companion object {

        private var config: DestinationConfig? = null

        @JvmStatic
        @VisibleForTesting
        fun initialize(root: JsonNode?) {
            initialize(root, false)
        }

        fun initialize(root: JsonNode?, isV2Destination: Boolean) {
            if (config == null) {
                requireNotNull(root) { "Cannot create DestinationConfig from null." }
                config = DestinationConfig()
                config!!.root = root
                config!!.isV2Destination = isV2Destination
            } else {
                LOGGER.warn { "Singleton was already initialized." }
            }
        }

        @JvmStatic
        val instance: DestinationConfig?
            get() {
                checkNotNull(config) { "Singleton not initialized." }
                return config
            }

        @JvmStatic
        @VisibleForTesting
        fun clearInstance() {
            config = null
        }
    }
}
