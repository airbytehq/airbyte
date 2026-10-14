/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import org.apache.iceberg.DataFile
import org.apache.iceberg.DeleteFile
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.StructLike
import org.apache.iceberg.Table
import org.apache.iceberg.data.GenericFileWriterFactory
import org.apache.iceberg.io.OutputFileFactory

/**
 * Resolves the physical locations of keys touched by one positional-delete flush.
 *
 * A position delete for every older physical copy is safe even when an equality or position delete
 * already hides that row, so [suppressDeletedPositions] can be turned off to write a delete for
 * every copy without consulting prior deletes. Whole-file supersession then has nothing to count
 * and must be off too.
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
    suppressDeletedPositions: Boolean = true,
    writeDeletionVectors: Boolean = false,
) {
    private val finder =
        SupersededRowFinder(
            table,
            schema,
            identifierFieldIds,
            state,
            allowWholeFileSupersession = allowWholeFileSupersession,
            suppressDeletedPositions = suppressDeletedPositions,
        )
    private val deleteFiles: ResolvedDeleteFiles =
        if (writeDeletionVectors) {
            DeletionVectorFiles(table, ref, outputFileFactory)
        } else {
            PositionalDeleteFiles(writerFactory, outputFileFactory)
        }

    /** Delete files (existing DVs) that the written deletes replace and the commit must remove. */
    val rewrittenDeleteFiles: List<DeleteFile>
        get() = deleteFiles.rewrittenDeleteFiles()

    val dataFilesOpened: Int
        get() = finder.dataFilesOpened

    val fullySupersededDataFiles: Set<DataFile>
        get() = finder.fullySupersededDataFiles

    init {
        require(maxTouchedKeys > 0) { "maxTouchedKeys must be positive" }
        // Whole-file supersession counts already-deleted positions, so it is meaningless
        // without them.
        require(suppressDeletedPositions || !allowWholeFileSupersession) {
            "Whole-file supersession requires suppression of already-deleted positions"
        }
    }

    /** Emits any deletes the writer deferred while resolving successive batches. */
    fun finish(): List<DeleteFile> = deleteFiles.finish()

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
        val spec: PartitionSpec,
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
