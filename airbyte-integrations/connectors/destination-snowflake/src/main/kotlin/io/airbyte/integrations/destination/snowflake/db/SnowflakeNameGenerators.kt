/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.db

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.QUOTE
import jakarta.inject.Singleton

// @Deprecated("Use SnowflakeTableSchemaMapper instead")
// @Singleton
// class SnowflakeFinalTableNameGenerator(private val config: SnowflakeConfiguration) :
//     FinalTableNameGenerator {
//     override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName {
//         val namespace = streamDescriptor.namespace ?: config.schema
//         return if (!config.legacyRawTablesOnly) {
//             TableName(
//                 namespace = namespace.toSnowflakeCompatibleName(),
//                 name = streamDescriptor.name.toSnowflakeCompatibleName(),
//             )
//         } else {
//             TableName(
//                 namespace = config.internalTableSchema,
//                 name =
//                     TypingDedupingUtil.concatenateRawTableName(
//                         namespace = escapeJsonIdentifier(namespace),
//                         name = escapeJsonIdentifier(streamDescriptor.name),
//                     ),
//             )
//         }
//     }
// }

@Singleton
class SnowflakeColumnNameGenerator(private val config: SnowflakeConfiguration) {
    data class ColumnName(val name: String, val displayName: String)

    fun getColumnName(column: String): ColumnName {
        return if (!config.legacyRawTablesOnly) {
            ColumnName(
                column.toSnowflakeCompatibleName(),
                column.toSnowflakeCompatibleName(),
            )
        } else {
            ColumnName(
                column,
                column,
            )
        }
    }
}

/**
 * Escapes double-quotes in a JSON identifier by doubling them. This shit is legacy -- I don't know
 * why this would be necessary but no harm in keeping it so I am keeping it.
 *
 * @return The escaped identifier.
 */
fun escapeJsonIdentifier(identifier: String): String {
    // Note that we don't need to escape backslashes here!
    // The only special character in an identifier is the double-quote, which needs to be
    // doubled.
    return identifier.replace(QUOTE, "$QUOTE$QUOTE")
}

/**
 * Transforms a string to be compatible with Snowflake table and column names.
 *
 * @return The transformed string suitable for Snowflake identifiers.
 */
fun String.toSnowflakeCompatibleName(): String {
    var identifier = this

    // Handle empty strings
    if (identifier.isEmpty()) {
        throw ConfigErrorException("Empty string is invalid identifier")
    }

    // Snowflake scripting language does something weird when the `${` bigram shows up in the
    // script so replace these with something else.
    // For completeness, if we trigger this, also replace closing curly braces with underscores.
    if (identifier.contains("\${")) {
        identifier = identifier.replace("$", "_").replace("{", "_").replace("}", "_")
    }

    // Escape double quotes
    identifier = escapeJsonIdentifier(identifier)

    return identifier.uppercase()
}
