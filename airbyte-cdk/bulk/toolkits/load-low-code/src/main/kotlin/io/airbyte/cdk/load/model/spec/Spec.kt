/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.v0.AdvancedAuth

data class Spec(
    @JsonProperty("connection_specification") val connectionSpecification: JsonNode,
    @JsonProperty("advanced_auth") val advancedAuth: AdvancedAuth?,
)
