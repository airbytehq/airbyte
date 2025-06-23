/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.config

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.Transformations.Companion.toAlphanumericAndUnderscore
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import jakarta.inject.Singleton
import java.util.Locale
import java.util.UUID

@Singleton
class ClickhouseFinalTableNameGenerator(private val config: ClickhouseConfiguration) :
    FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor) =
        TableName(
            namespace = (streamDescriptor.namespace ?: config.resolvedDatabase).toClickHouseCompatibleName(),
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
 * ClickHouse identifiers:
 * - Must start with a letter or underscore.
 * - Can contain letters, numbers, and underscores.
 * - Are case-sensitive (this function converts to lowercase for consistency).
 *
 * @return The transformed string suitable for ClickHouse identifiers.
 */
fun String.toClickHouseCompatibleName(): String {
    // 2. Replace any character that is not a lowercase letter (a-z),
    //    a digit (0-9), or an underscore (_) with a single underscore.
    var transformed = toAlphanumericAndUnderscore(this)


    // 4. Ensure the identifier does not start with a digit.
    //    If it starts with a digit, prepend an underscore.
    if (transformed.isNotEmpty() && transformed[0].isDigit()) {
        transformed = "_$transformed"
    }

    // 6. If, after all transformations, the string becomes empty (e.g., from an input like "!!!"),
    //    return a default, valid identifier.
    if (transformed.isEmpty()) {
        return "default_name_${UUID.randomUUID()}" // A fallback name if the input results in an empty string
    }

    return transformed
}
