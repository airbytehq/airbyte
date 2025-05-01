/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.DestinationStream.Descriptor
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.RawTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.micronaut.context.annotation.Factory
import javax.inject.Singleton
import org.apache.commons.codec.digest.DigestUtils

const val DEFAULT_AIRBYTE_INTERNAL_NAMESPACE = "airbyte_internal"

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
        if (catalog.streams.isEmpty()) {
            throw ConfigErrorException(
                "The catalog contained no streams. This likely indicates a platform/configuration error."
            )
        }

        val processedRawTableNames = mutableSetOf<TableName>()
        val processedFinalTableNames = mutableSetOf<TableName>()

        val result = mutableMapOf<DestinationStream, TableNameInfo>()

        catalog.streams.forEach { stream ->
            val originalRawTableName = rawTableNameGenerator.getTableName(stream.descriptor)
            val originalFinalTableName = finalTableNameGenerator.getTableName(stream.descriptor)
            val currentRawProcessedName: TableName
            val currentFinalProcessedName: TableName

            // Create a hash-suffixed name to avoid collision
            val hash =
                DigestUtils.sha1Hex(
                        "${originalFinalTableName.namespace}&airbyte&${stream.descriptor.name}"
                    )
                    .substring(0, 3)
            val newName = "${stream.descriptor.name}_$hash"

            if (originalRawTableName in processedRawTableNames) {
                currentRawProcessedName =
                    TableName(
                        originalRawTableName.namespace.takeUnless { it.isEmpty() }
                            ?: DEFAULT_AIRBYTE_INTERNAL_NAMESPACE,
                        newName
                    )
                processedRawTableNames.add(currentRawProcessedName)
            } else {
                processedRawTableNames.add(originalRawTableName)
                currentRawProcessedName = originalRawTableName
            }

            if (originalFinalTableName in processedFinalTableNames) {
                currentFinalProcessedName = TableName(originalFinalTableName.namespace, newName)
                processedFinalTableNames.add(currentFinalProcessedName)
            } else {
                processedFinalTableNames.add(originalFinalTableName)
                currentFinalProcessedName = originalFinalTableName
            }

            // Create column name mapping with collision handling
            val columnNameMapping = createColumnNameMapping(stream)

            result[stream] =
                TableNameInfo(
                    TableNames(
                        rawTableName = currentRawProcessedName,
                        finalTableName = currentFinalProcessedName,
                    ),
                    columnNameMapping
                )
        }

        return TableCatalog(result)
    }

    /**
     * Creates column name mapping with handling for potential collisions using incremental
     * numbering, with advanced resolution for truncation cases.
     */
    private fun createColumnNameMapping(stream: DestinationStream): ColumnNameMapping {
        val processedColumnNames = mutableSetOf<String>()
        val columnMappings = mutableMapOf<String, String>()
        // Map to track original column names by their truncated versions
        val originalColumnNameMap = mutableMapOf<String, String>()

        stream.schema.asColumns().forEach { (columnName, _) ->
            val processedColumnName =
                finalTableColumnNameGenerator.getColumnName(columnName).canonicalName

            // Store mapping between processed name and original name
            originalColumnNameMap[processedColumnName] = columnName

            // Get a unique column name by adding incremental numbers if necessary
            val finalColumnName =
                resolveColumnNameCollision(
                    processedColumnName,
                    existingNames = processedColumnNames,
                    originalColumnName = columnName
                )

            processedColumnNames.add(finalColumnName)
            columnMappings[columnName] = finalColumnName
        }

        return ColumnNameMapping(columnMappings)
    }

    /**
     * Resolves column name collisions by first trying incremental suffixes (_1, _2, etc.) If that
     * doesn't work due to name truncation, uses the more powerful superResolveColumnCollisions.
     *
     * @param processedName The name after initial processing by the column name generator
     * @param existingNames Set of names already used for other columns
     * @param originalColumnName The original column name before processing
     */
    private fun resolveColumnNameCollision(
        processedName: String,
        existingNames: Set<String>,
        originalColumnName: String
    ): String {
        // If processed name is unique, use it
        if (processedName !in existingNames) {
            return processedName
        }

        // Try adding incremental suffixes until we find a non-colliding name
        var counter = 1
        var candidateName: String
        var previousCandidate = processedName

        do {
            // Generate candidate name by adding numeric suffix
            candidateName =
                finalTableColumnNameGenerator
                    .getColumnName("${originalColumnName}_$counter")
                    .canonicalName

            // Check if we're making progress (detecting potential truncation)
            if (candidateName == previousCandidate) {
                // We're not making progress, likely due to name truncation
                // Use the more powerful resolution method with the ORIGINAL column name
                return superResolveColumnCollisions(
                    originalColumnName,
                    existingNames,
                    processedName.length
                )
            }

            previousCandidate = candidateName
            counter++
        } while (candidateName in existingNames)

        return candidateName
    }

    /**
     * Generates a name of the format `<prefix><length><suffix>` when simple suffix-based conflict
     * resolution fails due to name truncation. E.g. for affixLength=3: "veryLongName" -> "ver6ame"
     *
     * @param originalName The original column name that caused collision
     * @param existingNames Set of existing column names to avoid collision with
     * @param maximumColumnNameLength The maximum allowed length for the column name
     */
    private fun superResolveColumnCollisions(
        originalName: String,
        existingNames: Set<String>,
        maximumColumnNameLength: Int
    ): String {
        // Assume that the <length> portion can be expressed in at most 5 characters.
        // If someone is giving us a column name that's longer than 99999 characters,
        // that's just being silly.
        val affixLength = (maximumColumnNameLength - 5) / 2

        // If, after reserving 5 characters for the length, we can't fit the affixes,
        // just give up. That means the destination is trying to restrict us to a
        // 6-character column name, which is just silly.
        if (affixLength <= 0) {
            throw IllegalArgumentException(
                "Cannot solve column name collision: $originalName. We recommend removing this column to continue syncing."
            )
        }

        val prefix = originalName.substring(0, affixLength)
        val suffix = originalName.substring(originalName.length - affixLength, originalName.length)

        val length = originalName.length - 2 * affixLength
        val newColumnName = "$prefix$length$suffix"

        // If there's still a collision after this, just give up.
        // We could try to be more clever, but this is already a pretty rare case.
        if (newColumnName in existingNames) {
            throw IllegalArgumentException(
                "Cannot solve column name collision: $originalName. We recommend removing this column to continue syncing."
            )
        }

        return newColumnName
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
