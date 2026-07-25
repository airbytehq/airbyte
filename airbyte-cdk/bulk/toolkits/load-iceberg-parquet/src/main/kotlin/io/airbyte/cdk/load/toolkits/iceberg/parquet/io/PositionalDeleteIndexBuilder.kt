/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.iceberg.MetadataColumns
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.Record
import org.apache.iceberg.data.parquet.GenericParquetReaders
import org.apache.iceberg.parquet.Parquet
import org.apache.iceberg.types.TypeUtil

private val logger = KotlinLogging.logger {}

class PositionalDeleteIndexBuilder(
    private val maxEntries: Int = DEFAULT_MAX_ENTRIES,
) {
    fun empty(schema: Schema, identifierFieldIds: Set<Int>): PositionalDeleteIndex =
        PositionalDeleteIndex(TypeUtil.select(schema, identifierFieldIds).asStruct())

    fun build(
        table: Table,
        ref: String,
        schema: Schema,
        identifierFieldIds: Set<Int>,
    ): PositionalDeleteIndex {
        require(identifierFieldIds.isNotEmpty()) {
            "Positional deletes require at least one identifier field for table ${table.name()}"
        }
        val deleteSchema = TypeUtil.select(schema, identifierFieldIds)
        val index = PositionalDeleteIndex(deleteSchema.asStruct())
        require(table.refs()[ref]?.snapshotId() != null) {
            "Cannot build positional delete index for ${table.name()}: ref $ref has no snapshot"
        }
        val scan = table.newScan().useRef(ref)
        val files =
            scan.planFiles().use { tasks ->
                tasks.associateBy(
                    { it.file().location().toString() },
                    {
                        PlannedFile(
                            it.file(),
                            PositionalDeleteIndex.RowLocationMetadata(
                                table.specs()[it.file().specId()]!!,
                                it.partition(),
                            ),
                        )
                    },
                )
            }
        val start = System.nanoTime()
        var rows = 0L

        require(files.values.all { it.file.format() == org.apache.iceberg.FileFormat.PARQUET }) {
            "Positional delete index currently supports only Parquet data files"
        }
        for ((path, planned) in files) {
            var position = 0L
            val inputFile = table.io().newInputFile(path)
            Parquet.read(inputFile)
                .project(deleteSchema)
                .createReaderFunc { messageType ->
                    GenericParquetReaders.buildReader(deleteSchema, messageType)
                }
                .build<Record>()
                .use { records ->
                    for (record in records) {
                        if (index.size() >= maxEntries) {
                            throw IllegalStateException(
                                "Positional delete index for ${table.name()} exceeded its maximum " +
                                    "$maxEntries entries. Increase the configured limit or use equality deletes."
                            )
                        }
                        val key = GenericRecord.create(deleteSchema)
                        deleteSchema.columns().forEach { field ->
                            key.setField(field.name(), record.getField(field.name()))
                        }
                        val previous =
                            index.replace(
                                key,
                                PositionalDeleteIndex.RowLocation(
                                    path,
                                    position++,
                                    planned.metadata.spec,
                                    planned.metadata.partition,
                                ),
                            )
                        check(previous == null) {
                            "Positional delete index for ${table.name()} found multiple rows for " +
                                "the same identifier. Positional deletes require unique keys in " +
                                "the base snapshot."
                        }
                        rows += 1
                    }
                }
        }

        val elapsedMillis = (System.nanoTime() - start) / 1_000_000
        logger.info {
            "Built positional delete index for ${table.name()} on ref $ref: " +
                "${index.size()} keys, $rows rows, took ${elapsedMillis}ms"
        }
        return index
    }

    private data class PlannedFile(
        val file: org.apache.iceberg.DataFile,
        val metadata: PositionalDeleteIndex.RowLocationMetadata,
    )

    companion object {
        const val DEFAULT_MAX_ENTRIES = 10_000_000
    }
}
