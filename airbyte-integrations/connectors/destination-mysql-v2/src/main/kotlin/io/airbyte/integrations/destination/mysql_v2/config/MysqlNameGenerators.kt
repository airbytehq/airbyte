/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.config

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.Transformations.Companion.toAlphanumericAndUnderscore
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.mysql_v2.spec.MysqlConfiguration
import jakarta.inject.Singleton

/**
 * Generates final table names for MySQL.
 * Uses the configured database as the default namespace if stream doesn't specify one.
 */
@Singleton
class MysqlFinalTableNameGenerator(private val config: MysqlConfiguration) :
    FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName {
        return TableName(
            namespace = (streamDescriptor.namespace ?: config.database).toMysqlCompatibleName(),
            name = streamDescriptor.name.toMysqlCompatibleName(),
        )
    }
}

/**
 * Generates column names for MySQL.
 * Preserves case but converts special characters to underscores.
 */
@Singleton
class MysqlColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            column.toMysqlCompatibleName(),
            column.toMysqlCompatibleName(),
        )
    }
}

/**
 * Transforms a string to be compatible with MySQL table and column names.
 *
 * MySQL identifier rules:
 * - Can contain letters, digits, underscores, and dollar signs
 * - Can start with any of these characters (including digits)
 * - Maximum length is 64 characters
 * - Case sensitivity depends on filesystem (case-insensitive on Windows/macOS, sensitive on Linux)
 *
 * For portability, we:
 * - Replace special characters with underscores
 * - Preserve case (but be aware of platform differences)
 * - Truncate to 64 characters if needed
 *
 * @return The transformed string suitable for MySQL identifiers.
 */
fun String.toMysqlCompatibleName(): String {
    // Handle empty strings
    if (isEmpty()) {
        throw ConfigErrorException("Empty string is invalid identifier")
    }

    // Replace any character that is not a letter, digit, underscore, or dollar sign
    var transformed = toAlphanumericAndUnderscore(this)

    // MySQL allows identifiers starting with digits, but we'll be consistent
    // with ClickHouse and prepend underscore for safety
    if (transformed.isNotEmpty() && transformed[0].isDigit()) {
        transformed = "_$transformed"
    }

    // Handle empty results
    if (transformed.isEmpty()) {
        throw ConfigErrorException("Identifier transformation resulted in empty string")
    }

    // MySQL identifier max length is 64 characters
    if (transformed.length > 64) {
        transformed = transformed.substring(0, 64)
    }

    return transformed
}
