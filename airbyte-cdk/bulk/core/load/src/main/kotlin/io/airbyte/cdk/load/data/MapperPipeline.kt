/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Change

/**
 * @deprecated This class is deprecated and will be removed in a future release. We are
 * transitioning to a new mapping pattern using EnrichedDestinationRecordAirbyteValue and
 * EnrichedAirbyteValue for improved type safety and consistency.
 *
 * For examples on implementing the new pattern, please refer to:
 * - DestinationRecordRaw.asEnrichedDestinationRecordAirbyteValue()
 * - toRecord() method in the s3-data-lake destination
 */
class MapperPipeline(
    inputSchema: AirbyteType,
    schemaValueMapperPairs: List<Pair<AirbyteSchemaMapper, AirbyteValueMapper>>,
) {
    private val schemasWithMappers: List<Pair<AirbyteType, AirbyteValueMapper>>

    val finalSchema: AirbyteType

    init {
        val (schemaMappers, valueMappers) = schemaValueMapperPairs.unzip()
        val schemas =
            schemaMappers.runningFold(inputSchema) { schema, mapper -> mapper.map(schema) }
        schemasWithMappers = schemas.zip(valueMappers)
        finalSchema = schemas.last()
    }

    fun map(data: AirbyteValue, changes: List<Change>? = null): Pair<AirbyteValue, List<Change>> =
        schemasWithMappers.fold(data to (changes ?: emptyList())) {
            (value, changes),
            (schema, mapper) ->
            mapper.map(value, schema, changes)
        }
}

/**
 * @deprecated This class is deprecated and will be removed in a future release. We are
 * transitioning to a new mapping pattern using EnrichedDestinationRecordAirbyteValue and
 * EnrichedAirbyteValue for improved type safety and consistency.
 *
 * For examples on implementing the new pattern, please refer to:
 * - DestinationRecordRaw.asEnrichedDestinationRecordAirbyteValue()
 * - toRecord() method in the s3-data-lake destination
 */
interface MapperPipelineFactory {
    fun create(stream: DestinationStream): MapperPipeline
}
