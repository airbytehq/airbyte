/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.github.oshai.kotlinlogging.KotlinLogging
import kotlin.time.Duration.Companion.milliseconds
import org.apache.iceberg.MetadataColumns
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
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
        val scan = table.newScan().useRef(ref).select(columns)
        val scanSchema = scan.schema()
        val positions =
            scanSchema.columns().mapIndexed { fieldPosition, field ->
                field.name() to fieldPosition
            }.toMap()
        val start = System.nanoTime()
        var rows = 0L

        scan.planFiles().use { tasks ->
            for (task in tasks) {
                val dataTask = task.asDataTask()
                dataTask.rows().use { records ->
                    for (record in records) {
                        if (index.size() >= maxEntries) {
                            throw IllegalStateException(
                                "Positional delete index for ${table.name()} exceeded its maximum " +
                                    "$maxEntries entries. Increase the configured limit or use equality deletes."
                            )
                        }
                        val key = GenericRecord.create(deleteSchema)
                        deleteSchema.columns().forEach { field ->
                            key.setField(
                                field.name(),
                                record.get(positions[field.name()]!!, Any::class.java),
                            )
                        }
                        val path =
                            record.get(
                                positions[MetadataColumns.FILE_PATH.name()]!!,
                                CharSequence::class.java,
                            )
                        val position =
                            record.get(
                                positions[MetadataColumns.ROW_POSITION.name()]!!,
                                java.lang.Long::class.java,
                            )
                        index.replace(
                            key,
                            PositionalDeleteIndex.RowLocation(
                                path,
                                position.toLong(),
                                table.specs()[task.file().specId()]!!,
                                task.partition(),
                            ),
                        )
                        rows += 1
                    }
                }
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
