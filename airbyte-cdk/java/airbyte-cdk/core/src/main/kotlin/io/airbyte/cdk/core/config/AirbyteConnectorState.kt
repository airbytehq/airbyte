/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.config

import com.fasterxml.jackson.databind.JsonNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.commons.json.Jsons
import io.micronaut.context.annotation.ConfigurationProperties

/**
 *  Micronaut configured properties holder for the Airbyte connector state provided
 *  to the connector CLI as an argument.
 */
@ConfigurationProperties("airbyte.connector.state")
@SuppressFBWarnings(
    value = ["NP_NONNULL_RETURN_VIOLATION"],
    justification = "Uses dependency injection",
)
class AirbyteConnectorState {
    lateinit var json: String

    fun toJson(): JsonNode {
        return Jsons.deserialize(json)
    }
}
