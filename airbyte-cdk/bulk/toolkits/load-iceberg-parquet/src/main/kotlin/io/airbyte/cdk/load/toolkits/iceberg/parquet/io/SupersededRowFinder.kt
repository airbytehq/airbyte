/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

/** Physical locations of every committed row whose identifier appears in [keys]. */
class SupersededRowFinder(
    private val resolver: PositionalDeleteResolver,
) {
    fun find(keys: TouchedKeys, ref: String): Sequence<PositionalDeleteResolver.RowLocation> =
        resolver.find(keys, ref)
}
