/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.github.oshai.kotlinlogging.KotlinLogging
import kotlin.time.Duration.Companion.milliseconds
import org.apache.iceberg.MetadataColumns
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.data.IcebergGenerics
import org.apache.iceberg.data.GenericRecord
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
        val columns =
            deleteSchema.columns().map { it.name() } +
                listOf(MetadataColumns.FILE_PATH.name(), MetadataColumns.ROW_POSITION.name())
        val snapshotId =
            requireNotNull(table.refs()[ref]?.snapshotId()) {
                "Cannot build positional delete index for ${table.name()}: ref $ref has no snapshot"
            }
        val scan = table.newScan().useRef(ref)
        val locations =
            scan.planFiles().use { tasks ->
                tasks.associateBy(
                    { it.file().location().toString() },
                    {
                        PositionalDeleteIndex.RowLocationMetadata(
                            table.specs()[it.file().specId()]!!,
                            it.partition(),
                        )
                    },
                )
            }
        val start = System.nanoTime()
        var rows = 0L

        IcebergGenerics.read(table).useSnapshot(snapshotId).select(columns).build().use { records ->
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
                val path = record.getField(MetadataColumns.FILE_PATH.name()).toString()
                val position = (record.getField(MetadataColumns.ROW_POSITION.name()) as Number).toLong()
                val metadata =
                    requireNotNull(locations[path]) {
                        "Could not find planned data file $path while building positional delete index"
                    }
                val previous =
                    index.replace(
                        key,
                        PositionalDeleteIndex.RowLocation(
                            path,
                            position,
                            metadata.spec,
                            metadata.partition,
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

        val elapsed = (System.nanoTime() - start).milliseconds
        logger.info {
            "Built positional delete index for ${table.name()} on ref $ref: " +
                "${index.size()} keys, $rows rows, took $elapsed"
        }
        return index
    }

    companion object {
        const val DEFAULT_MAX_ENTRIES = 10_000_000
    }
}
