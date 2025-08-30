/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.discovery

import com.fasterxml.jackson.annotation.JsonProperty

/**
 * Configuration for destination check operations. Performs a HTTP request to the destination API to
 * check if the configuration is valid.
 */
data class CompositeOperations(
    @JsonProperty("type") val type: String = "CompositeOperations",
    @JsonProperty("operations") val operations: List<StaticOperation>
)
