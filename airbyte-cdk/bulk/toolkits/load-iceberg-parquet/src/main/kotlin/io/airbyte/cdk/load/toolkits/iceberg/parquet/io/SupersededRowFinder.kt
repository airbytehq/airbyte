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
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.Record
import org.apache.iceberg.data.parquet.GenericParquetReaders
import org.apache.iceberg.expressions.Expression
import org.apache.iceberg.expressions.Expressions
import org.apache.iceberg.parquet.Parquet
import org.apache.iceberg.types.Comparators
import org.apache.iceberg.types.Conversions
import org.apache.iceberg.types.TypeUtil

/** Physical locations of every committed row whose identifier appears in [keys]. */
class SupersededRowFinder(
    private val table: Table,
    schema: Schema,
    identifierFieldIds: Set<Int>,
    private val state: PositionalDeleteResolutionState,
    private val maxInValues: Int = MAX_IN_VALUES,
) {
    private val identifierSchema = TypeUtil.select(schema, identifierFieldIds)
    private val identifierFields = identifierSchema.columns()
    private val leadingField = identifierFields.first()

    val dataFilesOpened: Int
        get() = state.dataFilesOpened.get()

    val rowsScanned: Long
        get() = state.rowsScanned.get()

    fun find(keys: TouchedKeys, ref: String): Sequence<PositionalDeleteResolver.RowLocation> {
        if (keys.isEmpty()) return emptySequence()
        val touched = keys.keys()
        val expression = rowGroupExpression(touched)
        val bounds = touchedBounds(touched)
        val plannedFiles =
            table.newScan().useRef(ref).filter(expression).planFiles().use { tasks ->
                tasks
                    .asSequence()
                    .map { task ->
                        PlannedDataFile(
                            task.file(),
                            table.specs()[task.file().specId()]
                                ?: error("Unknown partition spec ${task.file().specId()}"),
                            task.partition(),
                            task.deletes().toList(),
                        )
                    }
                    .filter { mayContainAnyKey(it.file, bounds) }
                    .toList()
            }
        val legacyEqualityDeleteCount =
            plannedFiles
                .flatMap { it.deletes }
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
        state.rowsScanned.set(0)
        return plannedFiles
            .asSequence()
            .sortedBy { it.file.location().toString() }
            .onEach { state.dataFilesOpened.incrementAndGet() }
            .flatMap { supersededRowsIn(it, touched, expression) }
    }

    private fun supersededRowsIn(
        planned: PlannedDataFile,
        touched: Set<StructLike>,
        expression: Expression,
    ): Sequence<PositionalDeleteResolver.RowLocation> = sequence {
        val projectedSchema = Schema(identifierFields + MetadataColumns.ROW_POSITION)
        val inputFile = table.io().newInputFile(planned.file.location().toString())
        Parquet.read(inputFile)
            .project(projectedSchema)
            .filter(expression)
            .createReaderFunc { messageType ->
                GenericParquetReaders.buildReader(projectedSchema, messageType)
            }
            .build<Record>()
            .use { records ->
                for (record in records) {
                    state.rowsScanned.incrementAndGet()
                    if (touched.contains(keyFrom(record))) {
                        yield(
                            PositionalDeleteResolver.RowLocation(
                                planned.file.location(),
                                (record.getField(MetadataColumns.ROW_POSITION.name()) as Number)
                                    .toLong(),
                                planned.spec,
                                planned.partition,
                            )
                        )
                    }
                }
            }
    }

    private fun rowGroupExpression(touched: Set<StructLike>): Expression {
        val values = touched.mapNotNull { it.get(0, Any::class.java) }.distinct()
        val comparator: Comparator<Any> = Comparators.forType(leadingField.type().asPrimitiveType())
        val min =
            values.minWithOrNull(comparator)
                ?: error("Touched identifier field ${leadingField.name()} has no non-null values")
        val max =
            values.maxWithOrNull(comparator)
                ?: error("Touched identifier field ${leadingField.name()} has no non-null values")
        val range =
            Expressions.and(
                Expressions.greaterThanOrEqual(leadingField.name(), min),
                Expressions.lessThanOrEqual(leadingField.name(), max),
            )
        if (values.size <= maxInValues) {
            return Expressions.and(range, Expressions.`in`(leadingField.name(), values))
        }
        return range
    }

    private fun touchedBounds(touched: Set<StructLike>): List<TouchedBound> =
        identifierFields.indices.map { index ->
            val field = identifierFields[index]
            val comparator = Comparators.forType<Any>(field.type().asPrimitiveType())
            val values = touched.mapNotNull { it.get(index, Any::class.java) }
            require(values.isNotEmpty()) {
                "Touched identifier field ${field.name()} has no non-null values"
            }
            TouchedBound(field, comparator, values.minWith(comparator), values.maxWith(comparator))
        }

    private fun mayContainAnyKey(file: DataFile, bounds: List<TouchedBound>): Boolean {
        // For multi-column identifiers this is a bounding-box prefilter: it can admit files
        // containing no matching key tuple. Exact complete-key membership is checked after read.
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
        val deletes: List<DeleteFile>,
    )

    private data class TouchedBound(
        val field: org.apache.iceberg.types.Types.NestedField,
        val comparator: Comparator<Any>,
        val minimum: Any,
        val maximum: Any,
    )

    companion object {
        // InclusiveMetricsEvaluator in Iceberg 1.11.0 gives up on IN predicates above 200
        // The range keeps manifest and metrics pruning effective, while IN lets dictionary and
        // bloom filters perform exact membership checks until candidate-set lookup cost dominates.
        private const val MAX_IN_VALUES = 200
        private val logger = io.github.oshai.kotlinlogging.KotlinLogging.logger {}
    }
}
