/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Change

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

interface MapperPipelineFactory {
    fun create(stream: DestinationStream): MapperPipeline
}
