/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ConcurrentHashMap
import org.apache.iceberg.ContentFile
import org.apache.iceberg.DataFile
import org.apache.iceberg.DeleteFile
import org.apache.iceberg.Table
import org.apache.iceberg.deletes.Deletes
import org.apache.iceberg.deletes.PositionDeleteIndex
import org.apache.iceberg.deletes.PositionDeleteIndexUtil
import org.apache.iceberg.io.CloseableIterable
import org.apache.iceberg.io.WriteResult

private val logger = KotlinLogging.logger {}

/**
 * Stream-scoped tracking of the deletion-vector index described by [DeleteIndexStatistics].
 *
 * A flush reads the index to learn which positions of a data file are already deleted, then records
 * the positions it deletes so the commit can publish an updated index. When [enabled] is false
 * nothing is read or written and callers keep reading prior delete files directly.
 */
class DeleteIndexState(val enabled: Boolean = false) {
    private val observed = ConcurrentHashMap<String, ObservedDataFile>()
    private val cache = ConcurrentHashMap<String, DeleteIndexStatistics.Entry>()

    @Volatile private var cachedSnapshotId: Long? = null

    /** Discards the previous flush's observations. */
    internal fun beginFlush() {
        observed.clear()
    }

    /**
     * The index entries published for [snapshotId], preferring the copy this writer just published.
     *
     * The cache only avoids re-reading a file this writer wrote; entries are validated against the
     * planned scan either way, so a stale or absent cache cannot change what is deleted.
     */
    internal fun entries(table: Table, snapshotId: Long): Map<String, DeleteIndexStatistics.Entry> {
        if (!enabled) return emptyMap()
        if (cachedSnapshotId == snapshotId) return cache
        val entries = DeleteIndexStatistics.read(table)
        cache.clear()
        cache.putAll(entries)
        cachedSnapshotId = snapshotId
        return cache
    }

    /** Records the state a data file was resolved against, before this flush deletes from it. */
    internal fun observe(
        dataFileLocation: String,
        recordCount: Long,
        plannedDeletes: List<ContentFile<*>>,
        priorIndex: PositionDeleteIndex?,
    ) {
        if (!enabled) return
        observed[dataFileLocation] = ObservedDataFile(recordCount, plannedDeletes, priorIndex)
    }

    /** Records a position this flush deletes from [dataFileLocation]. */
    internal fun recordDeleted(dataFileLocation: String, position: Long) {
        if (!enabled) return
        observed
            .computeIfAbsent(dataFileLocation) {
                ObservedDataFile(UNKNOWN_RECORD_COUNT, emptyList(), null)
            }
            .deletedPositions
            .add(position)
    }

    /**
     * Publishes the index for the snapshot this flush produced.
     *
     * The index is an accelerator, so any failure is logged and dropped: the next flush reads
     * delete files instead. Data files removed by the commit are left out, and the entries this
     * call writes become the cache for the next flush.
     */
    internal fun publish(
        table: Table,
        snapshotId: Long,
        writeResult: WriteResult,
        removedDataFileLocations: Set<String>,
    ) {
        if (!enabled) return
        if (observed.isEmpty() && removedDataFileLocations.isEmpty()) return
        try {
            val newDeletesByDataFile =
                writeResult
                    .deleteFiles()
                    .filter { it.referencedDataFile() != null }
                    .groupBy { it.referencedDataFile()!! }
            val newDataFileRecordCounts =
                writeResult.dataFiles().associate { it.location().toString() to it.recordCount() }
            val entries =
                observed
                    .filterKeys { it !in removedDataFileLocations }
                    .mapNotNull { (location, file) ->
                        entryFor(location, file, newDeletesByDataFile, newDataFileRecordCounts)
                    }
            val statisticsFile =
                DeleteIndexStatistics.write(table, snapshotId, entries, removedDataFileLocations)
            if (statisticsFile != null) {
                cache.keys.removeAll(removedDataFileLocations)
                entries.forEach { cache[it.dataFileLocation] = it }
                cachedSnapshotId = snapshotId
            }
        } catch (e: Exception) {
            logger.warn(e) {
                "Unable to publish the delete index for snapshot $snapshotId of ${table.name()}; " +
                    "later flushes will read prior delete files instead"
            }
            cachedSnapshotId = null
        }
    }

    private fun entryFor(
        location: String,
        file: ObservedDataFile,
        newDeletesByDataFile: Map<String, List<DeleteFile>>,
        newDataFileRecordCounts: Map<String, Long>,
    ): DeleteIndexStatistics.Entry? {
        val recordCount =
            if (file.recordCount == UNKNOWN_RECORD_COUNT) {
                newDataFileRecordCounts[location] ?: return null
            } else {
                file.recordCount
            }
        val newDeletes = newDeletesByDataFile[location].orEmpty()
        val deletedPositions = file.deletedPositions.toList()
        if (deletedPositions.isEmpty() && file.priorIndex == null) {
            return null
        }
        val index =
            PositionDeleteIndexUtil.merge(
                listOfNotNull(
                    file.priorIndex,
                    Deletes.toPositionIndex(CloseableIterable.withNoopClose(deletedPositions)),
                )
            )
        return DeleteIndexStatistics.Entry(
            dataFileLocation = location,
            dataFileRecordCount = recordCount,
            coveredDeletesDigest =
                DeleteIndexStatistics.coveredDeletesDigest(file.plannedDeletes + newDeletes),
            cardinality = index.cardinality(),
            blobData = index.serialize(),
        )
    }

    private class ObservedDataFile(
        val recordCount: Long,
        val plannedDeletes: List<ContentFile<*>>,
        val priorIndex: PositionDeleteIndex?,
    ) {
        val deletedPositions: MutableList<Long> =
            java.util.Collections.synchronizedList(mutableListOf())
    }

    companion object {
        private const val UNKNOWN_RECORD_COUNT = -1L

        /** Locations of the data files a commit removes, whose index entries must be dropped. */
        fun removedLocations(dataFiles: Set<DataFile>): Set<String> =
            dataFiles.map { it.location().toString() }.toSet()
    }
}
