/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.command.DestinationStream
import jakarta.inject.Singleton
import org.apache.iceberg.Table
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.io.FileIO
import org.apache.iceberg.io.SupportsPrefixOperations

/**
 * Removes all data from an Iceberg [org.apache.iceberg.Table]. This method is necessary as some
 * catalog implementations do not clear the underlying files written to table storage.
 */
@Singleton
class IcebergTableCleaner(private val icebergUtil: IcebergUtil) {

    /**
     * Clears the table identified by the provided [TableIdentifier]. This removes all data and
     * files associated with the [org.apache.iceberg.Table].
     *
     * @param catalog The [Catalog] that is used to drop the [org.apache.iceberg.Table].
     * @param identifier The [TableIdentifier] that identifies the [org.apache.iceberg.Table] to be
     * cleared.
     * @param io The [FileIO] that may be used to delete the underlying data and metadata files.
     * @param tableLocation The storage location of files associated with the
     * [org.apache.iceberg.Table].
     */
    fun clearTable(
        catalog: Catalog,
        identifier: TableIdentifier,
        io: FileIO,
        tableLocation: String
    ) {
        catalog.dropTable(identifier, true)
        if (io is SupportsPrefixOperations) {
            io.deletePrefix(tableLocation)
        }
    }

    fun deleteOldGenerationData(
        table: Table,
        stagingBranchName: String,
        stream: DestinationStream
    ) {
        val currentGenerationIdSuffix = icebergUtil.constructGenerationIdSuffix(stream)

        table.newScan().planFiles().use { tasks ->
            tasks
                .filter { task ->
                    // Delete file if it doesn't contain the current generation ID prefix
                    // This will also include any potential compaction file from previous generation
                    // WARNING: This approach only works if users do not run compaction while the
                    // truncate refresh sync is running. If compaction occurs during the sync, files
                    // from the current generation may be renamed and lose their generation ID
                    // suffix, causing them to be incorrectly deleted and resulting in data loss.
                    // -------
                    !task.file().location().contains(currentGenerationIdSuffix)
                }
                .forEach { task ->
                    table
                        .newDelete()
                        .toBranch(stagingBranchName)
                        .deleteFile(task.file().location())
                        .commit()
                }
        }
    }
}
