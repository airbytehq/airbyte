/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet

/**
 * How much of the Iceberg spec a destination is allowed to use, ordered from the most broadly
 * readable to the most expressive.
 *
 * The levels are cumulative rather than orthogonal: variant is an Iceberg v3 extended type, so it
 * cannot be combined with format version 2.
 */
enum class IcebergCompatibilityLevel(
    val formatVersion: Int,
    val useVariant: Boolean,
) {
    /** Format version 2. Semi-structured values are written as JSON strings. */
    V2(formatVersion = 2, useVariant = false),

    /** Format version 3, still writing semi-structured values as JSON strings. */
    V3(formatVersion = 3, useVariant = false),

    /** Format version 3, writing semi-structured values as variant columns. */
    V3_WITH_VARIANT(formatVersion = 3, useVariant = true),
}
