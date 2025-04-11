/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import com.google.cloud.bigquery.BigQuery
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.bigquery.BigQueryUtils
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

class BigqueryStreamLoader(
    override val stream: DestinationStream,
    private val bigquery: BigQuery,
    private val config: BigqueryConfiguration,
) : StreamLoader {
    override suspend fun start() {
        super.start()
        logger.info { "Creating dataset if needed: ${config.rawTableDataset}" }
        BigQueryUtils.getOrCreateDataset(
            bigquery,
            config.rawTableDataset,
            config.datasetLocation.region
        )
        // TODO also need to create final table dataset
        logger.info {
            "Creating table if needed: ${TempUtils.rawTableId(config, stream.descriptor)}"
        }
        BigQueryUtils.createPartitionedTableIfNotExists(
            bigquery,
            TempUtils.rawTableId(config, stream.descriptor),
            BigQueryRecordFormatter.SCHEMA_V2,
        )
    }
}
