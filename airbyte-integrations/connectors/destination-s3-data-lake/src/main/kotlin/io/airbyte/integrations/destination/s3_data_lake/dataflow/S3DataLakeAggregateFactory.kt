/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.dataflow

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableWriterFactory
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.s3_data_lake.spec.DEFAULT_STAGING_BRANCH
import io.airbyte.integrations.destination.s3_data_lake.write.S3DataLakeStreamState
import jakarta.inject.Singleton

@Singleton
class S3DataLakeAggregateFactory(
    private val catalog: DestinationCatalog,
    private val streamStateStore: StreamStateStore<S3DataLakeStreamState>,
    private val icebergTableWriterFactory: IcebergTableWriterFactory,
    private val icebergUtil: IcebergUtil,
) : AggregateFactory {

    override fun create(key: StoreKey): Aggregate {
        val state = streamStateStore.get(key)!!
        val stream = catalog.getStream(key)

        val writer =
            icebergTableWriterFactory.create(
                table = state.table,
                generationId = icebergUtil.constructGenerationIdSuffix(stream),
                importType = stream.importType,
                schema = state.schema
            )

        return S3DataLakeAggregate(
            stream = stream,
            table = state.table,
            schema = state.schema,
            stagingBranchName = DEFAULT_STAGING_BRANCH,
            writer = writer,
            icebergUtil = icebergUtil,
        )
    }
}
