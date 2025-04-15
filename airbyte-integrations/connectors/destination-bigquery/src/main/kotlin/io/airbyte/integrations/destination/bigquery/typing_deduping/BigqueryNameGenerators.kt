/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.TableName
import io.airbyte.cdk.load.orchestration.TableNameGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator.Companion.nameTransformer
import java.util.Locale

class BigqueryRawTableNameGenerator(
    private val defaultNamespace: String,
    private val rawNamespace: String,
) : TableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName {
        return TableName(
            nameTransformer.getNamespace(rawNamespace),
            nameTransformer.convertStreamName(
                StreamId.concatenateRawTableName(
                    streamDescriptor.namespace ?: defaultNamespace,
                    streamDescriptor.name
                )
            ),
        )
    }
}

class BigqueryFinalTableNameGenerator(private val defaultNamespace: String) : TableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor) =
        TableName(
            nameTransformer.getNamespace(streamDescriptor.namespace ?: defaultNamespace),
            nameTransformer.convertStreamName(streamDescriptor.name),
        )
}

class BigqueryColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            nameTransformer.getIdentifier(column),
            // Bigquery columns are case-insensitive, so do all our validation on the
            // lowercased name
            nameTransformer.getIdentifier(column.lowercase(Locale.getDefault())),
        )
    }
}
