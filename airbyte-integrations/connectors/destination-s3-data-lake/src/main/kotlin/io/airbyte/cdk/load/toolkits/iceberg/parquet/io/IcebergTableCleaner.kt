/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

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

    fun deleteGenerationId(
        table: Table,
        stagingBranchName: String,
        generationIdSuffix: List<String>
    ) {
        val genIdsToDelete =
            generationIdSuffix
                .filter {
                    icebergUtil.assertGenerationIdSuffixIsOfValidFormat(it)
                    true
                }
                .toSet()

        table.newScan().planFiles().use { tasks ->
            tasks
                .filter { task -> genIdsToDelete.any { id -> task.file().location().contains(id) } }
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
