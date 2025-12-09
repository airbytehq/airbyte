/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.config

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.Transformations.Companion.toAlphanumericAndUnderscore
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameGenerator
import io.airbyte.cdk.load.table.FinalTableNameGenerator
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import jakarta.inject.Singleton
import java.util.Locale
import java.util.UUID

@Singleton
class ClickhouseFinalTableNameGenerator(private val config: ClickhouseConfiguration) :
    FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor) =
        TableName(
            namespace =
                (streamDescriptor.namespace ?: config.resolvedDatabase)
                    .toClickHouseCompatibleName(),
            name = streamDescriptor.name.toClickHouseCompatibleName(),
        )
}

@Singleton
class ClickhouseColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            column.toClickHouseCompatibleName(),
            column.lowercase(Locale.getDefault()).toClickHouseCompatibleName(),
        )
    }
}

/**
 * Transforms a string to be compatible with ClickHouse table and column names.
 *
 * @return The transformed string suitable for ClickHouse identifiers.
 */
fun String.toClickHouseCompatibleName(): String {
    // 1. Replace any character that is not a letter,
    //    a digit (0-9), or an underscore (_) with a single underscore.
    var transformed = toAlphanumericAndUnderscore(this)

    // 2. Ensure the identifier does not start with a digit.
    //    If it starts with a digit, prepend an underscore.
    if (transformed.isNotEmpty() && transformed[0].isDigit()) {
        transformed = "_$transformed"
    }

    // 3.Do not allow empty strings.
    if (transformed.isEmpty()) {
        return "default_name_${UUID.randomUUID()}" // A fallback name if the input results in an
        // empty string
    }

    return transformed
}
