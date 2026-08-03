/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import java.math.BigInteger
import java.nio.ByteBuffer
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
    private val maxSubRanges: Int = MAX_SUB_RANGES,
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
        require(values.isNotEmpty()) {
            "Touched identifier field ${leadingField.name()} has no non-null values"
        }
        val rangeExpression =
            disjointRanges(values, comparator)
                .map { (min, max) ->
                    Expressions.and(
                        Expressions.greaterThanOrEqual(leadingField.name(), min),
                        Expressions.lessThanOrEqual(leadingField.name(), max),
                    )
                }
                .reduce { left, right -> Expressions.or(left, right) }
        if (values.size <= maxInValues) {
            return Expressions.and(rangeExpression, Expressions.`in`(leadingField.name(), values))
        }
        return rangeExpression
    }

    private fun touchedBounds(touched: Set<StructLike>): List<TouchedBound> =
        identifierFields.indices.map { index ->
            val field = identifierFields[index]
            val comparator = Comparators.forType<Any>(field.type().asPrimitiveType())
            val values = touched.mapNotNull { it.get(index, Any::class.java) }
            require(values.isNotEmpty()) {
                "Touched identifier field ${field.name()} has no non-null values"
            }
            val ranges =
                if (index == 0) {
                    disjointRanges(values, comparator)
                } else {
                    listOf(values.minWith(comparator) to values.maxWith(comparator))
                }
            TouchedBound(field, comparator, ranges)
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
                bound.ranges.any { (minimum, maximum) ->
                    bound.comparator.compare(
                        maximum,
                        Conversions.fromByteBuffer<Any>(bound.field.type(), fileLower.duplicate())
                    ) >= 0 &&
                        bound.comparator.compare(
                            minimum,
                            Conversions.fromByteBuffer<Any>(
                                bound.field.type(),
                                fileUpper.duplicate()
                            )
                        ) <= 0
                }
        }
    }

    private fun disjointRanges(
        values: List<Any>,
        comparator: Comparator<Any>,
    ): List<Pair<Any, Any>> {
        // Splitting at the largest gaps minimizes the total covered span for a fixed range count.
        val sorted = values.distinct().sortedWith(comparator)
        val rangeCount = minOf(maxSubRanges.coerceAtLeast(1), sorted.size)
        if (rangeCount == 1) return listOf(sorted.first() to sorted.last())
        val splitIndexes =
            (0 until sorted.lastIndex)
                .sortedByDescending { gapScore(sorted[it], sorted[it + 1]) }
                .take(rangeCount - 1)
                .sorted()
        val ranges = mutableListOf<Pair<Any, Any>>()
        var start = 0
        for (splitIndex in splitIndexes) {
            ranges += sorted[start] to sorted[splitIndex]
            start = splitIndex + 1
        }
        ranges += sorted[start] to sorted.last()
        return ranges
    }

    private fun gapScore(left: Any, right: Any): Double {
        // Gap scoring is only a heuristic for choosing split points; correctness relies on
        // the comparator and the resulting inclusive ranges, not on this distance estimate.
        val leftBytes = gapBytes(left)
        val rightBytes = gapBytes(right)
        val width = maxOf(leftBytes?.size ?: 0, rightBytes?.size ?: 0)
        val leftValue = leftBytes?.let { BigInteger(1, leftPad(it, width)) } ?: gapValue(left)
        val rightValue = rightBytes?.let { BigInteger(1, leftPad(it, width)) } ?: gapValue(right)
        return if (leftValue != null && rightValue != null) {
            rightValue.subtract(leftValue).toDouble()
        } else {
            1.0
        }
    }

    private fun gapBytes(value: Any): ByteArray? =
        when (value) {
            is CharSequence -> value.toString().toByteArray(Charsets.UTF_8)
            is ByteBuffer -> {
                val bytes = ByteArray(value.remaining())
                value.duplicate().get(bytes)
                bytes
            }
            else -> null
        }

    private fun leftPad(bytes: ByteArray, width: Int): ByteArray =
        ByteArray(width - bytes.size) + bytes

    private fun gapValue(value: Any): BigInteger? =
        when (value) {
            is Number -> value.toString().toBigDecimal().toBigInteger()
            else -> null
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
        val ranges: List<Pair<Any, Any>>,
    )

    companion object {
        // InclusiveMetricsEvaluator in Iceberg 1.11.0 gives up on IN predicates above 200
        // The range keeps manifest and metrics pruning effective, while IN lets dictionary and
        // bloom filters perform exact membership checks until candidate-set lookup cost dominates.
        private const val MAX_IN_VALUES = 200
        // Eight is the largest count without a measurable elapsed-time penalty in the benchmark;
        // higher counts improve rows scanned in some cases but are slower in others.
        private const val MAX_SUB_RANGES = 8
        private val logger = io.github.oshai.kotlinlogging.KotlinLogging.logger {}
    }
}
