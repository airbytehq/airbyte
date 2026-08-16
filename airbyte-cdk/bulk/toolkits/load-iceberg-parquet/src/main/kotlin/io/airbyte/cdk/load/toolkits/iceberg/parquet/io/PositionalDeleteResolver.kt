/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import org.apache.iceberg.DeleteFile
import org.apache.iceberg.Schema
import org.apache.iceberg.StructLike
import org.apache.iceberg.Table
import org.apache.iceberg.data.GenericFileWriterFactory
import org.apache.iceberg.io.OutputFileFactory

/**
 * Resolves the physical locations of keys touched by one positional-delete flush.
 *
 * The resolver deliberately ignores existing delete files. A position delete for every older
 * physical copy is safe even when an equality or position delete already hides that row.
 */
class PositionalDeleteResolver(
    table: Table,
    private val ref: String,
    schema: Schema,
    identifierFieldIds: Set<Int>,
    writerFactory: GenericFileWriterFactory,
    outputFileFactory: OutputFileFactory,
    private val maxTouchedKeys: Int = DEFAULT_MAX_TOUCHED_KEYS,
    state: PositionalDeleteResolutionState = PositionalDeleteResolutionState(),
    allowWholeFileSupersession: Boolean = false,
) {
    private val finder =
        SupersededRowFinder(
            table,
            schema,
            identifierFieldIds,
            state,
            allowWholeFileSupersession = allowWholeFileSupersession,
        )
    private val deleteFiles = PositionalDeleteFiles(writerFactory, outputFileFactory)

    val dataFilesOpened: Int
        get() = finder.dataFilesOpened

    val fullySupersededDataFiles: Set<org.apache.iceberg.DataFile>
        get() = finder.fullySupersededDataFiles

    init {
        require(maxTouchedKeys > 0) { "maxTouchedKeys must be positive" }
    }

    fun resolve(touchedKeys: TouchedKeys): List<DeleteFile> =
        if (touchedKeys.isEmpty()) {
            emptyList()
        } else {
            deleteFiles.writeAll(
                finder.find(touchedKeys, ref),
                touchedKeys.supersededWithinFlush(),
            )
        }

    data class RowLocation(
        val path: CharSequence,
        val position: Long,
        val spec: org.apache.iceberg.PartitionSpec,
        val partition: StructLike?,
    )

    companion object {
        // The touched-key map and current-write map each retain a copied key and map overhead;
        // allowing roughly 320 bytes per key, plus references and temporary values, 250,000
        // entries reserve about 80 MB. This leaves most of a 2 GB heap for Parquet buffers,
        // writers, and the destination's other state.
        const val DEFAULT_MAX_TOUCHED_KEYS = 250_000
    }

    fun maxTouchedKeys(): Int = maxTouchedKeys
}
