/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.motherduck.db

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.Transformations.Companion.toAlphanumericAndUnderscore
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingUtil
import io.airbyte.integrations.destination.motherduck.spec.MotherDuckConfiguration
import jakarta.inject.Singleton
import java.util.Locale
import java.util.UUID

@Singleton
class MotherDuckFinalTableNameGenerator(private val config: MotherDuckConfiguration) :
    FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor) =
        TableName(
            namespace =
                (config.internalTableSchema ?: (streamDescriptor.namespace ?: config.schema))
                    .toDuckDBCompatibleName(),
            name =
                if (config.internalTableSchema.isNullOrBlank()) {
                    streamDescriptor.name.toDuckDBCompatibleName()
                } else {
                    TypingDedupingUtil.concatenateRawTableName(
                            streamDescriptor.namespace ?: config.schema,
                            streamDescriptor.name
                        )
                        .toDuckDBCompatibleName()
                },
        )
}

@Singleton
class MotherDuckColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            column.toDuckDBCompatibleName(),
            column.lowercase(Locale.getDefault()).toDuckDBCompatibleName(),
        )
    }
}

fun String.toDuckDBCompatibleName(): String {
    var transformed = toAlphanumericAndUnderscore(this)

    if (transformed.isNotEmpty() && transformed[0].isDigit()) {
        transformed = "_$transformed"
    }

    if (transformed.isEmpty()) {
        return "default_name_${UUID.randomUUID()}"
    }

    return transformed
}
