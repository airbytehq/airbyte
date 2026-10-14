/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import java.util.concurrent.ConcurrentHashMap
import org.apache.iceberg.DataFile
import org.apache.iceberg.DeleteFile
import org.apache.iceberg.FileContent
import org.apache.iceberg.Table
import org.apache.iceberg.io.WriteResult

object IcebergTableCommitter {
    private val commitLocks = ConcurrentHashMap<String, Any>()

    @Suppress("DEPRECATION")
    fun commit(
        table: Table,
        branch: String,
        writeResult: WriteResult,
        plannedSnapshotId: Long,
        fullySupersededDataFiles: Set<DataFile>,
        rewrittenDeleteFiles: Set<DeleteFile> = emptySet(),
    ) {
        synchronized(commitLocks.computeIfAbsent("${table.name()}::$branch") { Any() }) {
            if (fullySupersededDataFiles.isNotEmpty()) {
                val deleteFiles =
                    registeredDeletes(table, plannedSnapshotId, fullySupersededDataFiles)
                val transaction = table.newTransaction()
                val delta =
                    transaction
                        .newRowDelta()
                        .toBranch(branch)
                        .validateFromSnapshot(plannedSnapshotId)
                        .validateDataFilesExist(writeResult.referencedDataFiles().asIterable())
                        .validateDeletedFiles()
                        .validateNoConflictingDataFiles()
                        .validateNoConflictingDeleteFiles()
                writeResult.dataFiles().forEach(delta::addRows)
                writeResult.deleteFiles().forEach(delta::addDeletes)
                rewrittenDeleteFiles.forEach(delta::removeDeletes)
                delta.commit()
                val rewriteSnapshotId =
                    transaction.table().refs()[branch]?.snapshotId() ?: plannedSnapshotId
                transaction
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
                transaction.commitTransaction()
            } else if (
                writeResult.deleteFiles().isNotEmpty() ||
                    (writeResult.dataFiles().isNotEmpty() &&
                        writeResult.referencedDataFiles().isNotEmpty())
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
                rewrittenDeleteFiles.forEach(delta::removeDeletes)
                delta.commit()
            } else if (writeResult.dataFiles().isNotEmpty()) {
                val append = table.newAppend().toBranch(branch)
                writeResult.dataFiles().forEach(append::appendFile)
                append.commit()
            }
        }
    }

    private fun registeredDeletes(
        table: Table,
        snapshotId: Long,
        dataFiles: Set<DataFile>,
    ): Set<DeleteFile> {
        val dataFileLocations = dataFiles.map { it.location() }.toSet()
        return table.newScan().useSnapshot(snapshotId).planFiles().use { tasks ->
            val plannedTasks = tasks.toList()
            val deleteReferences =
                plannedTasks
                    .flatMap { task ->
                        task.deletes().map { deleteFile ->
                            deleteFile.location() to task.file().location()
                        }
                    }
                    .groupBy({ it.first }, { it.second })
            plannedTasks
                .filter { task -> dataFileLocations.contains(task.file().location()) }
                .flatMap { task ->
                    task.deletes().filter { deleteFile ->
                        deleteFile.content() == FileContent.POSITION_DELETES &&
                            deleteFile.referencedDataFile() != null &&
                            dataFileLocations.contains(deleteFile.referencedDataFile()) &&
                            deleteReferences[deleteFile.location()]?.toSet()?.size == 1
                    }
                }
                .toSet()
        }
    }
}
