/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.config

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.Transformations.Companion.toAlphanumericAndUnderscore
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.mysql.spec.MySQLConfiguration
import jakarta.inject.Singleton
import java.util.Locale
import java.util.UUID

@Singleton
class MySQLFinalTableNameGenerator(private val config: MySQLConfiguration) :
    FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor) =
        TableName(
            namespace =
                (streamDescriptor.namespace ?: config.database)
                    .toMySQLCompatibleName(),
            name = streamDescriptor.name.toMySQLCompatibleName(),
        )
}

@Singleton
class MySQLColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            column.toMySQLCompatibleName(),
            column.lowercase(Locale.getDefault()).toMySQLCompatibleName(),
        )
    }
}

/**
 * Transforms a string to be compatible with MySQL table and column names.
 * MySQL identifier limits:
 * - Maximum 64 characters
 * - Can contain letters, digits (0-9), underscores
 * - Should not start with a digit
 *
 * @return The transformed string suitable for MySQL identifiers.
 */
fun String.toMySQLCompatibleName(): String {
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

    // 4. Truncate to MySQL's 64-character limit
    if (transformed.length > 64) {
        transformed = transformed.substring(0, 64)
    }

    return transformed
}
