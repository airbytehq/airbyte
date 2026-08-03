/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import org.apache.iceberg.DataFile
import org.apache.iceberg.DeleteFile
import org.apache.iceberg.FileContent
import org.apache.iceberg.MetadataColumns
import org.apache.iceberg.Schema
import org.apache.iceberg.StructLike
import org.apache.iceberg.Table
import org.apache.iceberg.data.GenericFileWriterFactory
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.Record
import org.apache.iceberg.data.parquet.GenericParquetReaders
import org.apache.iceberg.expressions.Expression
import org.apache.iceberg.expressions.Expressions
import org.apache.iceberg.io.OutputFileFactory
import org.apache.iceberg.parquet.Parquet
import org.apache.iceberg.types.Comparators
import org.apache.iceberg.types.Conversions
import org.apache.iceberg.types.TypeUtil

/**
 * Resolves the physical locations of keys touched by one positional-delete flush.
 *
 * The resolver deliberately ignores existing delete files. A position delete for every older
 * physical copy is safe even when an equality or position delete already hides that row.
 */
class PositionalDeleteResolver(
    private val table: Table,
    private val ref: String,
    schema: Schema,
    identifierFieldIds: Set<Int>,
    private val writerFactory: GenericFileWriterFactory,
    private val outputFileFactory: OutputFileFactory,
    private val maxTouchedKeys: Int = DEFAULT_MAX_TOUCHED_KEYS,
    private val state: PositionalDeleteResolutionState = PositionalDeleteResolutionState(),
) {
    private val identifierSchema = TypeUtil.select(schema, identifierFieldIds)
    private val identifierFields = identifierSchema.columns()
    private val leadingField = identifierFields.first()
    /**
     * Number of data files opened by the most recent resolution. Intended for diagnostics/tests.
     */
    val dataFilesOpened: Int
        get() = state.dataFilesOpened.get()

    init {
        require(identifierFields.isNotEmpty()) {
            "Positional deletes require at least one identifier field"
        }
        require(maxTouchedKeys > 0) { "maxTouchedKeys must be positive" }
    }

    fun resolve(touchedKeys: TouchedKeys): List<DeleteFile> {
        if (touchedKeys.isEmpty()) {
            return emptyList()
        }
        val locations =
            SupersededRowFinder(this).find(touchedKeys, ref) + touchedKeys.supersededWithinFlush()
        return PositionalDeleteFiles(writerFactory, outputFileFactory).writeAll(locations)
    }

    internal fun find(
        touchedKeys: TouchedKeys,
        ref: String,
    ): Sequence<RowLocation> {
        if (touchedKeys.isEmpty()) {
            return emptySequence()
        }
        val touched = touchedKeys.keys()
        val expression = rowGroupExpression(touched)
        val bounds = touchedBounds(touched)
        val plannedTasks = table.newScan().useRef(ref).planFiles().use { tasks -> tasks.toList() }
        val plannedFiles =
            plannedTasks.map { task ->
                PlannedDataFile(
                    task.file(),
                    table.specs()[task.file().specId()]
                        ?: error("Unknown partition spec ${task.file().specId()}"),
                    task.partition(),
                )
            }
        val legacyEqualityDeleteCount =
            plannedTasks
                .flatMap { it.deletes() }
                .filter { it.content() == FileContent.EQUALITY_DELETES }
                .distinctBy { it.location() }
                .count()
        if (legacyEqualityDeleteCount > 0 && state.warningLogged.compareAndSet(false, true)) {
            logger.warn {
                "Positional delete mode found $legacyEqualityDeleteCount existing " +
                    "equality-delete file(s) in ${table.name()}. Positional mode will stop " +
                    "producing equality deletes, but it will not remove these legacy files. " +
                    "Syncs remain correct and complete, but the legacy files will remain until " +
                    "a compaction run configured with delete-file-threshold=1 or the stream is " +
                    "refreshed to rebuild the table."
            }
        }

        state.dataFilesOpened.set(0)
        val locations =
            plannedFiles
                .asSequence()
                .sortedBy { it.file.location().toString() }
                .filter { mayContainAnyKey(it.file, bounds) }
                .onEach { state.dataFilesOpened.incrementAndGet() }
                .flatMap { resolveDataFile(it, touched, expression) }
        return locations
    }

    private fun resolveDataFile(
        planned: PlannedDataFile,
        touched: Set<StructLike>,
        expression: Expression,
    ): Sequence<RowLocation> {
        val projectedSchema = Schema(identifierFields + MetadataColumns.ROW_POSITION)
        val inputFile = table.io().newInputFile(planned.file.location().toString())
        val positions = mutableListOf<Long>()
        Parquet.read(inputFile)
            .project(projectedSchema)
            .filter(expression)
            .createReaderFunc { messageType ->
                GenericParquetReaders.buildReader(projectedSchema, messageType)
            }
            .build<Record>()
            .use { records ->
                for (record in records) {
                    val key = keyFrom(record)
                    if (touched.contains(key)) {
                        positions +=
                            (record.getField(MetadataColumns.ROW_POSITION.name()) as Number)
                                .toLong()
                    }
                }
            }
        return positions.sorted().asSequence().map {
            RowLocation(planned.file.location(), it, planned.spec, planned.partition)
        }
    }

    private fun rowGroupExpression(touched: Set<StructLike>): Expression {
        val values = touched.mapNotNull { it.get(0, Any::class.java) }.distinct()
        if (values.size <= MAX_IN_VALUES) {
            return Expressions.`in`(leadingField.name(), values)
        }
        // Large IN predicates can create very large expression trees. The range is only a
        // row-group prefilter; exact key membership is still checked after reading each row.
        val comparator: Comparator<Any> = Comparators.forType(leadingField.type().asPrimitiveType())
        val min = values.minWithOrNull(comparator)!!
        val max = values.maxWithOrNull(comparator)!!
        return Expressions.and(
            Expressions.greaterThanOrEqual(leadingField.name(), min),
            Expressions.lessThanOrEqual(leadingField.name(), max),
        )
    }

    private fun touchedBounds(touched: Set<StructLike>): List<TouchedBound> =
        identifierFields.indices.map { index ->
            val field = identifierFields[index]
            val comparator = Comparators.forType<Any>(field.type().asPrimitiveType())
            val values = touched.mapNotNull { it.get(index, Any::class.java) }
            TouchedBound(
                field,
                comparator,
                values.minWithOrNull(comparator)!!,
                values.maxWithOrNull(comparator)!!,
            )
        }

    private fun mayContainAnyKey(file: DataFile, bounds: List<TouchedBound>): Boolean {
        val lower = file.lowerBounds().orEmpty()
        val upper = file.upperBounds().orEmpty()
        return bounds.all { bound ->
            val fileLower = lower[bound.field.fieldId()]
            val fileUpper = upper[bound.field.fieldId()]
            fileLower == null ||
                fileUpper == null ||
                (bound.comparator.compare(
                    bound.maximum,
                    Conversions.fromByteBuffer<Any>(bound.field.type(), fileLower.duplicate())
                ) >= 0 &&
                    bound.comparator.compare(
                        bound.minimum,
                        Conversions.fromByteBuffer<Any>(bound.field.type(), fileUpper.duplicate())
                    ) <= 0)
        }
    }

    private fun keyFrom(record: Record): StructLike {
        val key = GenericRecord.create(identifierSchema)
        identifierFields.forEach { field ->
            val value = record.getField(field.name())
            key.setField(field.name(), if (value is CharSequence) value.toString() else value)
        }
        return key
    }

    private data class PlannedDataFile(
        val file: DataFile,
        val spec: org.apache.iceberg.PartitionSpec,
        val partition: StructLike?,
    )

    data class RowLocation(
        val path: CharSequence,
        val position: Long,
        val spec: org.apache.iceberg.PartitionSpec,
        val partition: StructLike?,
    )

    private data class TouchedBound(
        val field: org.apache.iceberg.types.Types.NestedField,
        val comparator: Comparator<Any>,
        val minimum: Any,
        val maximum: Any,
    )

    companion object {
        // The touched-key map and current-write map each retain a copied key and map overhead;
        // allowing roughly 320 bytes per key, plus references and temporary values, 250,000
        // entries reserve about 80 MB. This leaves most of a 2 GB heap for Parquet buffers,
        // writers, and the destination's other state.
        const val DEFAULT_MAX_TOUCHED_KEYS = 250_000
        private const val MAX_IN_VALUES = 1_024
        private val logger = io.github.oshai.kotlinlogging.KotlinLogging.logger {}
    }

    fun maxTouchedKeys(): Int = maxTouchedKeys
}
