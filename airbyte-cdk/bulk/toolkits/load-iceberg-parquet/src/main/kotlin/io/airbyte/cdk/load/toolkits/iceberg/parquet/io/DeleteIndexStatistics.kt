/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.github.oshai.kotlinlogging.KotlinLogging
import java.security.MessageDigest
import java.util.UUID
import org.apache.iceberg.ContentFile
import org.apache.iceberg.FileFormat
import org.apache.iceberg.FileMetadata
import org.apache.iceberg.GenericBlobMetadata
import org.apache.iceberg.GenericStatisticsFile
import org.apache.iceberg.HasTableOperations
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.StatisticsFile
import org.apache.iceberg.Table
import org.apache.iceberg.deletes.PositionDeleteIndex
import org.apache.iceberg.puffin.Blob
import org.apache.iceberg.puffin.Puffin
import org.apache.iceberg.puffin.StandardBlobTypes

private val logger = KotlinLogging.logger {}

/**
 * Deletion-vector blobs for committed positional deletes, stored as Iceberg table statistics.
 *
 * Each blob holds the deleted row positions of one data file, encoded with the Iceberg
 * deletion-vector format so the same bytes can later be referenced by v3 deletion-vector delete
 * files. The blobs are registered as a [StatisticsFile] rather than as delete files: the positional
 * delete files remain the only delete metadata readers see, which keeps the table readable by v2
 * engines. The index is therefore an accelerator for later syncs, never a source of truth.
 *
 * Statistics are attached to a snapshot, not to individual data files, so every entry records the
 * state it was derived from: the referenced data file, that file's record count, and a digest of
 * the delete files it covers. An entry is used only when all three still match the planned scan,
 * which makes rewrites, compaction, and any other third-party change fall back to reading delete
 * files instead of trusting positions that no longer describe the file.
 */
object DeleteIndexStatistics {
    /** Airbyte-owned blob properties, alongside the standard deletion-vector properties. */
    const val REFERENCED_DATA_FILE_PROPERTY = "referenced-data-file"
    const val CARDINALITY_PROPERTY = "cardinality"
    const val DATA_FILE_RECORD_COUNT_PROPERTY = "airbyte-data-file-record-count"
    const val COVERED_DELETES_PROPERTY = "airbyte-covered-deletes"

    /** Entries above this count are pruned against the current snapshot before being carried. */
    const val CARRY_FORWARD_PRUNE_THRESHOLD = 10_000

    data class Entry(
        val dataFileLocation: String,
        val dataFileRecordCount: Long,
        val coveredDeletesDigest: String,
        val cardinality: Long,
        val blobData: java.nio.ByteBuffer,
    )

    /** A digest of the delete files an index covers, used to detect any change to that set. */
    fun coveredDeletesDigest(deleteFiles: Iterable<ContentFile<*>>): String {
        val digest = MessageDigest.getInstance("SHA-256")
        deleteFiles
            .map { "${it.location()}:${it.recordCount()}\u0000" }
            .sorted()
            .forEach { digest.update(it.toByteArray(Charsets.UTF_8)) }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }

    /**
     * Reads the newest statistics file that holds delete-index blobs.
     *
     * Only the newest is read: [write] carries forward the entries it does not replace, so older
     * statistics files hold strictly staler copies of the same data files.
     */
    fun read(table: Table): Map<String, Entry> {
        val statisticsFile = newestIndexStatisticsFile(table) ?: return emptyMap()
        return try {
            readEntries(table, statisticsFile)
        } catch (e: Exception) {
            logger.warn(e) {
                "Unable to read the delete index at ${statisticsFile.path()}; " +
                    "this flush will read prior delete files instead"
            }
            emptyMap()
        }
    }

    /**
     * Returns [stored] when it still describes [dataFileRecordCount] and [plannedDeletes] exactly.
     *
     * A match means every position in the blob is a position in the data file as it exists now, and
     * that the blob accounts for the same delete files the scan planned. Anything else - a
     * rewritten or compacted data file, a delete file added or removed by another writer, a blob
     * written before an unrelated commit - fails the check and forces the caller to read delete
     * files.
     */
    fun validEntry(
        stored: Entry?,
        dataFileLocation: String,
        dataFileRecordCount: Long,
        plannedDeletes: Iterable<ContentFile<*>>,
    ): Entry? {
        if (stored == null) return null
        if (stored.dataFileLocation != dataFileLocation) return null
        if (stored.dataFileRecordCount != dataFileRecordCount) return null
        if (stored.coveredDeletesDigest != coveredDeletesDigest(plannedDeletes)) return null
        if (stored.cardinality > dataFileRecordCount) return null
        return stored
    }

    /** Deserializes a validated [Entry] into a position index. */
    fun toIndex(entry: Entry): PositionDeleteIndex {
        val bytes = ByteArray(entry.blobData.remaining())
        entry.blobData.duplicate().get(bytes)
        return PositionDeleteIndex.deserialize(
            bytes,
            syntheticDeleteFile(entry, bytes.size.toLong()),
        )
    }

    /**
     * Writes [entries] plus the still-valid entries of the previous statistics file, and registers
     * the result for [snapshotId].
     *
     * Registering statistics for a snapshot replaces only that snapshot's entry, so the previous
     * statistics file is removed once its live entries have been carried forward. Failures are
     * logged and swallowed by callers: an absent or partial index only costs a later flush the work
     * of reading delete files.
     */
    fun write(
        table: Table,
        snapshotId: Long,
        entries: Collection<Entry>,
        removedDataFileLocations: Set<String> = emptySet(),
    ): StatisticsFile? {
        val previous = newestIndexStatisticsFile(table)
        val carried =
            previous
                ?.let { file ->
                    try {
                        readEntries(table, file)
                    } catch (e: Exception) {
                        logger.warn(e) { "Unable to carry forward the index at ${file.path()}" }
                        emptyMap()
                    }
                }
                .orEmpty()
                .filterKeys { location ->
                    location !in removedDataFileLocations &&
                        entries.none { it.dataFileLocation == location }
                }
        val pruned =
            if (carried.size > CARRY_FORWARD_PRUNE_THRESHOLD) {
                pruneToCurrentDataFiles(table, snapshotId, carried)
            } else {
                carried
            }
        val all = entries + pruned.values
        if (all.isEmpty()) {
            return null
        }
        val path = statisticsPath(table, snapshotId)
        val outputFile = table.io().newOutputFile(path)
        val writer = Puffin.write(outputFile).createdBy("Airbyte").build()
        val blobMetadata =
            writer.use { puffin ->
                all.forEach { entry ->
                    puffin.write(
                        Blob(
                            StandardBlobTypes.DV_V1,
                            emptyList(),
                            snapshotId,
                            SEQUENCE_NUMBER_UNKNOWN,
                            entry.blobData.duplicate(),
                            null,
                            mapOf(
                                REFERENCED_DATA_FILE_PROPERTY to entry.dataFileLocation,
                                CARDINALITY_PROPERTY to entry.cardinality.toString(),
                                DATA_FILE_RECORD_COUNT_PROPERTY to
                                    entry.dataFileRecordCount.toString(),
                                COVERED_DELETES_PROPERTY to entry.coveredDeletesDigest,
                            ),
                        )
                    )
                }
                puffin.finish()
                puffin.writtenBlobsMetadata().map(GenericBlobMetadata::from)
            }
        val statisticsFile =
            GenericStatisticsFile(
                snapshotId,
                path,
                writer.fileSize(),
                writer.footerSize(),
                blobMetadata,
            )
        val update = table.updateStatistics().setStatistics(statisticsFile)
        previous
            ?.takeIf { it.snapshotId() != snapshotId }
            ?.let { update.removeStatistics(it.snapshotId()) }
        update.commit()
        return statisticsFile
    }

    private fun readEntries(table: Table, statisticsFile: StatisticsFile): Map<String, Entry> {
        val inputFile = table.io().newInputFile(statisticsFile.path())
        return Puffin.read(inputFile)
            .withFileSize(statisticsFile.fileSizeInBytes())
            .withFooterSize(statisticsFile.fileFooterSizeInBytes())
            .build()
            .use { reader ->
                val blobs =
                    reader.fileMetadata().blobs().filter { it.type() == StandardBlobTypes.DV_V1 }
                reader
                    .readAll(blobs)
                    .mapNotNull { pair ->
                        val metadata = pair.first()
                        val data = pair.second()
                        val location = metadata.properties()[REFERENCED_DATA_FILE_PROPERTY]
                        val recordCount =
                            metadata.properties()[DATA_FILE_RECORD_COUNT_PROPERTY]?.toLongOrNull()
                        val digest = metadata.properties()[COVERED_DELETES_PROPERTY]
                        if (location == null || recordCount == null || digest == null) {
                            null
                        } else {
                            location to
                                Entry(
                                    dataFileLocation = location,
                                    dataFileRecordCount = recordCount,
                                    coveredDeletesDigest = digest,
                                    cardinality =
                                        metadata.properties()[CARDINALITY_PROPERTY]?.toLongOrNull()
                                            ?: 0,
                                    blobData = data,
                                )
                        }
                    }
                    .toMap()
            }
    }

    /**
     * Drops entries for data files that are no longer in [snapshotId].
     *
     * Carrying entries forward keeps one authoritative statistics file per snapshot, but a table
     * whose data files are steadily replaced would otherwise accumulate dead entries. This is a
     * metadata-only scan, so it runs only once the carried set is large enough to be worth it.
     */
    private fun pruneToCurrentDataFiles(
        table: Table,
        snapshotId: Long,
        carried: Map<String, Entry>,
    ): Map<String, Entry> =
        try {
            val live =
                table.newScan().useSnapshot(snapshotId).planFiles().use { tasks ->
                    tasks.map { it.file().location().toString() }.toSet()
                }
            carried.filterKeys { it in live }
        } catch (e: Exception) {
            logger.warn(e) { "Unable to prune the delete index; keeping all carried entries" }
            carried
        }

    private fun newestIndexStatisticsFile(table: Table): StatisticsFile? =
        table
            .statisticsFiles()
            .filter { file -> file.blobMetadata().any { it.type() == StandardBlobTypes.DV_V1 } }
            .maxByOrNull { it.snapshotId() }

    private fun statisticsPath(table: Table, snapshotId: Long): String {
        val name = "airbyte-delete-index-$snapshotId-${UUID.randomUUID()}.puffin"
        val operations = (table as? HasTableOperations)?.operations()
        return operations?.metadataFileLocation(name) ?: "${table.location()}/metadata/$name"
    }

    /**
     * A stand-in delete file for [PositionDeleteIndex.deserialize], which uses it to check the blob
     * length and cardinality and to attribute the index. The index is read from statistics, so
     * there is no delete file to attribute it to.
     */
    private fun syntheticDeleteFile(entry: Entry, sizeInBytes: Long) =
        FileMetadata.deleteFileBuilder(PartitionSpec.unpartitioned())
            .ofPositionDeletes()
            .withReferencedDataFile(entry.dataFileLocation)
            .withPath("airbyte-delete-index")
            .withFormat(FileFormat.PUFFIN)
            .withFileSizeInBytes(sizeInBytes)
            .withContentOffset(0)
            .withContentSizeInBytes(sizeInBytes)
            .withRecordCount(entry.cardinality)
            .build()

    private const val SEQUENCE_NUMBER_UNKNOWN = -1L
}
