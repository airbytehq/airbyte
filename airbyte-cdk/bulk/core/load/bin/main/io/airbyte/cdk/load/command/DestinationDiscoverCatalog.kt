/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

/**
 * Internal representation of a DestinationCatalog as returned by a destination on a discover
 * command.
 *
 * This is the load-cdk version of the DestinationCatalog from the protocol, however, there is
 * already a DestinationCatalog which represents the destination view of the AirbyteCatalog from a
 * destination POV.
 */
data class DestinationDiscoverCatalog(
    val operations: List<DestinationOperation>,
)
