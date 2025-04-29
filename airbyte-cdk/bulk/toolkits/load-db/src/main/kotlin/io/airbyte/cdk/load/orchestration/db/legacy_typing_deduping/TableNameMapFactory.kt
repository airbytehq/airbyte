/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.RawTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.micronaut.context.annotation.Factory
import javax.inject.Singleton
import org.apache.commons.codec.digest.DigestUtils

data class TableNameInfo(val tableNames: TableNames, val columnNameMapping: ColumnNameMapping)

data class TableCatalog(private val catalog: Map<DestinationStream, TableNameInfo>) :
    Map<DestinationStream, TableNameInfo> by catalog

data class TableCatalogByDescriptor(
    private val catalog: Map<DestinationStream.Descriptor, TableNameInfo>
) : Map<DestinationStream.Descriptor, TableNameInfo> by catalog

@Factory
class TableCatalogFactory(
    private val catalog: DestinationCatalog,
    private val rawTableNameGenerator: RawTableNameGenerator,
    private val finalTableNameGenerator: FinalTableNameGenerator,
    private val finalTableColumnNameGenerator: ColumnNameGenerator,
) {
    @Singleton
    fun get(): TableCatalog {
        val processedRawTableNames = mutableSetOf<String>()
        val processedFinalTableNames = mutableSetOf<String>()

        return TableCatalog(
            catalog.streams.associateWith { stream ->
                val originalRawTableName = rawTableNameGenerator.getTableName(stream.descriptor)
                val originalFinalTableName = finalTableNameGenerator.getTableName(stream.descriptor)

                // Handle raw table name collisions
                val finalRawTableName =
                    resolveTableNameCollision(originalRawTableName, processedRawTableNames)

                // Handle final table name collisions
                val finalFinalTableName =
                    resolveTableNameCollision(originalFinalTableName, processedFinalTableNames)

                // Create column name mapping with collision handling
                val columnNameMapping = createColumnNameMapping(stream)

                TableNameInfo(
                    TableNames(
                        rawTableName = finalRawTableName,
                        finalTableName = finalFinalTableName,
                    ),
                    columnNameMapping
                )
            }
        )
    }

    /**
     * Resolves table name collisions by adding a hash suffix when needed. Adds the processed name
     * to the tracking set.
     */
    private fun resolveTableNameCollision(
        originalName: TableName,
        processedNames: MutableSet<String>
    ): TableName {
        val nameStr = originalName.toPrettyString()

        return if (nameStr in processedNames) {
            // Create a hash-suffixed name to avoid collision
            val hash =
                DigestUtils.sha1Hex("${originalName.namespace}&airbyte&${originalName.name}")
                    .substring(0, 6)
            val newName = "${originalName.name}_$hash"
            TableName(originalName.namespace, newName).also {
                processedNames.add(it.toPrettyString())
            }
        } else {
            // Use original name and add to processed set
            processedNames.add(nameStr)
            originalName
        }
    }

    /**
     * Creates column name mapping with handling for potential collisions using incremental
     * numbering.
     */
    private fun createColumnNameMapping(stream: DestinationStream): ColumnNameMapping {
        val processedColumnNames = mutableSetOf<String>()
        val columnMappings = mutableMapOf<String, String>()

        stream.schema.asColumns().forEach { (columnName, _) ->
            val originalColumnName =
                finalTableColumnNameGenerator.getColumnName(columnName).displayName

            // Get a unique column name by adding incremental numbers if necessary
            val finalColumnName = getUniqueColumnName(originalColumnName, processedColumnNames)

            processedColumnNames.add(finalColumnName)
            columnMappings[columnName] = finalColumnName
        }

        return ColumnNameMapping(columnMappings)
    }

    /**
     * Finds a unique column name by adding incremental numeric suffixes if needed. Starts with the
     * original name, then tries adding _1, _2, etc. until a unique name is found.
     */
    private fun getUniqueColumnName(originalName: String, existingNames: Set<String>): String {
        // If original name is unique, use it
        if (originalName !in existingNames) {
            return originalName
        }

        // Try adding incremental suffixes until we find a non-colliding name
        var counter = 1
        var candidateName: String

        do {
            candidateName = "${originalName}_$counter"
            counter++
        } while (candidateName in existingNames)

        return candidateName
    }
}

@Factory
class TableCatalogByDescriptorFactory(
    private val map: TableCatalog,
) {
    @Singleton
    fun get(): TableCatalogByDescriptor {
        return TableCatalogByDescriptor(map.mapKeys { (k, _) -> k.descriptor })
    }
}
