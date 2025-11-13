/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.config

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.mongodb_v2.spec.MongodbConfiguration
import jakarta.inject.Singleton
import java.util.Locale

@Singleton
class MongodbFinalTableNameGenerator(private val config: MongodbConfiguration) :
    FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor) =
        TableName(
            namespace = (streamDescriptor.namespace ?: config.database).toMongodbCompatibleName(),
            name = streamDescriptor.name.toMongodbCompatibleName(),
        )
}

@Singleton
class MongodbColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            column.toMongodbCompatibleName(),
            column.lowercase(Locale.getDefault()).toMongodbCompatibleName(),
        )
    }
}

/**
 * MongoDB collection naming rules:
 * - Cannot contain null character
 * - Cannot start with "system."
 * - Max length: 120 characters (conservative limit)
 */
fun String.toMongodbCompatibleName(): String {
    var result = this.replace("\u0000", "") // Remove null characters

    // Check for system prefix BEFORE replacing dots
    val hasSystemPrefix = result.startsWith("system.")

    // Now do replacements
    result = result
        .replace("$", "_") // Replace $ with underscore (reserved for operators)
        .replace(".", "_") // Replace dots with underscore (used for nested access)

    // Add prefix if it was a system collection
    if (hasSystemPrefix) {
        result = "_$result"
    }

    return result.take(120) // Limit length
}
