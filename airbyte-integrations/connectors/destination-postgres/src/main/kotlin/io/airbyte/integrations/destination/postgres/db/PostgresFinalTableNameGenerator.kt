/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.db

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.Transformations.Companion.toAlphanumericAndUnderscore
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingUtil
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import jakarta.inject.Singleton
import java.util.Locale
import java.util.UUID

@Singleton
class PostgresFinalTableNameGenerator(private val config: PostgresConfiguration) :
    FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName {
        val namespace = streamDescriptor.namespace ?: config.schema
        return if (!config.legacyRawTablesOnly) {
            TableName(
                namespace = namespace.toPostgresCompatibleName(),
                name = streamDescriptor.name.toPostgresCompatibleName(),
            )
        } else {
            TableName(
                namespace = config.internalTableSchema!!.lowercase().toPostgresCompatibleName(),
                name =
                    TypingDedupingUtil.concatenateRawTableName(
                            namespace = namespace,
                            name = streamDescriptor.name,
                        )
                        .lowercase()
                        .toPostgresCompatibleName(),
            )
        }
    }
}

@Singleton
class PostgresColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            column.toPostgresCompatibleName(),
            column.lowercase(Locale.getDefault()).toPostgresCompatibleName(),
        )
    }
}

/**
 * Transforms a string to be compatible with PostgreSQL table and column names.
 *
 * PostgreSQL identifier rules:
 * - Maximum length is 63 bytes
 * - Can contain letters, digits, and underscores
 * - Must start with a letter or underscore (not a digit)
 * - Case-insensitive by default (unless quoted)
 *
 * @return The transformed string suitable for PostgreSQL identifiers.
 */
fun String.toPostgresCompatibleName(): String {
    // 1. Replace any character that is not a letter,
    //    a digit (0-9), or an underscore (_) with a single underscore.
    var transformed = toAlphanumericAndUnderscore(this)

    // 2. Ensure the identifier does not start with a digit.
    //    If it starts with a digit, prepend an underscore.
    if (transformed.isNotEmpty() && transformed[0].isDigit()) {
        transformed = "_$transformed"
    }

    // 3. Do not allow empty strings.
    if (transformed.isEmpty()) {
        return "default_name_${UUID.randomUUID()}" // A fallback name if the input results in an
        // empty string
    }

    // 4. Truncate to 63 characters if needed (PostgreSQL identifier limit)
    if (transformed.length > 63) {
        // Keep first part and add hash to avoid collisions
        val hash = transformed.hashCode().toString().takeLast(8)
        transformed = transformed.take(54) + "_" + hash
    }

    return transformed
}
