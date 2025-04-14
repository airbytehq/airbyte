/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.TableId
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.legacy_typing_deduping.TypingDedupingFinalTableOperations
import io.airbyte.cdk.load.orchestration.legacy_typing_deduping.TypingDedupingWriter
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class BigqueryWriterFactory(
    private val catalog: DestinationCatalog,
    private val bigquery: BigQuery,
    private val config: BigqueryConfiguration,
    private val sqlGenerator: BigQuerySqlGenerator,
    private val destinationHandler: BigQueryDestinationHandler,
) {
    @Singleton
    fun make() =
        TypingDedupingWriter(
            catalog,
            BigqueryInitialStateGatherer(),
            BigqueryRawTableOperations(),
            TypingDedupingFinalTableOperations(sqlGenerator, destinationHandler),
        )
}

// TODO delete this - this is definitely duplicated code, and also is definitely wrong
//   e.g. we need to handle special chars in stream name/namespace (c.f.
//   bigquerysqlgenerator.buildStreamId)
//   and that logic needs to be in BigqueryWriter.setup, to handle collisions
//   (probably actually a toolkit)
object TempUtils {
    fun rawTableId(
        config: BigqueryConfiguration,
        streamDescriptor: DestinationStream.Descriptor,
    ) =
        TableId.of(
            config.rawTableDataset,
            StreamId.concatenateRawTableName(
                streamDescriptor.namespace ?: config.datasetId,
                streamDescriptor.name
            )
        )
}
