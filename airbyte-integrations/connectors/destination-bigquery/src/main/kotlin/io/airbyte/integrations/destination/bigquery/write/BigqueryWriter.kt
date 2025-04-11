/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.TableId
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import jakarta.inject.Singleton

@Singleton
class BigqueryWriter(
    private val bigquery: BigQuery,
    private val config: BigqueryConfiguration,
) : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return BigqueryStreamLoader(stream, bigquery, config)
    }
}

// TODO delete this - this is definitely duplicated code, and also is definitely wrong
//   e.g. we need to handle special chars in stream name/namespace (c.f.
// bigquerysqlgenerator.buildStreamId)
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
