/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.discover

import com.fasterxml.jackson.annotation.JsonProperty

/** Represents a mapping between a current type and its corresponding target type. */
data class TypesMap(
    @JsonProperty("type") val type: String = "TypesMap",
    @JsonProperty("api_type") val apiType: List<String>,
    @JsonProperty("airbyte_type") val airbyteType: List<AirbyteType>
)
