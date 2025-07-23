/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.skeleton_directload.SkeletonDirectLoadSQLNameTransformer
import io.airbyte.integrations.destination.skeleton_directload.spec.SkeletonDirectLoadConfiguration
import java.util.Locale
import javax.inject.Singleton

private val nameTransformer = SkeletonDirectLoadSQLNameTransformer()

@Singleton
class SkeletonDirectLoadFinalTableNameGenerator(val config: SkeletonDirectLoadConfiguration) :
    FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor) =
        TableName(
            nameTransformer.getNamespace(streamDescriptor.namespace ?: config.namespace),
            nameTransformer.convertStreamName(streamDescriptor.name),
        )
}

@Singleton
class SkeletonDirectLoadColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            nameTransformer.convertStreamName(column),
            // Bigquery columns are case-insensitive, so do all our validation on the
            // lowercased name
            nameTransformer.convertStreamName(column.lowercase(Locale.getDefault())),
        )
    }
}
