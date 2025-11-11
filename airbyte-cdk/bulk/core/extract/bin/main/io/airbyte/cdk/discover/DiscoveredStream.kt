/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import io.airbyte.cdk.StreamIdentifier

data class DiscoveredStream(
    val id: StreamIdentifier,
    val columns: List<Field>,
    val primaryKeyColumnIDs: List<List<String>>,
)
