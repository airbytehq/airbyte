/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping

import com.google.cloud.bigquery.TableId
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.RawTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TypingDedupingUtil
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import java.util.Locale
import javax.inject.Singleton
import org.apache.commons.codec.digest.DigestUtils

private val nameTransformer = BigQuerySQLNameTransformer()

/**
 * BigQuery limits column names to 300 characters. See
 * https://cloud.google.com/bigquery/docs/schemas#column_names.
 */
const val BIGQUERY_MAX_COLUMN_NAME_LENGTH = 300

private const val COLUMN_NAME_HASH_LENGTH = 8

@Singleton
class BigqueryRawTableNameGenerator(val config: BigqueryConfiguration) : RawTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor) =
        TableName(
            nameTransformer.getNamespace(config.internalTableDataset),
            nameTransformer.convertStreamName(
                TypingDedupingUtil.concatenateRawTableName(
                    streamDescriptor.namespace ?: config.datasetId,
                    streamDescriptor.name,
                )
            ),
        )
}

@Singleton
class BigqueryFinalTableNameGenerator(val config: BigqueryConfiguration) : FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor) =
        TableName(
            nameTransformer.getNamespace(streamDescriptor.namespace ?: config.datasetId),
            nameTransformer.convertStreamName(streamDescriptor.name),
        )
}

@Singleton
class BigqueryColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            nameTransformer.convertStreamName(column).truncateToBigqueryColumnNameLength(),
            // Bigquery columns are case-insensitive, so do all our validation on the
            // lowercased name
            nameTransformer
                .convertStreamName(column.lowercase(Locale.getDefault()))
                .truncateToBigqueryColumnNameLength(),
        )
    }
}

/**
 * BigQuery rejects column names longer than [BIGQUERY_MAX_COLUMN_NAME_LENGTH] characters. Truncate
 * over-length names to a prefix plus a short deterministic hash of the full name, so that two
 * distinct over-length names sharing a prefix don't collide. Names within the limit are returned
 * unchanged, so already-synced columns keep their existing names.
 */
private fun String.truncateToBigqueryColumnNameLength(): String {
    if (length <= BIGQUERY_MAX_COLUMN_NAME_LENGTH) {
        return this
    }
    val hash = DigestUtils.sha1Hex(this).take(COLUMN_NAME_HASH_LENGTH)
    val prefixLength = BIGQUERY_MAX_COLUMN_NAME_LENGTH - hash.length - 1
    return "${substring(0, prefixLength)}_$hash"
}

fun TableName.toTableId(): TableId = TableId.of(this.namespace, this.name)
