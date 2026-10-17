/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import org.apache.iceberg.DeleteFile
import org.apache.iceberg.FileMetadata
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.data.GenericFileWriterFactory
import org.apache.iceberg.data.Record
import org.apache.iceberg.deletes.PositionDelete
import org.apache.iceberg.deletes.PositionDeleteWriter
import org.apache.iceberg.encryption.EncryptedOutputFile
import org.apache.iceberg.io.OutputFileFactory

/** One positional delete writer per data file, with positions in ascending order. */
class PositionalDeleteFiles(
    private val writerFactory: GenericFileWriterFactory,
    private val outputFileFactory: OutputFileFactory,
) : ResolvedDeleteFiles {
    override fun writeAll(
        locations: Sequence<PositionalDeleteResolver.RowLocation>,
        sameFlushLocations: Sequence<PositionalDeleteResolver.RowLocation>,
    ): List<DeleteFile> {
        val output = mutableListOf<DeleteFile>()
        output += writeOrdered(locations)
        output +=
            writeOrdered(
                sameFlushLocations
                    .toList()
                    .sortedWith(compareBy({ it.path.toString() }, { it.position }))
                    .asSequence(),
            )
        return output
    }

    private fun writeOrdered(
        locations: Sequence<PositionalDeleteResolver.RowLocation>,
    ): List<DeleteFile> {
        // Locations arrive path-sorted, so at most one writer stays open at a time: a new path
        // closes and collects the previous writer's result.
        val output = mutableListOf<DeleteFile>()
        var open: WriterState? = null
        fun closeOpen() {
            open?.let { state ->
                state.writer.close()
                state.writer.result().deleteFiles().forEach { deleteFile ->
                    output +=
                        FileMetadata.deleteFileBuilder(state.spec)
                            .copy(deleteFile)
                            .withReferencedDataFile(state.dataFilePath)
                            .build()
                }
                open = null
            }
        }
        try {
            locations.forEach { location ->
                val key = location.path.toString()
                var writer = open
                if (writer == null || writer.dataFilePath != key) {
                    closeOpen()
                    writer =
                        WriterState(
                            writerFactory.newPositionDeleteWriter(
                                newOutputFile(location),
                                location.spec,
                                location.partition,
                            ),
                            location.spec,
                            key,
                        )
                    open = writer
                }
                check(location.position >= writer.lastPosition) {
                    "Positional delete locations must be ordered by path then position"
                }
                val delete = PositionDelete.create<Record>()
                delete.set(location.path, location.position)
                writer.writer.referencedDataFiles().add(location.path.toString())
                writer.writer.write(delete)
                writer.lastPosition = location.position
            }
        } finally {
            closeOpen()
        }
        return output
    }

    /**
     * An unpartitioned spec renders an empty partition path, so asking for a partitioned location
     * yields a doubled separator that some readers cannot resolve.
     */
    private fun newOutputFile(location: PositionalDeleteResolver.RowLocation): EncryptedOutputFile =
        if (location.partition == null) {
            outputFileFactory.newOutputFile()
        } else {
            outputFileFactory.newOutputFile(location.spec, location.partition)
        }

    private class WriterState(
        val writer: PositionDeleteWriter<Record>,
        val spec: PartitionSpec,
        val dataFilePath: String,
        var lastPosition: Long = Long.MIN_VALUE,
    )
}
