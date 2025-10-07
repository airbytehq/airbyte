/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.discover

import com.fasterxml.jackson.annotation.JsonProperty

/** Component that represents the configuration for extracting and mapping schema information. */
data class SchemaConfiguration(
    @JsonProperty("type") val type: String = "SchemaConfiguration",
    @JsonProperty("properties_path") val propertiesPath: List<String>,
    @JsonProperty("property_name_path") val propertyNamePath: List<String>,
    @JsonProperty("type_path") val typePath: List<String>,
    @JsonProperty("type_mapping") val typeMapping: List<TypesMap>? = null,
)
