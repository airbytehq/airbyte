/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import org.apache.iceberg.DeleteFile
import org.apache.iceberg.StructLike
import org.apache.iceberg.data.GenericFileWriterFactory
import org.apache.iceberg.data.Record
import org.apache.iceberg.deletes.PositionDelete
import org.apache.iceberg.deletes.PositionDeleteWriter
import org.apache.iceberg.io.OutputFileFactory

/** One positional delete file per partition, with file paths and positions in ascending order. */
class PositionalDeleteFiles(
    private val writerFactory: GenericFileWriterFactory,
    private val outputFileFactory: OutputFileFactory,
) {
    fun writeAll(locations: Sequence<PositionalDeleteResolver.RowLocation>): List<DeleteFile> {
        val ordered =
            locations.toList().sortedWith(compareBy({ it.path.toString() }, { it.position }))
        return ordered
            .groupBy { PartitionKey(it.spec.specId(), partitionValues(it.partition)) }
            .values
            .flatMap { partitionLocations ->
                val first = partitionLocations.first()
                val writer: PositionDeleteWriter<Record> =
                    writerFactory.newPositionDeleteWriter(
                        outputFileFactory.newOutputFile(first.spec, first.partition),
                        first.spec,
                        first.partition,
                    )
                writer.use {
                    partitionLocations.forEach { location ->
                        val delete = PositionDelete.create<Record>()
                        delete.set(location.path, location.position)
                        it.write(delete)
                    }
                }
                writer.result().deleteFiles()
            }
    }

    private fun partitionValues(partition: StructLike?): List<Any?> =
        if (partition == null) {
            emptyList()
        } else {
            (0 until partition.size()).map { partition.get(it, Any::class.java) }
        }

    private data class PartitionKey(val specId: Int, val values: List<Any?>)
}
