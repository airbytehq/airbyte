/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.util.UUID
import org.apache.iceberg.DeleteFile
import org.apache.iceberg.FileContent
import org.apache.iceberg.FileScanTask
import org.apache.iceberg.MetadataColumns
import org.apache.iceberg.PartitionSpec
import org.apache.iceberg.Schema
import org.apache.iceberg.SnapshotRef
import org.apache.iceberg.StructLike
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.Record
import org.apache.iceberg.data.parquet.GenericParquetReaders
import org.apache.iceberg.deletes.BaseDVFileWriter
import org.apache.iceberg.deletes.Deletes
import org.apache.iceberg.deletes.PositionDeleteIndex
import org.apache.iceberg.io.CloseableIterable
import org.apache.iceberg.io.DeleteSchemaUtil
import org.apache.iceberg.parquet.Parquet
import org.apache.iceberg.types.TypeUtil
import org.apache.iceberg.util.ContentFileUtil

private val logger = KotlinLogging.logger {}

/**
 * Migrates an existing v2 table to Iceberg format version 3 in place, converting every legacy
 * delete file in the current snapshot into deletion vectors so that v3-only readers (which reject
 * v2 equality and position delete files) can read the table.
 *
 * This is a one-way upgrade: format version cannot be lowered afterwards.
 */
object IcebergTableUpgrader {

    /**
     * Upgrades the table identified by [tableId] to format v3. When [backup] is true, the current
     * metadata is first registered under a sibling table named
     * `<name>_v2_backup_<yyyyMMddHHmmss>` (UTC) so the pre-upgrade state remains readable.
     *
     * [branch] is the destination's main branch name; the migration reads from and commits to
     * that branch.
     *
     * No-op when the table is already v3 or newer. Returns the (re)loaded table.
     */
    fun upgradeToV3(
        catalog: Catalog,
        tableId: TableIdentifier,
        backup: Boolean = false,
        branch: String = SnapshotRef.MAIN_BRANCH,
    ): Table {
        val table = catalog.loadTable(tableId)
        val currentVersion = tableFormatVersion(table)
        if (currentVersion >= 3) {
            logger.info {
                "Table $tableId is already at format version v$currentVersion; skipping upgrade."
            }
            return table
        }
        if (backup) {
            registerBackup(catalog, table, tableId)
        }
        val migration = planMigration(table, branch)
        commitUpgrade(table, migration, branch)
        table.refresh()
        val remaining =
            table.newScan().useRef(branch).planFiles().use { tasks ->
                tasks
                    .asSequence()
                    .flatMap { it.deletes().asSequence() }
                    .filter { !ContentFileUtil.isDV(it) }
                    .distinctBy { it.location() }
                    .toList()
            }
        check(remaining.isEmpty()) {
            "Table $tableId still has ${remaining.size} non-deletion-vector delete file(s) " +
                "after the v3 upgrade: ${remaining.map { it.location() }}"
        }
        logger.info { "Upgraded table $tableId to format version v3." }
        return table
    }

    private fun registerBackup(catalog: Catalog, table: Table, tableId: TableIdentifier) {
        val timestamp =
            DateTimeFormatter.ofPattern("yyyyMMddHHmmss")
                .format(LocalDateTime.now(ZoneOffset.UTC))
        val backupId =
            TableIdentifier.of(tableId.namespace(), "${tableId.name()}_v2_backup_$timestamp")
        catalog.registerTable(backupId, currentMetadataFileLocation(table))
        logger.info { "Registered v2 backup table $backupId for $tableId." }
    }

    private fun currentMetadataFileLocation(table: Table): String =
        (table as org.apache.iceberg.HasTableOperations)
            .operations()
            .current()
            .metadataFileLocation()

    private data class MigratedDeletes(
        val legacyDeleteFiles: Set<DeleteFile>,
        val deletionVectors: List<DeleteFile>,
        val rewrittenDeleteFiles: List<DeleteFile>,
    )

    /**
     * Resolves every legacy delete file in the current snapshot to deleted positions and writes a
     * single merged DV per referenced data file.
     */
    private fun planMigration(table: Table, branch: String): MigratedDeletes {
        val tasks = table.newScan().useRef(branch).planFiles().use { it.toList() }
        val dataFileInfo = tasks.associateBy { it.file().location().toString() }
        // (data file path) -> positions to delete, alongside the spec/partition of the data file.
        class Positions(val spec: PartitionSpec, val partition: StructLike?) {
            val positions = mutableListOf<Long>()
        }
        val positionsByDataFile = LinkedHashMap<String, Positions>()
        fun positionsFor(dataFilePath: String): Positions? =
            dataFileInfo[dataFilePath]?.let { task ->
                positionsByDataFile.getOrPut(dataFilePath) {
                    Positions(
                        table.specs()[task.file().specId()]
                            ?: error("Unknown partition spec ${task.file().specId()}"),
                        task.partition(),
                    )
                }
            }

        val legacyDeletes = sortedSetOf<DeleteFile>(compareBy { it.location().toString() })
        val deleteFiles =
            tasks.flatMap { it.deletes() }.distinctBy { it.location().toString() }

        for (deleteFile in deleteFiles) {
            when {
                deleteFile.content() == FileContent.POSITION_DELETES &&
                    !ContentFileUtil.isDV(deleteFile) -> {
                    legacyDeletes += deleteFile
                    readPositionsByDataFile(table, deleteFile).forEach {
                        (dataFilePath, index) ->
                        positionsFor(dataFilePath)?.let { pending ->
                            index.forEach { pos -> pending.positions += pos }
                        }
                    }
                }
                deleteFile.content() == FileContent.EQUALITY_DELETES -> {
                    legacyDeletes += deleteFile
                    resolveEqualityDeletes(table, deleteFile, dataFileInfo, branch).forEach { location ->
                        val info = dataFileInfo[location.path.toString()] ?: return@forEach
                        // Iceberg semantics: an equality delete applies only to data files in the
                        // same spec/partition with a strictly lower data sequence number.
                        if (
                            info.file().specId() == deleteFile.specId() &&
                                info.file().dataSequenceNumber() <
                                    deleteFile.dataSequenceNumber() &&
                                partitionsEqual(info.partition(), location.partition)
                        ) {
                            positionsFor(location.path.toString())?.positions?.add(
                                location.position
                            )
                        }
                    }
                }
            }
        }

        if (positionsByDataFile.isEmpty()) {
            return MigratedDeletes(legacyDeletes, emptyList(), emptyList())
        }
        val locationProvider = table.locationProvider()
        val writer =
            BaseDVFileWriter(
                {
                    table.io()
                        .newOutputFile(
                            locationProvider.newDataLocation("${UUID.randomUUID()}.puffin")
                        )
                }
            ) { path ->
                // Merge an existing DV if the data file already has one.
                deleteFiles
                    .firstOrNull {
                        ContentFileUtil.isDV(it) && it.referencedDataFile()?.toString() == path
                    }
                    ?.let { loadDvIndex(table, it) }
            }
        try {
            positionsByDataFile.forEach { (path, pending) ->
                val index =
                    Deletes.toPositionIndex(
                        CloseableIterable.withNoopClose(pending.positions.toList())
                    )
                writer.delete(path, index, pending.spec, pending.partition)
            }
        } finally {
            writer.close()
        }
        val result = writer.result()
        return MigratedDeletes(legacyDeletes, result.deleteFiles(), result.rewrittenDeleteFiles())
    }

    /**
     * Bumps `format-version` and swaps the legacy delete files for DVs in a single transaction so
     * a failure leaves the table untouched at v2 and a later sync can retry the whole upgrade.
     */
    private fun commitUpgrade(table: Table, migration: MigratedDeletes, branch: String) {
        val transaction = table.newTransaction()
        transaction
            .updateProperties()
            .set(TableProperties.FORMAT_VERSION, "3")
            .commit()
        if (migration.legacyDeleteFiles.isNotEmpty() || migration.deletionVectors.isNotEmpty()) {
            val delta = transaction.newRowDelta().toBranch(branch)
            migration.legacyDeleteFiles.forEach(delta::removeDeletes)
            migration.deletionVectors.forEach(delta::addDeletes)
            migration.rewrittenDeleteFiles.forEach(delta::removeDeletes)
            delta.commit()
        }
        transaction.commitTransaction()
    }

    /** Positions keyed by data-file path for one position delete file. */
    private fun readPositionsByDataFile(
        table: Table,
        deleteFile: DeleteFile,
    ): Map<String, PositionDeleteIndex> {
        val deleteSchema = DeleteSchemaUtil.pathPosSchema()
        return Parquet.read(table.io().newInputFile(deleteFile.location()))
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

    /**
     * Resolves an equality delete file's keys to row positions in the table's data files, reusing
     * the same superseded-row scan the positional delete writer uses.
     */
    private fun resolveEqualityDeletes(
        table: Table,
        deleteFile: DeleteFile,
        dataFileInfo: Map<String, FileScanTask>,
        branch: String,
    ): Sequence<PositionalDeleteResolver.RowLocation> {
        val equalityFieldIds =
            deleteFile.equalityFieldIds()?.toSet()
                ?: table.schema().identifierFieldIds()
        val finder =
            SupersededRowFinder(
                table,
                table.schema(),
                equalityFieldIds,
                PositionalDeleteResolutionState(),
                suppressDeletedPositions = true,
            )
        val keyType = TypeUtil.select(table.schema(), equalityFieldIds).asStruct()
        val touched = TouchedKeys(keyType, Int.MAX_VALUE)
        val recordSchema = TypeUtil.select(table.schema(), equalityFieldIds)
        Parquet.read(table.io().newInputFile(deleteFile.location()))
            .project(recordSchema)
            .createReaderFunc { messageType ->
                GenericParquetReaders.buildReader(recordSchema, messageType)
            }
            .build<Record>()
            .use { records -> records.forEach { touched.markDeleted(it) } }
        return finder.find(touched, branch).asIterable().let { locations ->
            // Restrict to data files in the delete file's own spec with a strictly lower data
            // sequence number.
            locations
                .asSequence()
                .filter { location ->
                    dataFileInfo[location.path.toString()]
                        ?.file()
                        ?.let {
                            it.specId() == deleteFile.specId() &&
                                it.dataSequenceNumber() < deleteFile.dataSequenceNumber()
                        } == true
                }
        }
    }

    private fun partitionsEqual(left: StructLike?, right: StructLike?): Boolean {
        if (left == null || right == null) return left == right
        if (left.size() != right.size()) return false
        return (0 until left.size()).all { left.get(it, Any::class.java) == right.get(it, Any::class.java) }
    }

    private fun loadDvIndex(table: Table, dv: DeleteFile): PositionDeleteIndex {
        val input = table.io().newInputFile(dv.location())
        org.apache.iceberg.puffin.Puffin.read(input)
            .withFileSize(dv.fileSizeInBytes())
            .build()
            .use { reader ->
                val blobs =
                    reader
                        .fileMetadata()
                        .blobs()
                        .filter { it.offset() == dv.contentOffset() }
                        .toList()
                val blobData =
                    reader.readAll(blobs).singleOrNull()?.second()
                        ?: error("No deletion-vector blob found in ${dv.location()}")
                val bytes = ByteArray(blobData.remaining())
                blobData.get(bytes)
                return PositionDeleteIndex.deserialize(bytes, dv)
            }
    }
}
