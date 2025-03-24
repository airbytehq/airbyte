/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.avro

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

/**
 * @deprecated This class is deprecated and will be removed in a future release. We are
 * transitioning to a new mapping pattern using EnrichedDestinationRecordAirbyteValue and
 * EnrichedAirbyteValue for improved type safety and consistency.
 *
 * For examples on implementing the new pattern, please refer to:
 * - DestinationRecordRaw.asEnrichedDestinationRecordAirbyteValue()
 * - toRecord() method in the s3-data-lake destination
 */
@Suppress("DEPRECATION")
@Deprecated("Use DestinationRecordRaw.asEnrichedDestinationRecordAirbyteValue() logic instead")
class AvroMapperPipelineFactory : MapperPipelineFactory {
    @Suppress("DEPRECATION")
    override fun create(stream: DestinationStream): MapperPipeline =
        MapperPipeline(
            stream.schema,
            listOf(
                FailOnAllUnknownTypesExceptNull() to AirbyteValueNoopMapper(),
                MergeUnions() to AirbyteValueNoopMapper(),
                /**
                 * This recursive behavior is pretty sad and should not be replicated in the future.
                 * We currently support this to meet legacy requirements for S3 and should be
                 * avoided at all costs
                 */
                AirbyteSchemaNoopMapper() to
                    AirbyteValueDeepCoercingMapper(
                        recurseIntoObjects = true,
                        recurseIntoArrays = true,
                        recurseIntoUnions = true,
                    ),
                // We need to maintain the original ObjectWithNoProperties/etc type.
                // For example, if a stream declares no columns, we will (correctly) recognize
                // the root schema as ObjectTypeWithEmptySchema.
                // If we then map that root schema to StringType, then
                // AirbyteTypeToAirbyteTypeWithMeta will crash on it.
                AirbyteSchemaNoopMapper() to SchemalessValuesToJsonString(),
                AirbyteSchemaNoopMapper() to NullOutOfRangeIntegers(),
                AirbyteSchemaNoopMapper() to TimeStringToInteger(),
            ),
        )
}
