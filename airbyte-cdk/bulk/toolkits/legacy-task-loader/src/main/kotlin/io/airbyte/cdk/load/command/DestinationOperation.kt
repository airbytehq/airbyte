/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.load.data.AirbyteType

/**
 * Internal Representation of the DestinationOperation from the protocol that is used in the context
 * of a Destination Discover command.
 */
data class DestinationOperation(
    val objectName: String,
    val syncMode: ImportType,
    val schema: AirbyteType,
    val matchingKeys: List<List<String>>,
)
