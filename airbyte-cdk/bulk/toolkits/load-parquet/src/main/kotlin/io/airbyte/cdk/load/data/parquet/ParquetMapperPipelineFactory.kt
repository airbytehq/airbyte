/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.parquet

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValueNoopMapper
import io.airbyte.cdk.load.data.MapperPipeline
import io.airbyte.cdk.load.data.MapperPipelineFactory
import io.airbyte.cdk.load.data.MergeUnions
import io.airbyte.cdk.load.data.SchemalessTypesToJson
import io.airbyte.cdk.load.data.SchemalessValuesToJson
import io.airbyte.cdk.load.data.UnionTypeToDisjointRecord
import io.airbyte.cdk.load.data.UnionValueToDisjointRecord
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

@Singleton
@Secondary
class ParquetMapperPipelineFactory : MapperPipelineFactory {
    override fun create(stream: DestinationStream): MapperPipeline =
        MapperPipeline(
            stream.schema,
            listOf(
                SchemalessTypesToJson::class to SchemalessValuesToJson::class,
                MergeUnions::class to AirbyteValueNoopMapper::class,
                UnionTypeToDisjointRecord::class to UnionValueToDisjointRecord::class,
            ),
        )
}
