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
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import javax.inject.Singleton
import org.apache.commons.codec.digest.DigestUtils

private val LOGGER = KotlinLogging.logger {}
const val DEFAULT_AIRBYTE_INTERNAL_NAMESPACE = "airbyte_internal"

data class TableNameInfo(val tableNames: TableNames, val columnNameMapping: ColumnNameMapping)

data class TableCatalog(private val catalog: Map<DestinationStream, TableNameInfo>) :
    Map<DestinationStream, TableNameInfo> by catalog {
    fun getMappedColumnName(stream: DestinationStream, colName: String): String? =
        this[stream]?.columnNameMapping?.get(colName)
}

data class TableCatalogByDescriptor(
    private val catalog: Map<DestinationStream.Descriptor, TableNameInfo>
) : Map<DestinationStream.Descriptor, TableNameInfo> by catalog {
    fun getFinalTableName(desc: DestinationStream.Descriptor): TableName? =
        this[desc]?.tableNames?.finalTableName
}

@Factory
class TableCatalogFactory {
    @Singleton
    fun getTableCatalog(
        catalog: DestinationCatalog,
        // Raw table generator is optional. Direct-load destinations don't need it
        // (unless they were previously T+D destinations, in which case it's still required
        // so that we maintain stable names with the T+D version)
        rawTableNameGenerator: RawTableNameGenerator?,
        finalTableNameGenerator: FinalTableNameGenerator,
        finalTableColumnNameGenerator: ColumnNameGenerator,
    ): TableCatalog {
        val processedRawTableNames =
            if (rawTableNameGenerator != null) {
                mutableSetOf<TableName>()
            } else {
                null
            }
        val processedFinalTableNames = mutableSetOf<TableName>()

        val result = mutableMapOf<DestinationStream, TableNameInfo>()

        catalog.streams.forEach { stream ->
            val originalRawTableName = rawTableNameGenerator?.getTableName(stream.descriptor)
            val originalFinalTableName = finalTableNameGenerator.getTableName(stream.descriptor)
            val currentRawProcessedName: TableName?
            val currentFinalProcessedName: TableName

            val rawTableNameColliding =
                processedRawTableNames?.let { originalRawTableName in it } ?: false
            val finalTableNameColliding = originalFinalTableName in processedFinalTableNames
            if (rawTableNameColliding || finalTableNameColliding) {
                LOGGER.info {
                    "Detected table name collision for ${stream.descriptor.namespace}.${stream.descriptor.name}"
                }
                // Create a hash-suffixed name to avoid collision
                val hash =
                    DigestUtils.sha1Hex(
                            "${originalFinalTableName.namespace}&airbyte&${stream.descriptor.name}"
                        )
                        .substring(0, 3)
                val newName = "${stream.descriptor.name}_$hash"

                currentRawProcessedName =
                    rawTableNameGenerator?.getTableName(stream.descriptor.copy(name = newName))
                processedRawTableNames?.add(currentRawProcessedName!!)
                currentFinalProcessedName =
                    finalTableNameGenerator.getTableName(stream.descriptor.copy(name = newName))
                processedFinalTableNames.add(currentFinalProcessedName)
            } else {
                processedRawTableNames?.add(originalRawTableName!!)
                processedFinalTableNames.add(originalFinalTableName)
                currentRawProcessedName = originalRawTableName
                currentFinalProcessedName = originalFinalTableName
            }

            // Create column name mapping with collision handling
            val columnNameMapping = createColumnNameMapping(stream, finalTableColumnNameGenerator)

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
    private fun createColumnNameMapping(
        stream: DestinationStream,
        finalTableColumnNameGenerator: ColumnNameGenerator,
    ): ColumnNameMapping {
        val processedColumnNames = mutableSetOf<ColumnNameGenerator.ColumnName>()
        val columnMappings = mutableMapOf<String, String>()
        // Map to track original column names by their truncated versions

        stream.schema.asColumns().forEach { (columnName, _) ->
            val processedColumnName = finalTableColumnNameGenerator.getColumnName(columnName)

            // Get a unique column name by adding incremental numbers if necessary
            val finalColumnName =
                resolveColumnNameCollision(
                    stream,
                    processedColumnName,
                    existingNames = processedColumnNames,
                    originalColumnName = columnName,
                    finalTableColumnNameGenerator,
                )

            processedColumnNames.add(finalColumnName)
            columnMappings[columnName] = finalColumnName.displayName
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
        stream: DestinationStream,
        processedName: ColumnNameGenerator.ColumnName,
        existingNames: Set<ColumnNameGenerator.ColumnName>,
        originalColumnName: String,
        finalTableColumnNameGenerator: ColumnNameGenerator,
    ): ColumnNameGenerator.ColumnName {
        // If processed name is unique, use it
        if (!existingNames.hasConflict(processedName)) {
            return processedName
        }

        LOGGER.info {
            "Detected column name collision for ${stream.descriptor.namespace}.${stream.descriptor.name}.$originalColumnName"
        }

        // Try adding incremental suffixes until we find a non-colliding name
        var counter = 1
        var candidateName: ColumnNameGenerator.ColumnName
        var previousCandidate = processedName

        do {
            // Generate candidate name by adding numeric suffix
            candidateName =
                finalTableColumnNameGenerator.getColumnName("${originalColumnName}_$counter")

            // Check if we're making progress (detecting potential truncation)
            if (candidateName.canonicalName == previousCandidate.canonicalName) {
                // We're not making progress, likely due to name truncation
                // Use the more powerful resolution method with the ORIGINAL column name
                return superResolveColumnCollisions(
                    originalColumnName,
                    existingNames,
                    processedName.canonicalName.length,
                    finalTableColumnNameGenerator,
                )
            }

            previousCandidate = candidateName
            counter++
        } while (existingNames.hasConflict(candidateName))

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
        existingNames: Set<ColumnNameGenerator.ColumnName>,
        maximumColumnNameLength: Int,
        finalTableColumnNameGenerator: ColumnNameGenerator,
    ): ColumnNameGenerator.ColumnName {
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
        val newColumnName = finalTableColumnNameGenerator.getColumnName("$prefix$length$suffix")

        // If there's still a collision after this, just give up.
        // We could try to be more clever, but this is already a pretty rare case.
        if (existingNames.hasConflict(newColumnName)) {
            throw IllegalArgumentException(
                "Cannot solve column name collision: $originalName. We recommend removing this column to continue syncing."
            )
        }

        return newColumnName
    }

    @Singleton
    fun getTableCatalogByDescriptor(map: TableCatalog): TableCatalogByDescriptor {
        return TableCatalogByDescriptor(map.mapKeys { (k, _) -> k.descriptor })
    }
}

/**
 * can't just use `.contains()`, because we don't care whether the column names have the same
 * display name. We only care about the canonical name.
 *
 * (arguably we could override equals/hashcode? But that would make writing tests more difficult,
 * because it's not an intuitive behavior)
 */
private fun Collection<ColumnNameGenerator.ColumnName>.hasConflict(
    candidate: ColumnNameGenerator.ColumnName
) = this.any { it.canonicalName == candidate.canonicalName }
