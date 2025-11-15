/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.config

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.RawTableNameGenerator
import io.airbyte.cdk.load.table.TableName
import jakarta.inject.Singleton

@Singleton
class MongodbRawTableNameGenerator(
    private val config: MongodbConfiguration,
) : RawTableNameGenerator {
    override fun getTableName(descriptor: DestinationStream.Descriptor): TableName {
        // Raw tables go to the same database
        val namespace = config.resolvedDatabase
        val name = "_airbyte_raw_${descriptor.namespace}_${descriptor.name}".toMongodbCompatible()
        return TableName(namespace, name)
    }
}

@Singleton
class MongodbFinalTableNameGenerator(
    private val config: MongodbConfiguration,
) : FinalTableNameGenerator {
    override fun getTableName(descriptor: DestinationStream.Descriptor): TableName {
        // Map namespace to database, name to collection
        val namespace = descriptor.namespace?.toMongodbCompatible()
            ?: config.resolvedDatabase
        val originalName = descriptor.name
        val name = originalName.toMongodbCompatible()

        if (originalName != name) {
            println("DEBUG FinalTableNameGenerator: '$originalName' -> '$name'")
        }

        return TableName(namespace, name)
    }
}

@Singleton
class MongodbColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        // MongoDB field names are more permissive than collection names
        // Only sanitize if starting with $ (reserved) or contains null character
        val mongoName = column
            .replace("\u0000", "")  // Remove null characters
            .let { if (it.startsWith("$")) "_$it" else it }  // Prefix $ with underscore

        return ColumnNameGenerator.ColumnName(
            canonicalName = mongoName,
            displayName = mongoName,
        )
    }
}

// Helper: MongoDB collection/field names
// - Allow letters, numbers, underscores
// - Cannot start with system. (reserved prefix)
// - Replace invalid chars with underscore
// - MongoDB restricts: $, null, empty, system. prefix
// - Also avoid: . (namespace separator), special chars
fun String.toMongodbCompatible(): String {
    return this
        .replace(Regex("[^a-zA-Z0-9_]"), "_")  // Replace all special chars with underscore
        .replace(Regex("_+"), "_")  // Collapse multiple underscores
        .let { if (it.startsWith("system_")) "_$it" else it }  // Avoid system prefix
        .let { if (it.isEmpty()) "default_name" else it }  // Handle empty after sanitization
        .take(120) // MongoDB collection names max 120 bytes (UTF-8)
}
