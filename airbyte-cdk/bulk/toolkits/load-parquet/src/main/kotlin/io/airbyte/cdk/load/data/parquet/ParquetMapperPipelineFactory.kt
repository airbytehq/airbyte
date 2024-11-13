/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.parquet

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteSchemaNoopMapper
import io.airbyte.cdk.load.data.AirbyteValueNoopMapper
import io.airbyte.cdk.load.data.MapperPipeline
import io.airbyte.cdk.load.data.MapperPipelineFactory
import io.airbyte.cdk.load.data.MergeUnions
import io.airbyte.cdk.load.data.SchemalessTypesToJsonString
import io.airbyte.cdk.load.data.SchemalessValuesToJsonString
import io.airbyte.cdk.load.data.TimeStringToInteger
import io.airbyte.cdk.load.data.UnionTypeToDisjointRecord
import io.airbyte.cdk.load.data.UnionValueToDisjointRecord

class ParquetMapperPipelineFactory : MapperPipelineFactory {
    override fun create(stream: DestinationStream): MapperPipeline =
        MapperPipeline(
            stream.schema,
            listOf(
                SchemalessTypesToJsonString() to SchemalessValuesToJsonString(),
                AirbyteSchemaNoopMapper() to TimeStringToInteger(),
                MergeUnions() to AirbyteValueNoopMapper(),
                UnionTypeToDisjointRecord() to UnionValueToDisjointRecord(),
            ),
        )
}
