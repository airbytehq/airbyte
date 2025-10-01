/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.db

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingUtil
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import jakarta.inject.Singleton
import java.util.UUID

@Singleton
class SnowflakeFinalTableNameGenerator(private val config: SnowflakeConfiguration) :
    FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor) =
        TableName(
            namespace =
                (config.internalTableSchema ?: (streamDescriptor.namespace ?: config.schema))
                    .toSnowflakeCompatibleName(),
            name =
                if (config.internalTableSchema.isNullOrBlank()) {
                    streamDescriptor.name.toSnowflakeCompatibleName()
                } else {
                    TypingDedupingUtil.concatenateRawTableName(
                            streamDescriptor.namespace ?: config.schema,
                            streamDescriptor.name.toSnowflakeCompatibleName()
                        )
                },
        )
}

@Singleton
class SnowflakeColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            column.toSnowflakeCompatibleName().uppercase(),
            column.toSnowflakeCompatibleName().uppercase(),
        )
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
    return identifier.replace("\"", "\"\"")
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
        return "DEFAULT_NAME_${UUID.randomUUID()}".replace("-", "_")
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
