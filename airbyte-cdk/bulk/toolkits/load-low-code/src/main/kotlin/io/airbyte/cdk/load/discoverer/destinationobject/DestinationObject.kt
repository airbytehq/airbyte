/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.destinationobject

import com.fasterxml.jackson.databind.JsonNode

/**
 * This class is a structure containing the information of a destination object based on the API. It
 * may of may not have the schema information within the apiRepresentation. It is meant to be used
 * for interpolation in order to create the operation.
 */
data class DestinationObject(val name: String, val apiRepresentation: JsonNode)
