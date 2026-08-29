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
        deleteIndex: DeleteIndexState? = null,
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
                publishDeleteIndex(
                    table,
                    branch,
                    writeResult,
                    deleteIndex,
                    DeleteIndexState.removedLocations(fullySupersededDataFiles),
                )
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
                delta.commit()
                publishDeleteIndex(table, branch, writeResult, deleteIndex, emptySet())
            } else if (writeResult.dataFiles().isNotEmpty()) {
                val append = table.newAppend().toBranch(branch)
                writeResult.dataFiles().forEach(append::appendFile)
                append.commit()
            }
        }
    }

    /**
     * Publishes the deletion-vector index for the snapshot the commit just created.
     *
     * This runs inside the commit lock so the index always describes a snapshot this writer
     * produced, and after the data commit so a failure to write the index cannot fail the sync.
     */
    private fun publishDeleteIndex(
        table: Table,
        branch: String,
        writeResult: WriteResult,
        deleteIndex: DeleteIndexState?,
        removedDataFileLocations: Set<String>,
    ) {
        if (deleteIndex == null || !deleteIndex.enabled) return
        val snapshotId = table.refs()[branch]?.snapshotId() ?: return
        deleteIndex.publish(table, snapshotId, writeResult, removedDataFileLocations)
    }

    private fun registeredDeletes(
        table: Table,
        snapshotId: Long,
        dataFiles: Set<DataFile>,
    ): Set<DeleteFile> {
        val dataFileLocations = dataFiles.map { it.location().toString() }.toSet()
        return table.newScan().useSnapshot(snapshotId).planFiles().use { tasks ->
            val plannedTasks = tasks.toList()
            val deleteReferences =
                plannedTasks
                    .flatMap { task ->
                        task.deletes().map { deleteFile ->
                            deleteFile.location().toString() to task.file().location().toString()
                        }
                    }
                    .groupBy({ it.first }, { it.second })
            plannedTasks
                .filter { task -> dataFileLocations.contains(task.file().location().toString()) }
                .flatMap { task ->
                    task.deletes().filter { deleteFile ->
                        deleteFile.content() == FileContent.POSITION_DELETES &&
                            deleteFile.referencedDataFile() != null &&
                            dataFileLocations.contains(deleteFile.referencedDataFile()) &&
                            deleteReferences[deleteFile.location().toString()]?.toSet()?.size == 1
                    }
                }
                .toSet()
        }
    }
}
