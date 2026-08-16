/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import org.apache.iceberg.DeleteFile
import org.apache.iceberg.FileMetadata
import org.apache.iceberg.data.GenericFileWriterFactory
import org.apache.iceberg.data.Record
import org.apache.iceberg.deletes.PositionDelete
import org.apache.iceberg.deletes.PositionDeleteWriter
import org.apache.iceberg.io.OutputFileFactory

/** One positional delete writer per data file, with positions in ascending order. */
class PositionalDeleteFiles(
    private val writerFactory: GenericFileWriterFactory,
    private val outputFileFactory: OutputFileFactory,
) {
    fun writeAll(
        locations: Sequence<PositionalDeleteResolver.RowLocation>,
        sameFlushLocations: Sequence<PositionalDeleteResolver.RowLocation> = emptySequence(),
    ): List<DeleteFile> {
        val output = mutableListOf<DeleteFile>()
        output += writeOrdered(locations)
        output +=
            writeOrdered(
                sameFlushLocations
                    .toList()
                    .sortedWith(compareBy({ it.path.toString() }, { it.position }))
                    .asSequence()
            )
        return output
    }

    private fun writeOrdered(
        locations: Sequence<PositionalDeleteResolver.RowLocation>,
    ): List<DeleteFile> {
        val writers = mutableMapOf<String, WriterState>()
        try {
            locations.forEach { location ->
                val key = location.path.toString()
                val writer =
                    writers.getOrPut(key) {
                        WriterState(
                            writerFactory.newPositionDeleteWriter(
                                outputFileFactory.newOutputFile(location.spec, location.partition),
                                location.spec,
                                location.partition,
                            ),
                            location.spec,
                            key,
                        )
                    }
                check(
                    writer.lastPath == null ||
                        location.path.toString() > writer.lastPath!! ||
                        (location.path.toString() == writer.lastPath &&
                            location.position >= writer.lastPosition),
                ) {
                    "Positional delete locations must be ordered by path then position"
                }
                val delete = PositionDelete.create<Record>()
                delete.set(location.path, location.position)
                writer.writer.referencedDataFiles().add(location.path.toString())
                writer.writer.write(delete)
                writer.lastPath = location.path.toString()
                writer.lastPosition = location.position
            }
        } finally {
            writers.values.forEach { it.writer.close() }
        }
        return writers.values.flatMap { state ->
            state.writer.result().deleteFiles().map { deleteFile ->
                FileMetadata.deleteFileBuilder(state.spec)
                    .copy(deleteFile)
                    .withReferencedDataFile(state.dataFilePath)
                    .build()
            }
        }
    }

    private class WriterState(
        val writer: PositionDeleteWriter<Record>,
        val spec: org.apache.iceberg.PartitionSpec,
        val dataFilePath: String,
        var lastPath: String? = null,
        var lastPosition: Long = Long.MIN_VALUE,
    )
}
