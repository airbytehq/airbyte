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
import org.apache.iceberg.deletes.Deletes
import org.apache.iceberg.deletes.PositionDeleteIndex
import org.apache.iceberg.deletes.PositionDeleteIndexUtil
import org.apache.iceberg.expressions.Expression
import org.apache.iceberg.expressions.Expressions
import org.apache.iceberg.io.DeleteSchemaUtil
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
    private val allowWholeFileSupersession: Boolean = false,
    private val suppressDeletedPositions: Boolean = true,
) {
    private val identifierSchema = TypeUtil.select(schema, identifierFieldIds)
    private val identifierFields = identifierSchema.columns()
    private val leadingField = identifierFields.first()

    @Volatile private var indexEntries: Map<String, DeleteIndexStatistics.Entry> = emptyMap()

    val dataFilesOpened: Int
        get() = state.dataFilesOpened.get()

    val rowsScanned: Long
        get() = state.rowsScanned.get()

    val fullySupersededDataFiles: Set<DataFile>
        get() = state.fullySupersededDataFiles

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
        state.fullySupersededDataFiles.clear()
        state.positionDeleteIndexes.clear()
        state.unreadablePositionDeleteFiles.clear()
        state.positionDeleteFilesRead.set(0)
        state.deleteIndex.beginFlush()
        indexEntries =
            if (suppressDeletedPositions) {
                state.deleteIndex.entries(table, table.refs()[ref]?.snapshotId() ?: NO_SNAPSHOT)
            } else {
                emptyMap()
            }
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
        val positionIndex = positionDeleteIndex(planned)
        val priorDeletedPositions = positionIndex?.cardinality() ?: 0
        val projectedSchema = Schema(identifierFields + MetadataColumns.ROW_POSITION)
        val inputFile = table.io().newInputFile(planned.file.location().toString())
        val locations =
            if (allowWholeFileSupersession) {
                mutableListOf<PositionalDeleteResolver.RowLocation>()
            } else {
                null
            }
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
                    val position =
                        (record.getField(MetadataColumns.ROW_POSITION.name()) as Number).toLong()
                    if (
                        touched.contains(keyFrom(record)) &&
                            (positionIndex == null || !positionIndex.isDeleted(position))
                    ) {
                        val location =
                            PositionalDeleteResolver.RowLocation(
                                planned.file.location(),
                                position,
                                planned.spec,
                                planned.partition,
                            )
                        if (locations == null) {
                            yield(location)
                        } else {
                            locations += location
                        }
                    }
                }
            }
        if (locations != null) {
            if (locations.size.toLong() + priorDeletedPositions == planned.file.recordCount()) {
                state.fullySupersededDataFiles += planned.file
            } else {
                for (location in locations) {
                    yield(location)
                }
            }
        }
    }

    private fun positionDeleteIndex(planned: PlannedDataFile): PositionDeleteIndex? {
        if (!suppressDeletedPositions) return null
        val location = planned.file.location().toString()
        val index = mergedPositionDeleteIndex(planned, location)
        state.deleteIndex.observe(location, planned.file.recordCount(), planned.deletes, index)
        return index
    }

    private fun mergedPositionDeleteIndex(
        planned: PlannedDataFile,
        location: String,
    ): PositionDeleteIndex? {
        indexedPositionDeletes(planned, location)?.let {
            return it
        }
        val positionDeletes =
            planned.deletes.filter { it.content() == FileContent.POSITION_DELETES }
        if (positionDeletes.isEmpty()) return null
        val indexes =
            positionDeletes.mapNotNull { deleteFile ->
                val deletePath = deleteFile.location().toString()
                if (state.unreadablePositionDeleteFiles.contains(deletePath)) {
                    return@mapNotNull null
                }
                val indexesByDataFile =
                    state.positionDeleteIndexes[deletePath]
                        ?: try {
                            readPositionDeleteIndexes(deleteFile).also {
                                state.positionDeleteIndexes[deletePath] = it
                            }
                        } catch (e: Exception) {
                            state.unreadablePositionDeleteFiles.add(deletePath)
                            logger.warn(e) {
                                "Unable to load prior position deletes from $deletePath; " +
                                    "position suppression is disabled for data file " +
                                    "${planned.file.location()}"
                            }
                            return@mapNotNull null
                        }
                indexesByDataFile[planned.file.location().toString()]
            }
        return if (indexes.isEmpty()) {
            null
        } else {
            PositionDeleteIndexUtil.merge(indexes)
        }
    }

    /**
     * The already-deleted positions of [location] as published by a previous flush, or null when no
     * entry still describes the file.
     *
     * Reading one bitmap replaces reading every prior delete file of the data file. Validation is
     * strict: an entry that no longer matches the file's record count or the delete files this scan
     * planned is discarded, so the caller reads delete files exactly as if no index existed.
     */
    private fun indexedPositionDeletes(
        planned: PlannedDataFile,
        location: String,
    ): PositionDeleteIndex? {
        val entry =
            DeleteIndexStatistics.validEntry(
                indexEntries[location],
                location,
                planned.file.recordCount(),
                planned.deletes,
            )
                ?: return null
        return try {
            DeleteIndexStatistics.toIndex(entry)
        } catch (e: Exception) {
            logger.warn(e) {
                "Unable to decode the delete index entry for $location; " +
                    "this flush will read its prior delete files instead"
            }
            null
        }
    }

    private fun readPositionDeleteIndexes(
        deleteFile: DeleteFile,
    ): Map<String, PositionDeleteIndex> {
        state.positionDeleteFilesRead.incrementAndGet()
        val deleteSchema = DeleteSchemaUtil.pathPosSchema()
        return Parquet.read(table.io().newInputFile(deleteFile.location().toString()))
            .project(deleteSchema)
            .createReaderFunc { messageType ->
                GenericParquetReaders.buildReader(deleteSchema, messageType)
            }
            .build<Record>()
            .use { records ->
                Deletes.toPositionIndexes(records, deleteFile).entries.associate {
                    it.key.toString() to it.value
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
        private const val NO_SNAPSHOT = -1L
        private val logger = io.github.oshai.kotlinlogging.KotlinLogging.logger {}
    }
}
