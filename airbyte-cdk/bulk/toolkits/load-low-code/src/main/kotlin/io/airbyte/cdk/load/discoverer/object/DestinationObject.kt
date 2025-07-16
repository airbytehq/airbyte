/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.`object`

import com.fasterxml.jackson.databind.JsonNode

data class DestinationObject(val name: String, val apiRepresentation: JsonNode)
