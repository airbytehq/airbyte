/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.model.discovery

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.model.sync_mode.SyncMode

/**
 * Configuration for destination discovery operations which use a static schema where operations and
 * schema are known at compile time.
 */
data class StaticOperation(
    @JsonProperty("object_name") val objectName: String,
    @JsonProperty("sync_mode") val syncMode: SyncMode,
    @JsonProperty("schema") val schema: JsonNode,
    @JsonProperty("matching_keys") val matchingKeys: List<List<String>>? = emptyList(),
) : Operation
