/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

/** Essentially a datum for [MetadataQuerier] query results. */
data class DiscoveredStream(
    val table: TableName,
    val columnMetadata: List<ColumnMetadata>,
    val primaryKeyColumnNames: List<List<String>>
)
