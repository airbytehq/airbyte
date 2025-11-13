/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.table.ColumnNameGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

@Singleton
class ColumnNameResolver(
    private val finalTableColumnNameGenerator: ColumnNameGenerator,
) {
    /**
     * Creates column name mapping with handling for potential collisions using incremental
     * numbering, with advanced resolution for truncation cases.
     */
    fun createColumnNameMapping(
        namespace: String?,
        name: String,
        schema: AirbyteType,
    ): Map<String, String> {
        val processedColumnNames = mutableSetOf<ColumnNameGenerator.ColumnName>()
        val columnMappings = mutableMapOf<String, String>()

        schema.asColumns().forEach { (columnName, _) ->
            val processedColumnName = finalTableColumnNameGenerator.getColumnName(columnName)

            // Get a unique column name by adding incremental numbers if necessary
            val finalColumnName =
                resolveColumnNameCollision(
                    namespace,
                    name,
                    processedColumnName,
                    existingNames = processedColumnNames,
                    originalColumnName = columnName,
                    finalTableColumnNameGenerator,
                )

            processedColumnNames.add(finalColumnName)
            columnMappings[columnName] = finalColumnName.displayName
        }

        return columnMappings
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
        namespace: String?,
        streamName: String,
        processedName: ColumnNameGenerator.ColumnName,
        existingNames: Set<ColumnNameGenerator.ColumnName>,
        originalColumnName: String,
        finalTableColumnNameGenerator: ColumnNameGenerator,
    ): ColumnNameGenerator.ColumnName {
        // If processed name is unique, use it
        if (!existingNames.hasConflict(processedName)) {
            return processedName
        }

        log.info {
            "Detected column name collision for ${namespace ?: ""}.${streamName}.$originalColumnName"
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
                "Cannot solve column name collision: $originalName. We recommend removing this column to continue syncing.",
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
                "Cannot solve column name collision: $originalName. We recommend removing this column to continue syncing.",
            )
        }

        return newColumnName
    }

    /**
     * Extension function to check for conflicts in column names. We only care about the canonical
     * name, not the display name.
     */
    private fun Collection<ColumnNameGenerator.ColumnName>.hasConflict(
        candidate: ColumnNameGenerator.ColumnName
    ) = this.any { it.canonicalName == candidate.canonicalName }
}
