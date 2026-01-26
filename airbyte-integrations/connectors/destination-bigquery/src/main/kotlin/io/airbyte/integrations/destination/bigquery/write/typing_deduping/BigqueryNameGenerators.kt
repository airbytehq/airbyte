package io.airbyte.integrations.destination.bigquery.write.typing_deduping

import com.google.cloud.bigquery.TableId
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.RawTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingUtil
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.stream.StreamConfigProvider
import java.util.Locale
import javax.inject.Singleton

private val nameTransformer = BigQuerySQLNameTransformer()

class BigqueryRawTableNameGenerator(
    val config: BigqueryConfiguration,
    val streamConfigProvider: StreamConfigProvider
) : RawTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName {
        val suffix = streamConfigProvider.getTableSuffix(streamDescriptor)
        return TableName(
            nameTransformer.getNamespace(config.internalTableDataset),
            nameTransformer.convertStreamName(
                TypingDedupingUtil.concatenateRawTableName(
                    streamDescriptor.namespace ?: config.datasetId,
                    streamDescriptor.name,
                ) + suffix
            ),
        )
    }
}

class BigqueryFinalTableNameGenerator(
    val config: BigqueryConfiguration,
    val streamConfigProvider: StreamConfigProvider
) : FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName {
        val suffix = streamConfigProvider.getTableSuffix(streamDescriptor)
        return TableName(
            nameTransformer.getNamespace(streamConfigProvider.getDataset(streamDescriptor)),
            nameTransformer.convertStreamName(streamDescriptor.name + suffix),
        )
    }
}

@Singleton
class BigqueryColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            nameTransformer.convertStreamName(column),
            // Bigquery columns are case-insensitive, so do all our validation on the
            // lowercased name
            nameTransformer.convertStreamName(column.lowercase(Locale.getDefault())),
        )
    }
}

fun TableName.toTableId(): TableId = TableId.of(this.namespace, this.name)
