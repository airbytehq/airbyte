/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.parquet

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteSchemaNoopMapper
import io.airbyte.cdk.load.data.AirbyteValueDeepCoercingMapper
import io.airbyte.cdk.load.data.AirbyteValueNoopMapper
import io.airbyte.cdk.load.data.FailOnAllUnknownTypesExceptNull
import io.airbyte.cdk.load.data.MapperPipeline
import io.airbyte.cdk.load.data.MapperPipelineFactory
import io.airbyte.cdk.load.data.MergeUnions
import io.airbyte.cdk.load.data.NullOutOfRangeIntegers
import io.airbyte.cdk.load.data.SchemalessValuesToJsonString
import io.airbyte.cdk.load.data.TimeStringToInteger
import io.airbyte.cdk.load.data.UnionTypeToDisjointRecord
import io.airbyte.cdk.load.data.UnionValueToDisjointRecord

class ParquetMapperPipelineFactory : MapperPipelineFactory {
    override fun create(stream: DestinationStream): MapperPipeline =
        MapperPipeline(
            stream.schema,
            listOf(
                FailOnAllUnknownTypesExceptNull() to AirbyteValueNoopMapper(),
                MergeUnions() to AirbyteValueNoopMapper(),
                AirbyteSchemaNoopMapper() to AirbyteValueDeepCoercingMapper(),
                // We need to maintain the original ObjectWithNoProperties/etc type.
                // For example, if a stream declares no columns, we will (correctly) recognize
                // the root schema as ObjectTypeWithEmptySchema.
                // If we then map that root schema to StringType, then
                // AirbyteTypeToAirbyteTypeWithMeta will crash on it.
                // Furthermore, in UnionTypeToDisjointRecord, this enables us to write thes fields
                // as "object" rather than as "string".
                AirbyteSchemaNoopMapper() to SchemalessValuesToJsonString(),
                AirbyteSchemaNoopMapper() to NullOutOfRangeIntegers(),
                AirbyteSchemaNoopMapper() to TimeStringToInteger(),
                UnionTypeToDisjointRecord() to UnionValueToDisjointRecord(),
            ),
        )
}
