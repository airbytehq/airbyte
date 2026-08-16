/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import org.apache.iceberg.DataFile
import org.apache.iceberg.DeleteFile
import org.apache.iceberg.Table
import org.apache.iceberg.io.WriteResult

object IcebergTableCommitter {
    private val commitLock = Any()

    fun fullySupersededDataFiles(
        table: Table,
        plannedSnapshotId: Long,
        writeResult: WriteResult,
    ): Set<DataFile> {
        val referenced = writeResult.referencedDataFiles().map { it.toString() }.toSet()
        val deleteReferences =
            writeResult
                .deleteFiles()
                .mapNotNull { it.referencedDataFile() }
                .map { it.toString() }
                .toSet()
        val paths = referenced - deleteReferences
        if (paths.isEmpty()) return emptySet()
        return table.newScan().useSnapshot(plannedSnapshotId).planFiles().use { tasks ->
            tasks.map { it.file() }.filter { it.location().toString() in paths }.toSet()
        }
    }

    fun commit(
        table: Table,
        branch: String,
        writeResult: WriteResult,
        plannedSnapshotId: Long,
        fullySupersededDataFiles: Set<DataFile>,
    ) {
        synchronized(commitLock) {
            val hasReferencedDataFiles = writeResult.referencedDataFiles().isNotEmpty()
            if (
                writeResult.deleteFiles().isNotEmpty() ||
                    (writeResult.dataFiles().isNotEmpty() && hasReferencedDataFiles)
            ) {
                val delta =
                    table
                        .newRowDelta()
                        .toBranch(branch)
                        .validateFromSnapshot(plannedSnapshotId)
                        .validateDataFilesExist(writeResult.referencedDataFiles().asIterable())
                        .validateDeletedFiles()
                        .validateNoConflictingDataFiles()
                        .validateNoConflictingDeleteFiles()
                writeResult.dataFiles().forEach(delta::addRows)
                writeResult.deleteFiles().forEach(delta::addDeletes)
                delta.commit()
            } else if (writeResult.dataFiles().isNotEmpty()) {
                val append = table.newAppend().toBranch(branch)
                writeResult.dataFiles().forEach(append::appendFile)
                append.commit()
            }

            if (fullySupersededDataFiles.isNotEmpty()) {
                val deleteFiles =
                    registeredDeletes(table, plannedSnapshotId, fullySupersededDataFiles)
                table
                    .newRewrite()
                    .toBranch(branch)
                    .rewriteFiles(
                        fullySupersededDataFiles,
                        deleteFiles,
                        emptySet(),
                        emptySet(),
                    )
                    .validateFromSnapshot(plannedSnapshotId)
                    .commit()
            }
        }
    }

    private fun registeredDeletes(
        table: Table,
        snapshotId: Long,
        dataFiles: Set<DataFile>,
    ): Set<DeleteFile> {
        val paths = dataFiles.map { it.location().toString() }.toSet()
        return table.newScan().useSnapshot(snapshotId).planFiles().use { tasks ->
            tasks
                .filter { it.file().location().toString() in paths }
                .flatMap { it.deletes().toList() }
                .toSet()
        }
    }
}
