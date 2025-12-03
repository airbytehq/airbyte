/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.schema

import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

/** Applies destination-specific column name munging logic and handles any naming collisions. */
@Singleton
class ColumnNameResolver(
    private val mapper: TableSchemaMapper,
) {
    private val log = KotlinLogging.logger {}
    /**
     * Creates column name mapping with handling for potential collisions using incremental
     * numbering, with advanced resolution for truncation cases.
     */
    fun getColumnNameMapping(inputColumNames: Set<String>): Map<String, String> {
        val processedColumnNames = mutableSetOf<String>()
        val columnMappings = mutableMapOf<String, String>()

        inputColumNames.forEach { columnName ->
            val processedColumnName = mapper.toColumnName(columnName)

            // Get a unique column name by adding incremental numbers if necessary
            val finalColumnName =
                resolveColumnNameCollision(
                    processedColumnName,
                    existingNames = processedColumnNames,
                    originalColumnName = columnName,
                )

            processedColumnNames.add(finalColumnName)
            columnMappings[columnName] = finalColumnName
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
        processedName: String,
        existingNames: Set<String>,
        originalColumnName: String,
    ): String {
        // If processed name is unique, use it
        if (!hasConflict(existingNames, processedName)) {
            return processedName
        }

        log.info { "Detected column name collision for $originalColumnName" }

        // Try adding incremental suffixes until we find a non-colliding name
        var counter = 1
        var candidateName: String
        var previousCandidate = processedName

        do {
            // Generate candidate name by adding numeric suffix
            candidateName = mapper.toColumnName("${originalColumnName}_$counter")

            // Check if we're making progress (detecting potential truncation)
            if (colsConflict(candidateName, previousCandidate)) {
                // We're not making progress, likely due to name truncation
                // Use the more powerful resolution method with the ORIGINAL column name
                return superResolveColumnCollisions(
                    originalColumnName,
                    existingNames,
                    processedName.length,
                )
            }

            previousCandidate = candidateName
            counter++
        } while (existingNames.any { colsConflict(it, candidateName) })

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
        maximumColumnNameLength: Int,
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
                "Cannot solve column name collision: $originalName. We recommend removing this column to continue syncing.",
            )
        }

        val prefix = originalName.take(affixLength)
        val suffix = originalName.substring(originalName.length - affixLength, originalName.length)

        val length = originalName.length - 2 * affixLength
        val newColumnName = mapper.toColumnName("$prefix$length$suffix")

        // If there's still a collision after this, just give up.
        // We could try to be more clever, but this is already a pretty rare case.
        if (hasConflict(existingNames, newColumnName)) {
            throw IllegalArgumentException(
                "Cannot solve column name collision: $originalName. We recommend removing this column to continue syncing.",
            )
        }

        return newColumnName
    }

    fun colsConflict(a: String, b: String): Boolean = mapper.colsConflict(a, b)

    fun hasConflict(existingNames: Set<String>, candidate: String) =
        existingNames.any { colsConflict(it, candidate) }
}
