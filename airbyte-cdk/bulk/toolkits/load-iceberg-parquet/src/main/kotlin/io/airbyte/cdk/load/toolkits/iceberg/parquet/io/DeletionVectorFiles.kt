/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import org.apache.iceberg.DeleteFile
import org.apache.iceberg.FileContent
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.StructLike
import org.apache.iceberg.Table
import org.apache.iceberg.deletes.BaseDVFileWriter
import org.apache.iceberg.deletes.Deletes
import org.apache.iceberg.deletes.PositionDeleteIndex
import org.apache.iceberg.io.CloseableIterable
import org.apache.iceberg.io.FileIO
import org.apache.iceberg.io.OutputFileFactory
import org.apache.iceberg.puffin.Puffin
import org.apache.iceberg.util.ContentFileUtil

/**
 * Writes resolved row locations as Iceberg v3 deletion vectors (Puffin files, one DV per data
 * file). A data file may only have a single DV, so positions are buffered across [writeAll] calls
 * and materialized once by [finish]. The buffer merge includes the data file's existing DV (if
 * any); the replaced DV is reported by [rewrittenDeleteFiles] so the commit can remove it in the
 * same row delta.
 */
class DeletionVectorFiles(
    private val table: Table,
    private val ref: String,
    private val outputFileFactory: OutputFileFactory,
) : ResolvedDeleteFiles {
    private class PendingDv(
        val spec: PartitionSpec,
        val partition: StructLike?,
    ) {
        val positions = mutableListOf<Long>()
    }

    private val pending = LinkedHashMap<String, PendingDv>()
    private val rewritten = mutableListOf<DeleteFile>()
    private val existingDvByDataFile = lazy { indexExistingDvs() }

    override fun writeAll(
        locations: Sequence<PositionalDeleteResolver.RowLocation>,
        sameFlushLocations: Sequence<PositionalDeleteResolver.RowLocation>,
    ): List<DeleteFile> {
        (locations + sameFlushLocations).forEach { location ->
            val pendingDv =
                pending.getOrPut(location.path.toString()) {
                    PendingDv(location.spec, location.partition)
                }
            pendingDv.positions += location.position
        }
        return emptyList()
    }

    override fun finish(): List<DeleteFile> {
        if (pending.isEmpty()) {
            return emptyList()
        }
        val writer =
            BaseDVFileWriter(outputFileFactory) { path ->
                existingDvByDataFile.value[path]?.let { dv -> loadDvIndex(dv) }
            }
        try {
            pending.forEach { (path, pendingDv) ->
                val index =
                    Deletes.toPositionIndex(
                        CloseableIterable.withNoopClose(pendingDv.positions.toList()),
                    )
                writer.delete(path, index, pendingDv.spec, pendingDv.partition)
            }
        } finally {
            writer.close()
        }
        pending.clear()
        val result = writer.result()
        rewritten += result.rewrittenDeleteFiles()
        return result.deleteFiles()
    }

    override fun rewrittenDeleteFiles(): List<DeleteFile> = rewritten

    /** The DV currently registered for each data file in the scanned snapshot, if any. */
    private fun indexExistingDvs(): Map<String, DeleteFile> =
        table.newScan().useRef(ref).planFiles().use { tasks ->
            tasks
                .asSequence()
                .flatMap { it.deletes().asSequence() }
                .filter { deleteFile ->
                    deleteFile.content() == FileContent.POSITION_DELETES &&
                        ContentFileUtil.isDV(deleteFile) &&
                        deleteFile.referencedDataFile() != null
                }
                .associate { it.referencedDataFile() to it }
        }

    private fun loadDvIndex(dv: DeleteFile): PositionDeleteIndex =
        loadDeletionVectorIndex(table.io(), dv)
}

/** Reads the deletion-vector index for one file-scoped DV from its Puffin blob. */
internal fun loadDeletionVectorIndex(io: FileIO, dv: DeleteFile): PositionDeleteIndex {
    val input = io.newInputFile(dv.location())
    Puffin.read(input).withFileSize(dv.fileSizeInBytes()).build().use { reader ->
        val blobs =
            reader.fileMetadata().blobs().filter { it.offset() == dv.contentOffset() }.toList()
        val blobData =
            reader.readAll(blobs).singleOrNull()?.second()
                ?: error("No deletion-vector blob found in ${dv.location()}")
        val bytes = ByteArray(blobData.remaining())
        blobData.get(bytes)
        return PositionDeleteIndex.deserialize(bytes, dv)
    }
}
