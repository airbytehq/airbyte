/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

data class DiscoveredStream(
    val name: String,
    val namespace: String?,
    val columns: List<Field>,
    val primaryKeyColumnIDs: List<List<String>>,
)
