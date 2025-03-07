/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.iceberg.parquet

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteSchemaNoopMapper
import io.airbyte.cdk.load.data.AirbyteValueDeepCoercingMapper
import io.airbyte.cdk.load.data.AirbyteValueNoopMapper
import io.airbyte.cdk.load.data.MapperPipeline
import io.airbyte.cdk.load.data.MapperPipelineFactory
import io.airbyte.cdk.load.data.MergeUnions

class IcebergParquetPipelineFactory : MapperPipelineFactory {
    override fun create(stream: DestinationStream): MapperPipeline =
        MapperPipeline(
            stream.schema,
            listOf(
                MergeUnions() to AirbyteValueNoopMapper(),
                AirbyteSchemaNoopMapper() to
                    AirbyteValueDeepCoercingMapper(
                        // See IcebergNullOutOfRangeIntegers for explanation.
                        recurseIntoObjects = false,
                        recurseIntoArrays = true,
                        recurseIntoUnions = false,
                    ),
                AirbyteSchemaNoopMapper() to IcebergStringifyComplexTypes(),
                AirbyteSchemaNoopMapper() to IcebergNullOutOfRangeIntegers(),
            ),
        )
}
