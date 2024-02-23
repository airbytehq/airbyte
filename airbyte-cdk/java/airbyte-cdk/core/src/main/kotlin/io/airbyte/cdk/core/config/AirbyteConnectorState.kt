/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.config

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import io.micronaut.context.annotation.ConfigurationProperties

/**
 *  Micronaut configured properties holder for the Airbyte connector state provided
 *  to the connector CLI as an argument.
 */
@ConfigurationProperties("airbyte.connector.state")
class AirbyteConnectorState {
    lateinit var json: String

    fun toJson(): JsonNode {
        return Jsons.deserialize(json)
    }
}
