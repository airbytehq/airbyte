/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import org.apache.iceberg.DataFile
import org.apache.iceberg.DeleteFile
import org.apache.iceberg.FileContent
import org.apache.iceberg.Table
import org.apache.iceberg.io.WriteResult
import java.util.concurrent.ConcurrentHashMap

object IcebergTableCommitter {
    private val commitLocks = ConcurrentHashMap<String, Any>()

    @Suppress("DEPRECATION")
    fun commit(
        table: Table,
        branch: String,
        writeResult: WriteResult,
        plannedSnapshotId: Long,
        fullySupersededDataFiles: Set<DataFile>,
    ) {
        synchronized(commitLocks.computeIfAbsent("${table.name()}::$branch") { Any() }) {
            var rewriteSnapshotId = plannedSnapshotId
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
                rewriteSnapshotId = table.refs()[branch]?.snapshotId() ?: plannedSnapshotId
            } else if (writeResult.dataFiles().isNotEmpty()) {
                val append = table.newAppend().toBranch(branch)
                writeResult.dataFiles().forEach(append::appendFile)
                append.commit()
            }

            if (fullySupersededDataFiles.isNotEmpty()) {
                val deleteFiles =
                    registeredDeletes(table, rewriteSnapshotId, fullySupersededDataFiles)
                table
                    .newRewrite()
                    .toBranch(branch)
                    .rewriteFiles(
                        fullySupersededDataFiles,
                        deleteFiles,
                        emptySet(),
                        emptySet(),
                    )
                    .validateFromSnapshot(rewriteSnapshotId)
                    .commit()
            }
        }
    }

    private fun registeredDeletes(
        table: Table,
        snapshotId: Long,
        dataFiles: Set<DataFile>,
    ): Set<DeleteFile> {
        val dataFileLocations = dataFiles.map { it.location().toString() }.toSet()
        return table.newScan().useSnapshot(snapshotId).planFiles().use { tasks ->
            tasks
                .filter { task -> dataFileLocations.contains(task.file().location().toString()) }
                .flatMap { task ->
                    task.deletes().filter { deleteFile ->
                        deleteFile.content() == FileContent.POSITION_DELETES &&
                            deleteFile.referencedDataFile() != null &&
                            dataFileLocations.contains(deleteFile.referencedDataFile())
                    }
                }
                .toSet()
        }
    }
}
