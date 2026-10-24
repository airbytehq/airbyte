/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import org.apache.iceberg.DeleteFile

/** Writes resolved row locations as delete files of the table's configured delete encoding. */
interface ResolvedDeleteFiles {
    fun writeAll(
        locations: Sequence<PositionalDeleteResolver.RowLocation>,
        sameFlushLocations: Sequence<PositionalDeleteResolver.RowLocation> = emptySequence(),
    ): List<DeleteFile>

    /**
     * Emits any buffered deletes. A writer may defer physical files to produce at most one delete
     * file per data file across successive [writeAll] calls within a flush.
     */
    fun finish(): List<DeleteFile> = emptyList()

    /**
     * Existing delete files the written deletes replace. Deletion vectors merge a data file's prior
     * DV, so the commit must remove the replaced file in the same [org.apache.iceberg.RowDelta].
     */
    fun rewrittenDeleteFiles(): List<DeleteFile> = emptyList()
}
